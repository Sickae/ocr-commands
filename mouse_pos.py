import pyautogui
import time

x = 0
y = 0

def get_mouse_pos():
    global x, y
    pos = pyautogui.position()
    if x != pos[0] and y != pos[1]:
        x = pos[0]
        y = pos[1]
        print(f'{x}, {y}')
        
while True:
    get_mouse_pos()
    time.sleep(1) 