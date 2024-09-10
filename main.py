#! /usr/bin/env python3
import re
import subprocess
import sys

# 1. command to get the input source,
# 2. indice for ids or variables to extract,
# 3. mapping of aliases
COMMANDS = {
    # TODO make extra arguement for a preview command and also a description
    # TODO add a long name and short name alias

    # apt
    "a": ( "apt list | sed 's_/_ _'", {'{}': 0, '{install_status}': 1, '{description}': slice(2, None) },
        {
            "i": "sudo apt install",
            "install": "sudo apt install",
            "r": "sudo remove install",
            "remove": "sudo remove install"
        },
        "Manage apt packages"),
    # docker
    # --preview="docker inspect --format='{{json .NetworkSettings.Networks}} {{json .Mounts}} {{json .Ports}}' {1} | jq ."
    "d": ( "docker ps -a --format='table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.RunningFor}}\t{{.Status}}' | sed 1d | sort -k2", {'{}': 0},
        {
            "logs": "docker logs -f --tail 100 {}",
            "sh": "docker exec -it {} sh",
            "exec": "docker exec -it {}",
            "start": "docker start",
            "stop": "docker stop",
            "inspect": "docker inspect",
            "restart": "docker restart",
            "rm": "docker rm",
            "rmf": "docker rm -f "
        },
        "Manage docker conatiners"),
    "ds": (
        "docker service ls --format 'table {{.ID}}\t{{.Name}}\t{{.Mode}}\t{{.Replicas}}\t{{.Image}}\t{{.Ports}}' | sed 1d", 
        {'{}': 1},
        {
            "su": "docker service scale {}=1",
            "sd": "docker service scale {}=0",
            "suq": "docker service scale -d {}=1",
            "sdq": "docker service scale -d {}=0",
            "scale-up": "docker service scale {}=+1",
            "scale-down": "docker service scale {}=-1",
            "scale": "docker service scale {}={}",
            "rm": "docker service rm {}",
            "inspect": "docker service inspect {}",
            "logs": "docker service logs {}"
        },
        "Manage Docker services"
    ),
    "di": ( "docker image ls | sed 1d", {'{}': 2},
        {
            "rm": "docker image rm",
            "rmf": "docker image rm -f"
        },
        "Manage docker images"),
    "dv": ( "docker volume ls | sed 1d", {'{}': 1, '{driver}': 0},
        {
            "rm": "docker volume rm",
            "rmf": "docker volume rm -f",
            "inspect": "docker volume inspect {}"
        },
        "Manage docker volumes"),
    "dvv": ( "docker system df -v | sed -n '/VOLUME NAME/,/^$/ { p }'", {'{}': 0, '{link}': 1, '{size}': 2},
        {
            "rm": "docker volume rm",
            "rmf": "docker volume rm -f",
            "inspect": "docker volume inspect {}"
        },
        "Manage docker volumes"),
    "dn": ( "docker network ls | sed 1d", {'{}': 0, '{name}': 1, '{driver}': 2, '{scope}': 3},
        {
            "rm": "docker network rm",
            "rmf": "docker network rm -f",
            "inspect": "docker network inspect {}"
        },
        "Manage docker networks"),
    # git
    "gb": ( "git branch -a | sed 's/[\* ]*//'", {'{}': 0},
        {
            "c": "git checkout {}",
            "co": "git checkout {}",
            "track": "git checkout --track {}",
            "lg": "git lg {}",
            "diff": "git diff {}"
        },
        "Manage git branches"),
    "k": ( "kubectl get --all-namespaces pods",
        {'{}':1, '{pod}': 1, '{namespace}': 0, '{n}': 0},
        {
            "logs": "kubectl logs -n \"{namespace}\" --tail 100 -f \"{}\"",
            "logs0": "kubectl logs -n \"{namespace}\" --tail 0 -f \"{}\"",
            "exec": "kubectl -n \"{namespace}\" exec -it \"{}\" -- ",
            "k": "echo kubectl -n \"{namespace}\""
        },
        "Manage kubernetes pods"),
    # make
    "m": ( "cat Makefile | awk -F':' '/^[a-zA-Z0-9][^\$$#\/\\t=]*:([^=]|$$)/ {split($1,A,/ /);for(i in A)print A[i]}' | sort", {'{}':0},
        {
            "m": "make"
        },
        "Run make commands"),
    # ps
    "p": ( "ps -ef", {'{}': 1, '{user}': 0, '{pid}': 1, '{ppid}': 2, '{cmd}': slice(7, None)},
        {
            "k" : "kill",
            "k9": "kill -9"
        },
        "Manage processes"),
    # System V init scripts - services
    "s": ( "sudo service --status-all", {'{}': 3, '{status}': 1},
        {
            "restart": "sudo service {} restart",
            "status": "sudo service {} status",
            "start": "sudo service {} start",
            "stop": "sudo service {} stop"
        },
        "Manage services"),
     # disk usage
    "du": (
        "du -h --max-depth=1", 
        {'{}': 0},
        {
            "a": "du -ah",
            "s": "du -sh"
        },
        "Check disk usage"
    ),
    # find
    "f": (
        "find . -type f", 
        {'{}': 0},
        {
            "name": "find . -name \"{}\"",
            "size": "find . -size {}",
            "type": "find . -type {}"
        },
        "Find files and directories"
    ),
    # grep
    "g": (
        "grep -r '' .", 
        {'{}': 0},
        {
            "i": "grep -ri \"{}\" .",
            "v": "grep -rv \"{}\" .",
            "l": "grep -rl \"{}\" ."
        },
        "Search text using grep"
    ),
    # tar
    "t": (
        "tar -cvf archive.tar", 
        {'{}': 0},
        {
            "x": "tar -xvf {}",
            "z": "tar -czvf {}.tar.gz {}",
            "j": "tar -cjvf {}.tar.bz2 {}"
        },
        "Create and extract tar archives"
    ),
    # system information
    "sys": (
        "uname -a", 
        {'{}': 0},
        {
            "i": "uname -i",
            "n": "uname -n",
            "r": "uname -r",
            "v": "uname -v"
        },
        "Get system information"
    ),
    # network information
    "net": (
        "ifconfig", 
        {'{}': 0},
        {
            "a": "ifconfig -a",
            "s": "ifconfig {}"
        },
        "Get network information"
    ),
    # memory usage
    "mem": (
        "free -h", 
        {'{}': 0},
        {
            "t": "free -t",
            "m": "free -m",
            "g": "free -g"
        },
        "Check memory usage"
    ),
    # disk space
    "df": (
        "df -h", 
        {'{}': 0},
        {
            "i": "df -i",
            "T": "df -T"
        },
        "Check disk space"
    ),
    # user management
    "user": (
        "cat /etc/passwd", 
        {'{}': 0},
        {
            "a": "sudo adduser {}",
            "d": "sudo deluser {}",
            "m": "sudo usermod {}"
        },
        "Manage users"
    ),
    # group management
    "group": (
        "cat /etc/group", 
        {'{}': 0},
        {
            "a": "sudo addgroup {}",
            "d": "sudo delgroup {}",
            "m": "sudo groupmod {}"
        },
        "Manage groups"
    ),
}

def remove_empty(arr):
    return [ x for x in arr if x != "" ]

def ensureString(x):
    # sometimes if we use the slice() function instead of an integer
    # we receive a list of string rather than a string.
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return " ".join(x)
    raise Exception('Only string or list of strings are supported')

def usage(command=None):
    if command and command in COMMANDS:
        # get command description
        command_description = COMMANDS[command][3] if len(COMMANDS[command]) > 3 else "No description available"
        aliases = COMMANDS[command][2]
        alias_descriptions = "\n    ".join([f"{alias} - {cmd}" for alias, cmd in aliases.items()])
        return f"""
Usage:
ducttape {command} <alias>

Available aliases for '{command}' 
Description: {command_description}:
    {alias_descriptions}

Ex:
ducttape {command} {list(aliases.keys())[0]}

        """
    else:
        commands = [(cmd, COMMANDS[cmd][3] if len(COMMANDS[cmd]) > 3 else "No description available") for cmd in COMMANDS]
        return """
Usage:
ducttape <command>
commands are:
    {}
    """.format("\n    ".join(["{} - {}".format(cmd, desc) for cmd, desc in commands]))

def main():
    # find source (first argument means the source)
    try:
        source = sys.argv[1]
        source_command = COMMANDS[source][0]
    except:
        print(usage(), file=sys.stderr)
        sys.exit(1)

    # second argument is the alias
    # check if we only have a command, then print usage
    if len(sys.argv) < 3:
        print(usage(source), file=sys.stderr)
        sys.exit(0)

    # TODO: make it more dynamic so the system command list will come from COMMANDS dict
    system_commands = ["du", "f", "g", "t", "sys", "net", "mem", "df", "user", "group"]
    if source in system_commands:
        try:
            result = subprocess.run(source_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout.decode())
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            print(e.stderr.decode(), file=sys.stderr)
            sys.exit(1)

    # filter through fzf
    # TODO make the DUCTTAPE_FZF_OPTIONS env variable
    result = subprocess.run('{} | fzf -m --height 40% --no-sort'.format(source_command), shell=True, stdout=subprocess.PIPE)

    # extract ids
    lines=result.stdout.decode().strip().split('\n')
    r = re.compile('\s+')

    #check against command aliases (only first argument for the command)
    cmd = ""

    # TODO support multiline without a {}, eg multiple section with `echo`
    #      would pass all arguments on one line
    for line in lines:
        index = COMMANDS[source][1]['{}']
        variables = remove_empty(r.split(line))
        # the " ".join is to support the splice() operation
        identifier = ensureString(variables[index])

        alias = "echo"
        if len(sys.argv) > 2:
            alias = sys.argv[2]
        aliases = COMMANDS[source][2]

        # get the cmd
        cmd = aliases.get(alias, alias)
        rest = " ".join(sys.argv[3:])

        # handling when its not an alias we take in all the rest of the args
        if alias not in aliases:
            cmd = "{} {}".format(cmd, rest)

        # make the replacement of {}, if absent then append at the end
        if "{}" not in cmd:
            cmd = "{} {}".format(cmd, identifier)

        # expand other variables
        extractions = COMMANDS[source][1]
        for key in extractions:
            if key == "{}":
                cmd = cmd.replace("{}", identifier)
                continue

            index = extractions[key]
            cmd = cmd.replace(key, ensureString(variables[index]))

        # if we had an alias than we happend the rest after the {}
        # eg. this supports alias exec to do `docker exec {} <rest like bash>`
        if alias in aliases:
            cmd = "{} {}".format(cmd, rest)

        # TODO make a debug command line flag
        #print(cmd, file=sys.stderr)

        try:
            subprocess.run(cmd, shell=True)
        except KeyboardInterrupt:
            print("^C", file=sys.stderr)


if __name__ == "__main__":
    main()
