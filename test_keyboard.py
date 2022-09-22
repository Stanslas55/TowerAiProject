import keyboard
import time

delay = 0.2 # or >= 0.2 secs works fine

while True:
    if keyboard.is_pressed("space"):
        print("Space key pressed!")
        
        exit() 
          