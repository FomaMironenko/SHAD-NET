#!/usr/bin/env python3

import json
import os


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
def build_ip_init_cmd(interfaces):

    cmd_lines = []
    for name, addr in interfaces.items():
        cmd_lines.append(f'interface {name}')
        cmd_lines.append(f'ip address {addr}')
        cmd_lines.append('exit')
        cmd_lines.append('!')
    
    return cmd_lines


# build conf command from rouring_config.json
def build_routing_cmd(rules, nodes_def):

    cmd_lines = []
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

    cmd_lines.append('!')
    return cmd_lines



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

    # generate conf files
    try:

        for name, description in nodes_def.items():
            routing_rules = routings[name]
            print(f'Generating config for {name} ...')

            f_lines = [
                'frr version 8.4_git',
                'frr defaults traditional',
                f'hostname {name}',
                'no ipv6 forwarding',
                # 'service integrated-vtysh-config',
            ]

            f_lines.append('!')
            f_lines += build_routing_cmd(routing_rules, nodes_def)
            f_lines += build_ip_init_cmd(description['interfaces'])

            f_body = '\n'.join(f_lines)
            f_path = os.path.join(name, 'frr.conf')
            if not os.path.exists(name):
                os.mkdir
            with open(f_path, 'w') as f:
                f.write(f_body)
            
            print('Done\n')

    except Exception as e:

        print('Failed to generate conf files!')
        print(e)
    


if __name__ == '__main__': main()

