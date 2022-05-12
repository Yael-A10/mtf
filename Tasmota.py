from queue import Empty
import sys
import subprocess
installed = [r.decode().split('==')[0] for r in subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).split()]
modules = ['esptool', 'requests', 'pyserial']
for module in modules:
    if module not in installed:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])
import esptool
import requests
import os
import serial

path = os.path.dirname(os.path.abspath(__file__)) + '/'
versions = ['tasmota-sensors.bin', 'tasmota.bin', 'tasmota-lite.bin', 'tasmota-minimal.bin']

def download(file):
    url = 'http://ota.tasmota.com/tasmota/release/'+file
    r = requests.get(url, allow_redirects=True)
    open(path + file, 'wb').write(r.content)

def flash(file):
    esptool.main(['erase_flash'])
    esptool.main(['write_flash', '-fs', '1MB', '-fm', 'dout', '0x0', file])

def question(q):
    data = ''
    while data != 'y' and data !='n':
        data = input(q + ' [y/n]: ').lower().strip()
    return data

def findAvailable():
  availableVersions = []
  for x in versions:
    if os.path.exists(path + x):
      availableVersions.append(x)
  return availableVersions

def findFile():
    available = findAvailable()
    if available and question('Do you want to use existing file(s); '+'; '.join(available)) == 'y':
        if len(available) > 1:
            availableIndex = []
            for x in available:
                print(x + ' [' + str(available.index(x)) + ']')
                availableIndex.append(available.index(x))
            data = '-1'
            while not data.isnumeric() or int(data) not in availableIndex:
                data = input('Which file would you like to use: ')
            return available[int(data)]
        else:
            return available[0]
    else:
        versionIndex = []
        for x in versions:
            print(x + ' [' + str(versions.index(x)) + ']')
            versionIndex.append(versions.index(x))
        data = '-1'
        while not data.isnumeric() or int(data) not in versionIndex:
            data = input('Which version would you like to use: ')
        download(versions[int(data)])
        return versions[int(data)]

def findConfigFile():
    if os.path.exists(path + 'config.txt'):
        return open(path + 'config.txt', 'r')
    else:
        print('Please put your config file named config.txt in this folder (' + path + ')')
        exit()

def configure(file):
    command = 'Backlog '
    for x in file:
        command += x.strip('\n') + '; '
    command = command[:-2]+'\n'
    test = esptool.get_default_connected_device(esptool.get_port_list(), None, 2, 115200)
    port = test._port.port
    test._port.close()
    ser = serial.Serial(port, 115200, timeout=3)
    esptool.main(['read_mac'])
    char = 0
    while char != b'':
        char = ser.read(1)
        print(char)
    char = 0
    while char != b'':
        char = ser.read(1)
        print(char)
    ser.write(command.encode())
    char = 0
    while char != b'':
        char = ser.read(1)
        print(char)
    print('Finished configuring!')
    ser.close()

arguments = ' '.join(sys.argv[1:]).replace('--Flash', '-f').replace('--Configure', '-c').split()
options = ['-f', '-c']
results = {'-f': '', '-c': ''}
for argument in arguments:
    for option in options:
        if argument == option:
            if len(arguments) > arguments.index(argument)+1:
                if arguments[arguments.index(argument)+1] in ('y', 'n'):
                    options.pop(options.index(option))
                    results[argument] = arguments[arguments.index(argument)+1]
                elif os.path.exists(arguments[arguments.index(argument)+1]) or os.path.exists(path + arguments[arguments.index(argument)+1]):
                    options.pop(options.index(option))
                    results[argument] = 'y'
                else:
                    print('Path '+ arguments[arguments.index(argument)+1] + ' or path ' + path + arguments[arguments.index(argument)+1] + ' do not exist, please check your file name.')
                    exit()

if results['-f'] != 'n' and (results ['-f'] == 'y' or question('Do you want to flash') == 'y'):
    if len(arguments) > 0 and len(arguments) > arguments.index('-f')+1 and os.path.exists(arguments[arguments.index('-f')+1]):
        flash(arguments[arguments.index('-f')+1])
    elif len(arguments) > 0 and len(arguments) > arguments.index('-f')+1 and os.path.exists(path + arguments[arguments.index('-f')+1]):
        flash(path + arguments[arguments.index('-f')+1])
    else:
        flash(path + findFile())
if results['-c'] != 'n' and (results['-c'] == 'y' or question('Do you want to configure') == 'y'):
    if len(arguments) > 0 and len(arguments) > arguments.index('-c')+1 and os.path.exists(arguments[arguments.index('-c')+1]):
        configure(arguments[arguments.index('-c')+1])
    elif len(arguments) > 0 and len(arguments) > arguments.index('-c')+1 and os.path.exists(path + arguments[arguments.index('-c')+1]):
        configure(path + arguments[arguments.index('-c')+1])
    else:
        configure(findConfigFile())