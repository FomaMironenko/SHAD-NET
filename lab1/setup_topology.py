#!/usr/bin/env python3

import subprocess


routers = {
    'router1': {
        'container': 'clab-frrlab1_1-router1',
        'interfaces': {
            'lo': '10.10.10.1/32',
            'eth1': '192.168.1.1/24',
            'eth2': '192.168.2.1/24',
            'eth3': '192.168.11.1/24',
        }
    },
    'router2': {
        'container': 'clab-frrlab1_1-router2',
        'interfaces': {
            'lo': '10.10.10.2/32',
            'eth1': '192.168.1.2/24',
            'eth2': '192.168.3.2/24',
            'eth3': '192.168.22.2/24',
        }
    },
    'router3': {
        'container': 'clab-frrlab1_1-router3',
        'interfaces': {
            'lo': '10.10.10.3/32',
            'eth1': '192.168.2.3/24',
            'eth2': '192.168.3.3/24',
            'eth3': '192.168.33.3/24',
        }
    },
}


def build_router_cmd(interfaces):
    cmd_lines = []
    cmd_lines.append('conf')
    for name, addr in interfaces.items():
        cmd_lines.append(f'int {name}')
        cmd_lines.append(f'ip address {addr}')
    cmd_lines.append('do wr')
    return '\n'.join(cmd_lines) + '\n'



def main():

    try:

        for name, description in routers.items():
            print(f'Init {name} ...')
            router_cmd = build_router_cmd(description['interfaces'])
            subprocess.run(['sudo', 'docker', 'exec', '-it', description['container'], 'vtysh', '-c', router_cmd])
            print('Done\n')

    except subprocess.CalledProcessError as e:

        print('Failed to init router!')



if __name__ == '__main__': main()


