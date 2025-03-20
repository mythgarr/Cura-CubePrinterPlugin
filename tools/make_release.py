#####################################################################
# make_release.py
#####################################################################
#  python script to make a .curaplugin file for drag/drop
#  installation into cura as well as making the necessary zip file for
#  uploading to contribute.ultimaker.com for release in the cura marketplace
#
# Written by Tim Schoenmackers and mirdoc
#
# This source is released under the terms of the LGPLv3 or higher.
# The full text of the LGPLv3 License can be found here:
# https://github.com/mirdoc/Cura-CubePrinterPlugin/blob/master/LICENSE
#
#
# Requirements:
#  This tool calls the wkhtmltopdf tool (64 bit) to make the pdf documentation
#    Download the tool from: https://wkhtmltopdf.org/downloads.html and set
#    the WKHTMLTOPDF_DIR appropriately below
#
#  Additionally this tool requires python 3 and the grip package
#    (pip install grip)
#####################################################################
import os
import platform
import shutil
import zipfile
import json
from pathlib import Path

PLUGIN_NAME = 'CubePrinterPlugin'

with open(f'./plugins/{PLUGIN_NAME}/plugin.json') as json_file:
    plugin_json = json.load(json_file)
    json_file.close()

RELEASE_DIR = Path('./RELEASE').absolute()
RELEASE_TEMP_DIR = RELEASE_DIR / PLUGIN_NAME
RELEASE_PLUGINS_DIR = RELEASE_TEMP_DIR / 'files/plugins'
CURA_PACKAGE_FILE = RELEASE_DIR / f'{PLUGIN_NAME}-{plugin_json["version"]}.curapackage'
ULTIMAKER_ZIP = RELEASE_DIR / f'{PLUGIN_NAME}.zip'
PLUGIN_DIR = RELEASE_TEMP_DIR / 'files' / 'plugins' / PLUGIN_NAME

ALL_PLUGINS = [PLUGIN_NAME, 'CubeWriter', 'Cube3Writer', 'CubexWriter', 'CubeproWriter']

################################
## Step 1
## cleanup & make directories
################################

if(os.path.exists(RELEASE_TEMP_DIR)):
    shutil.rmtree(RELEASE_TEMP_DIR)

# delete existing files
for item in [Path('README.html'), Path('README.pdf'), CURA_PACKAGE_FILE,
             PLUGIN_DIR / f'{PLUGIN_NAME}.zip']:
    print(f'Checking {item.absolute()}')
    if item.exists():
        print(f'Deleting {item.absolute()}')
        item.unlink()

# make new dirs
RELEASE_TEMP_DIR.mkdir(parents=True, exist_ok=True)

dirs = [
    RELEASE_TEMP_DIR,
    RELEASE_TEMP_DIR / 'files',
    RELEASE_PLUGINS_DIR]
    
for item in ALL_PLUGINS:
    dirs.append(RELEASE_PLUGINS_DIR / item)

for item in dirs:
    item.mkdir(parents=True, exist_ok=True)

################################
## Step 2
## copy the cubepro printer definitions,
## materials, the platform stl file,
## and the quality files
################################
zipList = {
    'CubePro.def.json':             './resources/definitions/',
    'CubeProDuo.def.json':          './resources/definitions/',
    'CubeProTrio.def.json':         './resources/definitions/',
    'Cube.def.json':                './resources/definitions/',
    'Cube2.def.json':               './resources/definitions/',
    'Cube3.def.json':               './resources/definitions/',
    'CubeX.def.json':               './resources/definitions/',
    'CubeXDuo.def.json':            './resources/definitions/',
    'CubeXTrio.def.json':           './resources/definitions/',
    'CubePro_extruder_0.def.json':  './resources/extruders/',
    'CubePro_extruder_1.def.json':  './resources/extruders/',
    'CubePro_extruder_2.def.json':  './resources/extruders/',
    'Cube_extruder_0.def.json':     './resources/extruders/',
    'Cube2_extruder_0.def.json':     './resources/extruders/',
    'Cube3_extruder_0.def.json':    './resources/extruders/',
    'Cube3_extruder_1.def.json':    './resources/extruders/',
    'CubeX_extruder_0.def.json':    './resources/extruders/',
    'CubeX_extruder_1.def.json':    './resources/extruders/',
    'CubeX_extruder_2.def.json':    './resources/extruders/',
    'CubePro_platform.stl':         './resources/meshes/',
    'CubePro/':                     './resources/quality/',
    'CubeProDuo/':                  './resources/quality/',
    'CubeProTrio/':                 './resources/quality/',
    'CubeX/':                       './resources/quality/',
    'CubeXDuo/':                    './resources/quality/',
    'CubeXTrio/':                   './resources/quality/',
    'Cube/':                        './resources/quality/',
    'Cube2/':                       './resources/quality/',
    'Cube3/':                       './resources/quality/'
}

for file_name, file_path in zipList.items():
    if file_name.endswith('/'):
        shutil.copytree(os.path.abspath(file_path + file_name), PLUGIN_DIR / file_name)
    else:
        shutil.copy2(os.path.abspath(file_path + file_name), PLUGIN_DIR)

################################
## Step 3
## zip the files copied above
################################
internal_zip_file_name = PLUGIN_DIR / f'{PLUGIN_NAME}.zip'
z = zipfile.ZipFile(internal_zip_file_name, 'w', zipfile.ZIP_DEFLATED)
for file_name, file_path in zipList.items():
    if file_name.endswith('/'):
        for root, dirs, files in os.walk(os.path.join(PLUGIN_DIR, file_name)):
            for file in files:
                z.write(os.path.join(PLUGIN_DIR, file_name, file), os.path.join(file_name, file))
    else:
        z.write(os.path.join(PLUGIN_DIR, file_name), os.path.basename(file_name));

################################
## Step 4
## now delete the files that were copied in Step 2
################################
for file_name, file_path in zipList.items():
    path = PLUGIN_DIR / file_name
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()

if platform.system() == "Windows":    
    ################################
    ## Step 5
    ## Create the README.pdf file from
    ## the markdown
    ################################
    WKHTMLTOPDF_DIR = Path("c:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
    if not WKHTMLTOPDF_DIR.exists():
        print("wkhtmltopdf not found - skipping README.pdf generation")
    else:
        currDir = os.getcwd()
        os.chdir('..')
        os.system('python -m grip README.md --export README.html')
        os.system('"{0}" {1} {2} {3}'.format(WKHTMLTOPDF_DIR, '--enable-local-file-access', 'README.html', os.path.join(PLUGIN_DIR,'README.pdf')))
        shutil.copy2(os.path.join(PLUGIN_DIR, 'README.pdf'), '.')
        os.chdir(currDir)

################################
## Step 6
## Copy the remaining plugin files
################################
for item in ALL_PLUGINS:
    shutil.copytree(os.path.abspath('./plugins/' + item),  RELEASE_PLUGINS_DIR / item, dirs_exist_ok = True)

################################
## Step 7
## Copy required files to the release directory
################################
remaining_files = [os.path.abspath('./LICENSE'),
                   os.path.abspath('./docs/icon.png'),
                   os.path.abspath('./resources/package.json')]

for file in remaining_files:
    shutil.copy2(file, RELEASE_TEMP_DIR)

################################
## Step 8
## Zip up the plugin for release
################################
with zipfile.ZipFile(CURA_PACKAGE_FILE, 'w', zipfile.ZIP_DEFLATED) as z:
    for item in RELEASE_TEMP_DIR.rglob('*'):
        if not item.is_file():
            continue
        relative_path = item.relative_to(RELEASE_TEMP_DIR)
        z.write(item, relative_path)


################################
## Step 9
## Make the ultimaker zip file for upload to contribute.ultimaker.com
################################
shutil.copy2(os.path.abspath('./LICENSE'), PLUGIN_DIR)

with zipfile.ZipFile(ULTIMAKER_ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
    for item in RELEASE_PLUGINS_DIR.rglob('*'):
        if not item.is_file():
            continue
        relative_path = item.relative_to(RELEASE_PLUGINS_DIR)
        z.write(item, relative_path)


################################
## Step 10
## Cleanup the files and directories
################################
shutil.rmtree(RELEASE_TEMP_DIR)


# List the contents of the directory
try:
    directory_contents = RELEASE_DIR.rglob('*')
    # Print the contents
    for item in directory_contents:
        print(item.absolute())
except FileNotFoundError:
    print(f"The directory {directory_path} does not exist.")