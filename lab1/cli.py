#!/usr/bin/env python3

import subprocess
import json
import os
import re


def run_docker_ps():
    subprocess.run(['sudo', 'docker', 'ps'])


def run_ping(args, descr):
    if len(args) != 1:
        raise Exception(f'Invalid number of arguments to ping: {len(args)}')
    subprocess.run(['sudo', 'docker', 'exec', '-it', descr['container'], 'sh', '-c', f'ping {args[0]} -c 2'])


def run_traceroute(args, descr):
    if len(args) != 1:
        raise Exception(f'Invalid number of arguments to traceroute: {len(args)}')
    subprocess.run(['sudo', 'docker', 'exec', '-it', descr['container'], 'sh', '-c', f'traceroute {args[0]}'])


def run_sh_run(descr):
    result = subprocess.run(
        ['sudo', 'docker', 'exec', '-it', descr['container'], 'vtysh', '-c', 'sh run'],
        stdout=subprocess.PIPE)
    
    out_blocks = result.stdout.decode('utf8').split('!')
    if len(out_blocks) < 5:
        print(''.join(out_blocks))
    else:
        print(''.join(out_blocks[2:-1]))


def run_sh_ip_route(descr):
    result = subprocess.run(
        ['sudo', 'docker', 'exec', '-it', descr['container'], 'vtysh', '-c', 'sh ip route'],
        stdout=subprocess.PIPE)
    
    out_lines = result.stdout.decode('utf8').splitlines()
    for line in out_lines:
        if re.match(r'[A-Z]>\*', line):
            print(line)


def run_sh_int_brief(descr):
    subprocess.run(['sudo', 'docker', 'exec', '-it', descr['container'], 'vtysh', '-c', 'sh int brief'])


def run_at_cmd(args):
    
    global nodes_def
    if len(args) < 2:
        raise Exception(f'Invalid number of arguments to `at` command: {len(args)}')
    
    node_name = args[0]
    if node_name not in nodes_def.keys():
        raise Exception(f'Unknown node name: `{node_name}`')
    descr = nodes_def[node_name]

    if args[1] == 'sh':
        cmd = ' '.join(args[1:])
        if cmd == 'sh run':
            run_sh_run(descr)
            return
        if cmd == 'sh ip route':
            run_sh_ip_route(descr)
            return
        if cmd == 'sh int brief':
            run_sh_int_brief(descr)
            return

    if args[1] == 'ping':
        run_ping(args[2:], descr)
        return

    if args[1] == 'traceroute':
        run_traceroute(args[2:], descr)
        return

    raise Exception('Unknow comand syntax. Please try again.')


def run_help(args):
    if len(args) != 0:
        raise Exception('Run help commnad with no arguments')
    
    global nodes_def
    print(f'''
    Available hostnames:
    {', '.join(nodes_def.keys())}

    Available commands:
    - docker ps
    - at [hostname] sh run
    - at [hostname] sh ip route
    - at [hostname] sh int brief
    - at [hostname] ping x.x.x.x
    - at [hostname] traceroute x.x.x.x
    - help
    - exit
    ''')


def main():

    # Load nodes definition
    global nodes_def
    nodes_def = {}
    try:

        f_nodes = open('nodes_config.json')
        nodes_def = json.load(f_nodes)
        f_nodes.close()

    except Exception as e:

        print('Failed to load nodes definition! Please, make sure nodes_config.json and routing_config.json in the script directory.')
        print(e)
        exit(1)


    while True:
        cmd_line = input('> ')
        args = re.split(r'\s', cmd_line)
        args = [arg for arg in args if arg != '' ]

        try:
            if len(args) == 0:
                continue
            print('')

            if args[0] == 'at':
                run_at_cmd(args[1:])
            
            if args[0] == 'docker':
                if len(args) == 2 and args[1] == 'ps':
                    run_docker_ps()
                else:
                    raise Exception('unsupported docker command')

            if args[0] == 'help':
                run_help(args[1:])

            if args[0] == 'exit':
                if len(args) != 1:
                    raise Exception('exit command has no arguments')
                else:
                    exit(0)

            print('')

        except Exception as e:

            print(f'Command failed: {e}')

    


if __name__ == '__main__': main()

