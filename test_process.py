from multiprocessing import Process, freeze_support
import sys
from time import sleep
import keyboard

def test():
    while(True):
        sleep(1)
        print("Game Started")

def manageApp():
    while(True):
            #threading.Thread(target=TowerAI.runGame).start()
            runGame = Process(target=test)
            runGame.start()
            # In this part, we have to search if the ending screen is displayed. 
            # If yes, then kill the runGame thread.        
            # Then click on Retry and start a new runGame thread.
            i = 0
            while(True):
                sleep(1)
                i += 1
                
                if(i == 3):                   
                    runGame.kill()
                    print("Restart Game")
                    break

def quit_app():
 
    while True:
        if keyboard.is_pressed("space"):
            
            sys.exit() 

if __name__ == '__main__':  
    freeze_support()   
    quit = Process(target=quit_app)
    #quit.start()
    manageApp()        