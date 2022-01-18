import esptool
import requests
import os

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

if question('Do you want to flash') == 'y':
    flash(findFile())
else:
    print('i dont want to flash')