#!/usr/bin/env python3

import subprocess
import json


# sets the last part of ipv4 to zero
def mask_address(addr):

    prts = addr.split('/')
    assert len(prts) == 2

    ipv4 = prts[0].split('.')
    assert len(ipv4) == 4

    ipv4[3] = '0'
    return '.'.join(ipv4) + '/24'


# extract pure ipv4
def remove_suffix(addr):

    prts = addr.split('/')
    assert len(prts) == 2

    return prts[0]


# build conf command from nodes_config.json
def build_node_init_cmd(interfaces):

    cmd_lines = []
    cmd_lines.append('conf')

    for name, addr in interfaces.items():
        cmd_lines.append(f'int {name}')
        cmd_lines.append(f'ip address {addr}')
    
    cmd_lines.append('do wr')
    return '\n'.join(cmd_lines) + '\n'


# build conf command from rouring_config.json
def build_routing_cmd(rules, nodes_def):

    cmd_lines = []
    cmd_lines.append('conf')

    for path in rules:
        hop_name = path['hop'][0]
        hop_int  = path['hop'][1]

        hop_addr = nodes_def[hop_name]['interfaces'][hop_int]
        hop_addr = remove_suffix(hop_addr)

        for dst in path['dst']:
            dct_name = dst[0]
            dst_int  = dst[1]
            crop_dst = dst[2]

            dst_addr = nodes_def[dct_name]['interfaces'][dst_int]
            if crop_dst:
                dst_addr = mask_address(dst_addr)

            cmd_lines.append(f'ip route {dst_addr} {hop_addr} {path["int"]}')

    cmd_lines.append('do wr')
    return '\n'.join(cmd_lines) + '\n'



def main():

    nodes_def = {}
    routings = {}

    # Load network configuration
    try:

        f_nodes = open('nodes_config.json')
        nodes_def = json.load(f_nodes)
        f_nodes.close()

        f_routings = open('routing_config.json')
        routings = json.load(f_routings)
        f_routings.close()

    except Exception as e:

        print('Failed to load network config! Please, make sure nodes_config.json and routing_config.json in the script directory.')
        print(e)
        exit(1)

    # Init static IP address
    try:

        for name, description in nodes_def.items():
            print(f'Init {name} ...')
            init_cmd = build_node_init_cmd(description['interfaces'])
            # subprocess.run(['sudo', 'docker', 'exec', '-it', description['container'], 'vtysh', '-c', init_cmd])
            print('Done\n')

    except subprocess.CalledProcessError as e:

        print('Failed to init static IPs!')

    # Init static routings
    try:

        for name, rules in routings.items():
            print(f'Init routing for {name} ...')
            container = nodes_def[name]['container']
            routing_cmd = build_routing_cmd(rules, nodes_def)
            # subprocess.run(['sudo', 'docker', 'exec', '-it', container, 'vtysh', '-c', routing_cmd])
            print('Done\n')

    except subprocess.CalledProcessError as e:

        print('Failed to init static routings!')



if __name__ == '__main__': main()


