import re
import subprocess
import sys

# 1. command to get the input source,
# 2. indice for ids or variables to extract,
# 3. mapping of aliases
COMMANDS = {
    # docker
    "d": ( "docker ps -a | sed 1d", {'{}': 0},
        {
            "logs": "docker logs -f --tail 100 {}",
            "sh": "docker exec -it {} sh",
            "exec": "docker exec -it {}",
            "start": "docker start",
            "stop": "docker stop",
            "inspect": "docker inspect"
        }),
    # git
    "g": ( "git branch -a | sed 's/[\* ]*//'", {'{}': 0},
        {
            "c": "git checkout {}",
            "co": "git checkout {}",
            "track": "git checkout {}",
            "lg": "git lg {}",
            "diff": "git diff {}"
        }),
    # ps
    "p": ( "ps -ef", {'{}': 1, '{user}': 0, '{pid}': 1, '{ppid}': 2, '{cmd}': 7}, # TODO support an array of range cmd
        {
            "k" : "kill",
            "k9": "kill -9"
        }),
    # make
    "m": ( "cat Makefile | awk -F':' '/^[a-zA-Z0-9][^\$$#\/\\t=]*:([^=]|$$)/ {split($1,A,/ /);for(i in A)print A[i]}' | sort", {'{}':0},
        {
            "m": "make"
        }),
    "k": ( "kubectl get --all-namespaces pods",
        {'{}':1, '{pod}': 1, '{namespace}': 0, '{n}': 0},
        {
            "logs": "kubectl logs -n \"{namespace}\" --tail 100 -f \"{}\"",
            "logs0": "kubectl logs -n \"{namespace}\" --tail 0 -f \"{}\"",
            "exec": "kubectl -n \"{namespace}\" exec -it \"{}\" -- ",
            "k": "echo kubectl -n \"{namespace}\""
        })
}

def remove_empty(arr):
    return [ x for x in arr if x != "" ]

def main():
    # find source (first argument means the source)
    source = sys.argv[1]
    source_command = COMMANDS[source][0] # TODO make error message if source is not in COMMANDS

    # filter through fzf
    result = subprocess.run('{} | fzf -m --height 40%'.format(source_command), shell=True, stdout=subprocess.PIPE)

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
        identifier = variables[index]

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
            cmd = cmd.replace(key, variables[index])

        # if we had an alias than we happend the rest after the {}
        # eg. this supports alias exec to do `docker exec {} <rest like bash>`
        if alias in aliases:
            cmd = "{} {}".format(cmd, rest)

        # TODO make a debug command line flag
        #print(cmd, file=sys.stderr)

        # TODO catch KeyboardInterrupt
        subprocess.run(cmd, shell=True)


if __name__ == "__main__":
    main()
