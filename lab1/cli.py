#!/usr/bin/env python3

import subprocess
import json
import os
import re


def run_sh_run(descr):
    subprocess.run(['sudo', 'docker', 'exec', '-it', descr['container'], 'vtysh', '-c', 'sh run'])
    print('\n')

def run_sh_ip_route(descr):
    subprocess.run(['sudo', 'docker', 'exec', '-it', descr['container'], 'vtysh', '-c', 'sh ip route'])
    print('\n')

def run_sh_int_brief(descr):
    subprocess.run(['sudo', 'docker', 'exec', '-it', descr['container'], 'vtysh', '-c', 'sh int brief'])
    print('\n')



def run_at_cmd(args):
    
    global nodes_def
    if len(args) <= 1:
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

    raise Exception('Unknow comand syntax. Please try again.')


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

        try:
            if len(args) == 0:
                continue
            if args[0] == 'at':
                run_at_cmd(args[1:])
            if args[0] == 'docker':
                raise Exception('docker not supported')

        except Exception as e:

            print(f'Command failed: {e}')

    


if __name__ == '__main__': main()

