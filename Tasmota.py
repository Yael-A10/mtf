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

impFlash = False
while impFlash != 'y' and impFlash != 'n':
    impFlash = input('Do you want to flash [y/n]: ').lower().strip()
if impFlash == 'y':
    available_versions = []
    for x in versions:
        if os.path.exists(path + x):
            available_versions.append(x)
    print(available_versions)
    if available_versions:
        while True:
            impUseFile = input('Do you want to use existing file(s); '+'; '.join(available_versions)+' [y/n]: ')
            if impUseFile == 'y' or impUseFile == 'n':
                break
        if impUseFile == 'y':
            if len(available_versions) > 1:
                while True:
                    for x in available_versions:
                        print(x + ' [' + str(available_versions.index(x)) + ']')
                    impWhichFile = input('Which file would you like to use: ')
                    if impWhichFile.isnumeric() and int(impWhichFile) >= 0 and int(impWhichFile) < len(available_versions):
                        break
                download(available_versions[int(impWhichFile)])
                flash(available_versions[int(impWhichFile)])
            else:
                download(available_versions[0])
                flash(available_versions[0])
    else:
        while True:
            for x in versions:
                print(x + ' [' + str(versions.index(x)) + ']')
            impWhichVersion = input('Which version would you like to use: ')
            if impWhichVersion.isnumeric() and int(impWhichVersion) >= 0 and int(impWhichVersion) < len(versions):
                break
        download(versions[int(impWhichVersion)])
        flash(versions[int(impWhichVersion)])
else:
    print('i dont want to flash')