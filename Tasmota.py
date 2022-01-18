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
    esptool.main(['write_flash', '-fs', '1MB', '-fm', 'dout', '0x0', path + file])

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
            while not data.isnumeric() or int(data) in availableIndex:
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
    if os.path.exists(path + 'config.txt') and question('Is config.txt your config file?') == 'y':
        file = open(path + 'config.txt', 'r')
    else:
        file = open(path + input('Please enter your file name: '))
    return file

def findPort():
    #code from esptool function get_default_connected_device
    for each_port in reversed(esptool.get_port_list()):
        print("Serial port %s" % each_port)
        try:
            esptool.ESPLoader.detect_chip(each_port, 115200, 'default_reset', False, 3)
            port = each_port
            break
        except (esptool.FatalError, OSError) as err:
            print("%s failed to connect: %s" % (each_port, err))
            port = None
    return port

def configure(file):
    command = 'Backlog '
    for x in file:
        command += x.strip('\n') + '; '
    command = command[:-2]
    print(command)
    port = findPort()
    if port != None:
        ser = serial.Serial(port, 115200, timeout=5)
        #ser.write(b'telemetry 15')
        print(ser.readline())
        ser.close()

if question('Do you want to flash') == 'y':
    flash(findFile())
if question('Do you want to configure') == 'y':
    configure(findConfigFile())