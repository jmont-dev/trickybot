from pynput.mouse import Button, Controller
mouse=Controller()

while True:
    mouse.click(Button.left, 1)