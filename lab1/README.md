# 1. Генератор

Генератор принимает на вход два файла: `nodes_config.json` -- с описанием статических ip адресов на узлах сети; и `routing_config.json` -- с описанием статической маршрктизации на узлах. Исходя из заданной в них топологии и адресов он генерирует файлы конфигурации `frr.conf` в директориях соответствующих узлов (маршрутизаторов и PC).

## Запуск генератора

Для запуска генерации необходимо перейти в директорию `lab1`, убедиться что в ней находятся `nodes_config.json` и `routing_config.json` и запустить скрипт `generate_conf.py`. Генератор считает статическую конфигурацию из `.json` и сохранит полученные `frr.conf` файлы в поддиректориях `PC1`, `PC2`, `PC3`, `router1`, `router2`, `router3`. 

Рекомендуемая версия `python3`: `3.9`. Поддерживаемая ОС: `Linux`.

## Запуск containerlab

После того как генератор сохранил файлы конфигурации, их нужно привязать к файлам `etc/frr/frr.conf` в каждом из контейнеров. Для этого следует добавить соотвествующую запись в секцию `binds` каждого из узлов в `frrlab1_1.yml`. Например: для `router3`:
```yaml
binds:
        - router3/daemons:/etc/frr/daemons
        - router3/frr.conf:/etc/frr/frr.conf
```
и для `PC1`:
```yaml
binds:
        - PC1/daemons:/etc/frr/daemons
        - PC1/frr.conf:/etc/frr/frr.conf
```


# 2. Запуск команд (парсер)

После того как сгенерированная конфигурация была запущена в `containterlab`, можно воспользоваться скриптом `cli.py`, который в цикле обрабатывает интересующие команды. Для исполнения каждой из них скрипт подключается к соотвествтующему контейнеру, исполняет запрошенную команду и выводит результат обратно пользователю: при необходимости преобразовав его. **Большинство команд запускают `sudo docker exec` и требуют ввода пароля администратора**.

## Поддерживаемые команды

### 1. help

Краткая справка по всем командам. Пример вывода:
```
Available hostnames:
router1, router2, router3, PC1, PC2, PC3

Available commands:
- help
- exit
- docker ps
- at [hostname] sh run
- at [hostname] sh ip route
- at [hostname] sh int brief
- at [hostname] ping x.x.x.x
- at [hostname] traceroute x.x.x.x
```

### 2. exit

Завершение работы и выход из цикла обработки команд.

### 3. docker ps

Показать имеющиеся контейнеры *без преобразования вывода*. Пример вывода:
```
CONTAINER ID   IMAGE                  COMMAND                  CREATED       STATUS       PORTS     NAMES
9fb403e92cc1   frrouting/frr:latest   "/sbin/tini -- /usr/…"   2 hours ago   Up 2 hours             clab-frrlab1_1-PC2
ec2396f2fccb   frrouting/frr:latest   "/sbin/tini -- /usr/…"   2 hours ago   Up 2 hours             clab-frrlab1_1-PC1
2f4db842a9f4   frrouting/frr:latest   "/sbin/tini -- /usr/…"   2 hours ago   Up 2 hours             clab-frrlab1_1-PC3
3ecf35cd02de   frrouting/frr:latest   "/sbin/tini -- /usr/…"   2 hours ago   Up 2 hours             clab-frrlab1_1-router2
c46c82dc4096   frrouting/frr:latest   "/sbin/tini -- /usr/…"   2 hours ago   Up 2 hours             clab-frrlab1_1-router3
8b07fe0e754e   frrouting/frr:latest   "/sbin/tini -- /usr/…"   2 hours ago   Up 2 hours             clab-frrlab1_1-router1
```

### 4. at [hostname] sh run
Запускает `sh run` на заданном хосте. Список имён хостов (маршрутизаторов и PC) можно увидеть в команде `help`. Примеры вывода команды:

#### `at router1 sh run`:
```
ip route 192.168.22.0/24 192.168.1.2 eth1
ip route 192.168.33.0/24 192.168.2.3 eth2
ip route 10.10.10.2/32 192.168.1.2 eth1
ip route 10.10.10.3/32 192.168.2.3 eth2

interface eth1
 ip address 192.168.1.1/24
exit

interface eth2
 ip address 192.168.2.1/24
exit

interface eth3
 ip address 192.168.11.1/24
exit

interface lo
 ip address 10.10.10.1/32
exit
```

#### `at PC2 sh run`:
```
ip route 10.10.10.0/24 192.168.22.2 eth1
ip route 192.168.11.0/24 192.168.22.2 eth1
ip route 192.168.33.0/24 192.168.22.2 eth1

interface eth1
 ip address 192.168.22.4/24
exit
```


### 5. at [hostname] sh ip route
Запускает `sh ip route` на заданном хосте. Список имён хостов (маршрутизаторов и PC) можно увидеть в команде `help`. Примеры вывода команды:

#### `at router2 sh ip route`:
```
K>* 0.0.0.0/0 [0/0] via 172.20.20.1, eth0, 02:05:40
S>* 10.10.10.1/32 [1/0] via 192.168.1.1, eth1, weight 1, 02:05:25
C>* 10.10.10.2/32 is directly connected, lo, 02:05:40
S>* 10.10.10.3/32 [1/0] via 192.168.3.3, eth2, weight 1, 02:05:25
C>* 172.20.20.0/24 is directly connected, eth0, 02:05:40
C>* 192.168.1.0/24 is directly connected, eth1, 02:05:31
C>* 192.168.3.0/24 is directly connected, eth2, 02:05:39
S>* 192.168.11.0/24 [1/0] via 192.168.1.1, eth1, weight 1, 02:05:25
C>* 192.168.22.0/24 is directly connected, eth3, 02:05:21
S>* 192.168.33.0/24 [1/0] via 192.168.3.3, eth2, weight 1, 02:05:25
```

#### `at PC3 sh ip route`:
```
K>* 0.0.0.0/0 [0/0] via 172.20.20.1, eth0, 02:06:21
S>* 10.10.10.0/24 [1/0] via 192.168.33.3, eth1, weight 1, 02:06:06
C>* 172.20.20.0/24 is directly connected, eth0, 02:06:21
S>* 192.168.11.0/24 [1/0] via 192.168.33.3, eth1, weight 1, 02:06:06
S>* 192.168.22.0/24 [1/0] via 192.168.33.3, eth1, weight 1, 02:06:06
C>* 192.168.33.0/24 is directly connected, eth1, 02:06:20
```


### 6. at [hostname] sh int brief
Запускает `sh int brief` на заданном хосте. Список имён хостов (маршрутизаторов и PC) можно увидеть в команде `help`. Примеры вывода команды:

#### `at router3 sh int brief`:
```
Interface       Status  VRF             Addresses
---------       ------  ---             ---------
eth0            up      default         172.20.20.2/24
                                        + 2001:172:20:20::2/64
eth1            up      default         192.168.2.3/24
eth2            up      default         192.168.3.3/24
eth3            up      default         192.168.33.3/24
lo              up      default         10.10.10.3/32
```

#### `at PC1 sh int brief`:
```
Interface       Status  VRF             Addresses
---------       ------  ---             ---------
eth0            up      default         172.20.20.6/24
                                        + 2001:172:20:20::6/64
eth1            up      default         192.168.11.4/24
lo              up      default         
```


### 7. at [hostname] ping x.x.x.x
Запускает `ping x.x.x.x -с 2` на заданном хосте. Список имён хостов (маршрутизаторов и PC) можно увидеть в команде `help`. *Не преобразует вывод*. Примеры вывода команды:

#### `at router1 ping 192.168.2.3`:
```
PING 192.168.2.3 (192.168.2.3): 56 data bytes
64 bytes from 192.168.2.3: seq=0 ttl=64 time=0.056 ms
64 bytes from 192.168.2.3: seq=1 ttl=64 time=0.115 ms

--- 192.168.2.3 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.056/0.085/0.115 ms
```

#### `at PC2 ping 192.168.11.4`:
```
PING 192.168.11.4 (192.168.11.4): 56 data bytes
64 bytes from 192.168.11.4: seq=0 ttl=62 time=0.070 ms
64 bytes from 192.168.11.4: seq=1 ttl=62 time=0.130 ms

--- 192.168.11.4 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.070/0.100/0.130 ms
```

#### `at PC3 ping 10.10.10.2`:
```
PING 10.10.10.2 (10.10.10.2): 56 data bytes
64 bytes from 10.10.10.2: seq=0 ttl=63 time=0.059 ms
64 bytes from 10.10.10.2: seq=1 ttl=63 time=0.086 ms

--- 10.10.10.2 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.059/0.072/0.086 ms
```


### 8. at [hostname] traceroute x.x.x.x
Запускает `traceroute x.x.x.x` на заданном хосте. Список имён хостов (маршрутизаторов и PC) можно увидеть в команде `help`. *Не преобразует вывод*. Примеры вывода команды:

#### `at router1 traceroute 192.168.2.3`:
```
traceroute to 192.168.2.3 (192.168.2.3), 30 hops max, 46 byte packets
 1  192.168.2.3 (192.168.2.3)  0.005 ms  0.005 ms  0.003 ms
```

#### `at PC2 traceroute 192.168.11.4`:
```
traceroute to 192.168.11.4 (192.168.11.4), 30 hops max, 46 byte packets
 1  192.168.22.2 (192.168.22.2)  0.005 ms  0.005 ms  0.004 ms
 2  192.168.1.1 (192.168.1.1)  0.003 ms  0.058 ms  0.004 ms
 3  192.168.11.4 (192.168.11.4)  0.003 ms  0.006 ms  0.005 ms
```

#### `at PC3 traceroute 10.10.10.2`:
```
traceroute to 10.10.10.2 (10.10.10.2), 30 hops max, 46 byte packets
 1  192.168.33.3 (192.168.33.3)  0.006 ms  0.004 ms  0.004 ms
 2  10.10.10.2 (10.10.10.2)  0.003 ms  0.005 ms  0.003 ms
```



# 3. Разрыв логического линка между R1 и R2

1. Проверим что до разрыва линка связь между PC1 и PC2 есть:
#### `at PC1 ping 192.168.22.4`
```
PING 192.168.22.4 (192.168.22.4): 56 data bytes
64 bytes from 192.168.22.4: seq=0 ttl=62 time=0.082 ms
64 bytes from 192.168.22.4: seq=1 ttl=62 time=0.142 ms

--- 192.168.22.4 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.082/0.112/0.142 ms
```

2. Отключим интерфейс `eth1` на `router1`:
```
router1# conf
router1(config)# int eth1
router1(config-if)# shutdown
```

3. Теперь связь между PC1 и PC2 потеряна:
#### `at PC1 ping 192.168.22.4`
```
PING 192.168.22.4 (192.168.22.4): 56 data bytes

--- 192.168.22.4 ping statistics ---
2 packets transmitted, 0 packets received, 100% packet loss
```

#### `at PC2 ping 192.168.11.4`
```
PING 192.168.11.4 (192.168.11.4): 56 data bytes

--- 192.168.11.4 ping statistics ---
2 packets transmitted, 0 packets received, 100% packet loss
```

4. Данное поведение объясняется тем что в нашей конфигурации пакеты от router1 к router2 и обратно не могут проходить через router3. Действительно, посмотрим на вывод следующих двух команд:

### `at router1 sh run`
```
ip route 192.168.22.0/24 192.168.1.2 eth1 // <->
ip route 192.168.33.0/24 192.168.2.3 eth2
ip route 10.10.10.2/32 192.168.1.2 eth1
ip route 10.10.10.3/32 192.168.2.3 eth2

interface eth1
...
```

### `at router2 sh run`
```
ip route 192.168.11.0/24 192.168.1.1 eth1 // <->
ip route 192.168.33.0/24 192.168.3.3 eth2
ip route 10.10.10.1/32 192.168.1.1 eth1
ip route 10.10.10.3/32 192.168.3.3 eth2

interface eth1
...
```

Таким образом, все пакеты между router1 и router2 должны проходить через линк `router1:eth1 <-> 192.168.1.0/24 <-> router2:eth1`, который и был отключен.

