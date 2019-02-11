import json
import subprocess
import sys
import time
import xml.etree.ElementTree as xmlTree


def intInput(desc):
    while True:
        try:
            data = int(input(desc))
            break
        except Exception as e:
            print(e)
    return data


print('Initializing ADB as a root...')

# Start adb as root
subprocess.call("adb root", shell=True)
time.sleep(3)

# Get all of the installed app packages
packages = subprocess.check_output("adb shell 'pm list packages -f' | sed -e 's/.*=//' | sort",
                                   shell=True).decode('UTF-8').split('\n')
# Remove empty package
packages.pop()

# Iterate packages
for i, package in enumerate(packages):

    # Show progressbar
    sys.stdout.write('\r')
    sys.stdout.write("Getting app packages [%-30s] %d%%" % ('=' * int((i+1) / len(packages) * 30), int((i+1) / len(packages) * 100)))
    sys.stdout.flush()

    # Remove packages that doesn't have any preference files
    check_pref_file_str = "adb shell 'ls /data/data/" + package + "/shared_prefs'"
    check_pref_file = subprocess.check_output(check_pref_file_str, shell=True).decode('UTF-8')
    if 'No such file or directory' in check_pref_file:
        packages.remove(package)

# New line
print("")

for i, package in enumerate(packages):
    print(str(i) + ') ' + package)

package_index = intInput('\nSelect app package: ')

if package_index < 0 or package_index > len(packages) - 1:
    sys.exit(0)

package = packages[package_index]
print(package)

# Get preference files of selected package
pref_files_str = "adb shell 'ls /data/data/" + package + "/shared_prefs'"
pref_files = subprocess.check_output(pref_files_str, shell=True).decode('UTF-8').split('\n')

# Remove empty file name
pref_files.pop()

while True:
    for i, pref_file in enumerate(pref_files):
        print(str(i) + ') ' + pref_file)

    print('-1) Exit')
    pref_file_index = intInput('\nSelect preference file: ')

    if pref_file_index == -1:
        break

    if pref_file_index < 0 or pref_file_index > len(pref_files) - 1:
        print('Please enter a valid index!')
        continue

    pref_file = pref_files[pref_file_index]

    # Get preference file content
    pref_file_data_str = "adb shell 'cat /data/data/" + package + "/shared_prefs/" + pref_file + "'"
    pref_file_data = subprocess.check_output(pref_file_data_str, shell=True).decode('UTF-8')

    # Decode XML content
    root = xmlTree.fromstring(pref_file_data)

    while True:
        for i, child in enumerate(root):
            if child.tag == 'string':
                print(str(i) + ') ', child.tag, child.attrib['name'], child.text)
            else:
                print(str(i) + ') ', child.tag, child.attrib['name'], child.attrib['value'])

        print('-1) Back to previous page')
        pref_index = intInput('\nSelect preference to edit: ')

        if pref_index == -1:
            break

        if pref_index < 0 or pref_index > len(root) - 1:
            print('Please enter a valid index!')
            continue

        pref = root[pref_index]

        pref_new_value = input('\nEnter new value: ')

        if pref.tag == 'string':
            root[pref_index].text = pref_new_value
        else:
            root[pref_index].attrib['value'] = pref_new_value

        # Update preference file content with decoded xmlTree
        pref_update_str_content = '<?xml version="1.0" encoding="utf-8" standalone="yes" ?>\n' + xmlTree.tostring(root) \
            .decode('UTF-8')

        pref_update_str = "adb shell echo '" + json.dumps(pref_update_str_content) + " > /data/data/" \
                          + package + "/shared_prefs/" + pref_file + "'"
        pref_update = subprocess.check_output(pref_update_str, shell=True).decode('UTF-8')
        print('Preference updated!')
