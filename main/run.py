import json
import subprocess
import sys
import time
import xml.etree.ElementTree as xmlTree

from main.utils import intInput

print('Initializing..')

subprocess.call("adb root", shell=True)
time.sleep(3)

print('Getting packages..')

packages = subprocess.check_output("adb shell 'pm list packages -f' | sed -e 's/.*=//' | sort",
                                   shell=True).decode('UTF-8').split('\n')

for package in packages:
    if len(package) == 0:
        packages.remove(package)
    else:
        check_pref_file_str = "adb shell 'ls /data/data/" + package + "/shared_prefs'"
        check_pref_file = subprocess.check_output(check_pref_file_str, shell=True).decode('UTF-8')
        if 'No such file or directory' in check_pref_file:
            packages.remove(package)

for i, package in enumerate(packages):
    pass
    print(str(i) + ') ' + package)

package_index = intInput('Please select app package:')

if package_index < 0 or package_index > len(packages) - 1:
    sys.exit(0)

package = packages[package_index]
print(package)

pref_files_str = "adb shell 'ls /data/data/" + package + "/shared_prefs'"
pref_files = subprocess.check_output(pref_files_str, shell=True).decode('UTF-8').split('\n')

for pref_file in pref_files:
    if len(pref_file) == 0:
        pref_files.remove(pref_file)

while True:
    for i, pref_file in enumerate(pref_files):
        print(str(i) + ') ' + pref_file)

    print('-1) Exit')
    pref_file_index = intInput('Please select pref file:')

    if pref_file_index == -1:
        break

    if pref_file_index < 0 or pref_file_index > len(pref_files) - 1:
        print('Please enter a valid index!')
        continue

    pref_file = pref_files[pref_file_index]

    pref_file_data_str = "adb shell 'cat /data/data/" + package + "/shared_prefs/" + pref_file + "'"
    pref_file_data = subprocess.check_output(pref_file_data_str, shell=True).decode('UTF-8')

    root = xmlTree.fromstring(pref_file_data)

    while True:
        for i, child in enumerate(root):
            if child.tag == 'string':
                print(str(i) + ') ', child.tag, child.attrib['name'], child.text)
            else:
                print(str(i) + ') ', child.tag, child.attrib['name'], child.attrib['value'])

        print('-1) Back to previous page')
        pref_index = intInput('Select preference to edit:')

        if pref_index == -1:
            break

        if pref_index < 0 or pref_index > len(root) - 1:
            print('Please enter a valid index!')
            continue

        pref = root[pref_index]

        pref_new_value = input('Enter new value')
        root[pref_index].attrib['value'] = pref_new_value

        pref_update_str_content = '<?xml version="1.0" encoding="utf-8" standalone="yes" ?>\n' + xmlTree.tostring(root) \
            .decode('UTF-8')

        pref_update_str = "adb shell echo '" + json.dumps(pref_update_str_content) + " > /data/data/" \
                          + package + "/shared_prefs/" + pref_file + "'"
        pref_update = subprocess.check_output(pref_update_str, shell=True).decode('UTF-8')
        print('Preference updated!')
