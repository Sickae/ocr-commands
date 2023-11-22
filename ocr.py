import pytesseract
from PIL import ImageGrab
import pyautogui
import json
import time
import re

# Constants
CFG_PATH = 'ocr.cfg'

with open(CFG_PATH, 'r') as file:
    config = json.load(file)

def extract_text_from_screen(left, top, width, height):
    screen_region = (left, top, left + width, top + height)
    screenshot = ImageGrab.grab(bbox=screen_region)

    extracted_text = pytesseract.image_to_string(screenshot)
    return extracted_text

def save_cfg():
    with open(CFG_PATH, 'w') as file:
        json.dump(config, file, indent=4)

def get_auth_level(name):
    auth = next((item for item in config['Authorization'] if item.get("Name") == name), None)
    return auth['Level'] if auth is not None else None

def look_for_command():
    text = extract_text_from_screen(config['ChatRegion']['Left'],
                                    config['ChatRegion']['Top'],
                                    config['ChatRegion']['Width'],
                                    config['ChatRegion']['Height'])
        .strip()
    
    print(f'text: {repr(text)}')
    
    for command in config['Commands']:
        matched = re.match(command['Regex'], text)
        if (matched):
            command_function = COMMAND_FUNCTIONS.get(command['Name'])
            if command_function:
                function_arguments = matched.groups()
                print(f'args: {function_arguments}')
                command_function(function_arguments)
                break
    
    time.sleep(1)

# Commands

def add_auth_command(args):
    if get_auth_level(args[0]) is not None:
        return
    
    config['Authorization'].append({"Name": args[0], "Level": int(args[1])})
    save_cfg()

def remove_auth_command(args):
    if get_auth_level(args[0]) is None:
        return

    auth = next((item for item in config['Authorization'] if item.get('Name') == args[0]), None)
    config['Authorization'].remove(auth)
    save_cfg()
    
def sp_command():
    print('sp command')

def buffs_command():
    for buff in config['BuffPositions']:
        pyautogui.click(buff['X'], buff['Y'])
        time.sleep(.5)

COMMAND_FUNCTIONS = {
    "ADD_AUTH": add_auth_command,
    "REMOVE_AUTH": remove_auth_command,
    "SP": sp_command,
    "BUFFS": buffs_command
}

while True:
    look_for_command()

