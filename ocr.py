import pytesseract
import pyautogui
import json
import time
import re
import os

# Constants
BASE_CFG_PATH = 'ocr.cfg'
LOCAL_CFG_PATH = 'local.cfg'

config = {}

def merge_configs(base_config, override_config):
    for key, value in override_config.items():
        if key in base_config and isinstance(value, dict) and isinstance(base_config[key], dict):
            merge_configs(base_config[key], value)
        else:
            base_config[key] = value

    return base_config

def read_config():
    with open(BASE_CFG_PATH, 'r') as file:
        config = json.load(file)

    with open(LOCAL_CFG_PATH, 'r') as file:
        return merge_configs(config, json.load(file))


def extract_text_from_screen(left, top, width, height):
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    extracted_text = pytesseract.image_to_string(screenshot)
    return extracted_text

def save_cfg():
    with open(LOCAL_CFG_PATH, 'w') as file:
        json.dump(config, file, indent=4)

def get_auth_level(name):
    auth = next((item for item in config['Authorization'] if item.get("Name") == name), None)
    return auth['Level'] if auth is not None else None

def sleep():
    time.sleep(config['TypeInterval'])

def extract_chat_message(text):
    pattern = '(.+)\s+.{1}\s(.+)'
    matched = re.match(pattern, text)
    return (matched.groups()[0], matched.groups()[1]) if matched else None

def write_to_chat(str):
    chars = [char for char in str]
    pyautogui.press('enter')
    sleep()
    pyautogui.press(chars)
    sleep()
    pyautogui.press('enter')

def look_for_command():
    pyautogui.screenshot
    text = extract_text_from_screen(config['ChatRegion']['Left'],
                                    config['ChatRegion']['Top'],
                                    config['ChatRegion']['Width'],
                                    config['ChatRegion']['Height'])\
                                        .strip()

    chat_msg = extract_chat_message(text)
    if chat_msg is None:
        return

    for command in config['Commands']:
        command_trigger = f'{config["CommandPrefix"]}{command["Regex"]}'
        matched = re.match(command_trigger, chat_msg[1])
        if matched and get_auth_level(chat_msg[0]) >= command['MinimumLevel']:
            command_function = COMMAND_FUNCTIONS.get(command['Name'])
            if command_function:
                function_arguments = matched.groups()
                command_function(function_arguments)
                message = command.get('Message')
                if message is not None:
                    write_to_chat(message)
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

def sp_command(args):
    write_to_chat('/p todo')

def buffs_command(args):
    for buff in config['BuffPositions']:
        pyautogui.click(button='right', x=buff['X'], y=buff['Y'])
        sleep()

COMMAND_FUNCTIONS = {
    "ADD_AUTH": add_auth_command,
    "REMOVE_AUTH": remove_auth_command,
    "SP": sp_command,
    "BUFFS": buffs_command
}

config = read_config()
while True:
    look_for_command()
