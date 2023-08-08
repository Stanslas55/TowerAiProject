from multiprocessing import Process, freeze_support
import multiprocessing
from multiprocessing.sharedctypes import Value
from time import sleep
from sys import exit
import keyboard

import pyautogui
from screeninfo import get_monitors

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

import cv2 as cv
import numpy as np

from datetime import datetime
from time import strftime


def wfile(msg, mode='a'):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    with open('logs.txt', mode) as f:
        txt = "{}: {}\n".format(dt_string, msg)
        f.write(txt)

class TowerAI:
    
    __regenThresh__ = 500
    __defenseThresh__ = 5000
    __pvThresh__ = 1000000

    __regenIncr__ = 500
    __defenseIncr__ = 5000
    __pvIncr__ = 1000000

    __pvPrice__ = 0

    # On Phase 2, we focus on the Value in the OCRed string. 
    # On Phase 3, we focus on the Price in the OCRed string.
    __focusValue__ = True    

    __nphase__ =  0

    # This section gets the main monitor's features (x and y start position, width and height).
    def __init__(self):
        wfile("\n\n\t\tInitialisation", 'w')
        monitor = get_monitors()[0]
        self.main_screen = (monitor.x, monitor.y, monitor.width, monitor.height)
        #print(main_screen)

        stat_box_width = 532 / 2 # 1065 / 2
        stat_box_height = 215 / 2 # 430 / 2

        X_stat_box = self.main_screen[0] + 1385 / 2
        Y_stat_box = 1380 / 2

        X_retry = self.main_screen[0] + 770
        Y_retry = 782

        # A
        X_diamond_local = 691
        # B
        Y_diamond_local = 365
        # C
        Diamond_width = 124
        # D
        Diamond_height = 76

        Retry_width = 175
        Retry_height = 93

        X_diamond = self.main_screen[0] + X_diamond_local
        Y_diamond = Y_diamond_local

        X_tournament = self.main_screen[0] + 877
        Y_tournament = 609

        X_start = self.main_screen[0] + 822
        Y_start = 772      

        stride = 5

        # loc variables contain starting X and Y, then Width and Height of the box.
        self.__locTL__ = (X_stat_box + stat_box_width / 2, Y_stat_box + 30, stat_box_width / 2 - 15, stat_box_height - 45)
        # center variables contains the center of the boxes, to click later when needed.
        self.__centerTL__ = (X_stat_box + stat_box_width / 2 + 50, Y_stat_box + stat_box_height / 2)

        self.__locTR__ = (X_stat_box + stat_box_width + stride + stat_box_width / 2, Y_stat_box + 29, stat_box_width / 2 - 15, stat_box_height - 45)
        self.__centerTR__ = (X_stat_box + stat_box_width + stride + stat_box_width / 2 + 50, Y_stat_box + stat_box_height / 2) 
 
        self.__locBR__ = (X_stat_box + stat_box_width + stride + stat_box_width / 2, Y_stat_box + stat_box_height + 35, stat_box_width / 2 - 40, stat_box_height - 45)
        self.__centerBR__ = (X_stat_box + stat_box_width + stride + stat_box_width / 2 +  stat_box_width / 3, Y_stat_box + stat_box_height + stat_box_height / 2)

        # Need to find the Sword, Shield, Star position and centers. Same proccess than before.
        X_tab_box = self.main_screen[0] + 1357 / 2
        Y_tab_box = 1973 / 2

        tab_box_width = 279.5 / 2 #559 / 2
        tab_box_height = 106 / 2

        self.__locSword__ = (X_tab_box, Y_tab_box, tab_box_width, tab_box_height)
        self.__centerSword__ = (X_tab_box + tab_box_width / 2, Y_tab_box + tab_box_height / 2)

        self.__locShield__ = (X_tab_box + tab_box_width + stride / 4, Y_tab_box, tab_box_width, tab_box_height)
        self.__centerShield__ = (X_tab_box + tab_box_width + stride / 4 + tab_box_width / 2, Y_tab_box + tab_box_height / 2)

        self.__locRetry__ = (X_retry, Y_retry, Retry_width, Retry_height)
        self.__centerRetry__ = (X_retry + Retry_width / 4, Y_retry + Retry_height / 4)

        self.__locDiamond__ = (X_diamond, Y_diamond, Diamond_width, Diamond_height)
        self.__centerDiamond__ = (X_diamond + Diamond_width / 2, Y_diamond + Diamond_height / 2)

        self.__locTournament__ = (X_tournament, Y_tournament, 165, 86)
        self.__centerTournament__ = (X_tournament + 165 / 2, Y_tournament + 86 / 2)

        self.__locStart__ = (X_start, Y_start, 280, 112)
        self.__centerStart__ = (X_start + 280 / 2, Y_start + 112 / 2)      

        self.exit = multiprocessing.Event()
        self.pause = multiprocessing.Event()

##### PROCESSING METHODS #####
    def __click__(self, item):
        pyautogui.click(x=item[0], y=item[1], clicks=1, button='left')

    def __screenToString__(self, region):

        screen_to_ocr = pyautogui.screenshot(region=region)        
        screen_to_ocr = np.array(screen_to_ocr)
        gray = cv.cvtColor(screen_to_ocr, cv.COLOR_BGR2GRAY)
        res, threshed_screen = cv.threshold(gray, 127, 255, cv.THRESH_BINARY_INV)

        return pytesseract.image_to_string(threshed_screen)    

    def __letterToNumber__(self, x):          

        if x == '' :
            wfile("__letterToNumber__ returns -1")            
            return -1

        try:
            if 'K' in x:
                return int(round(float(x.replace('K', '')) * 1000))

            if 'M' in x:       
                return int(round(float(x.replace('M', '')) * 1000000))

        except ValueError:
            return -1

        return int(round(float(x)))

    def __processString__(self, x):   

        x = x.split("\n")              
        x.remove('') 
        
        wfile("In processingString: x = {}".format(x))     

        if(x == []):
            return x                   
    
        x = [i.replace(',', '.') for i in x]
        x = [i.replace('$ ', '') for i in x]
        x = [i.replace('/sec', '') for i in x]       
        # If Shield, returns value (x[0]), else returns price (x[1])
        return x[0] if self.__focusValue__ else x[1]

    def __getPvPrice__(self):      

        wfile("In getPvPrice") 

        result_ocr = self.__screenToString__(region=self.__locTL__)  
        
        x = result_ocr.split("\n")
        
        if(x[0][0] in ['x']):
            x = x[1:]  

        x = [i.replace(',', '.') for i in x]
        x = [i.replace('$ ', '') for i in x]   

        wfile("x after processing: {}".format(x))

        result = self.__letterToNumber__(x[1])             
            
        return result

 
 ##### TEST METHODS #####       

    def test_ocr(self):      
        sleep(5)

        all_loc = [self.__locTL__, self.__locTR__, self.__locBR__]
        for loc in all_loc:
           
            result_ocr = self.__screenToString__(region=loc)        
            processed_result = self.__processString__(result_ocr)        
            value = self.__letterToNumber__(processed_result)
            print(value)

    def test_pv_price(self):
        sleep(5)
        print("PV price: " , self.__getPvPrice__() )   

    def test_attaque_price(self):
        sleep(5)       
        Degats_OCR = self.__screenToString__(region=self.__locTL__)
        res = self.__processString__(Degats_OCR)
        value = self.__letterToNumber__(res)
        print("Attaque price", value)

    def test_clicks(self):

        self.__click__(self.__centerTL__)
        sleep(1)
        self.__click__(self.__centerTR__)
        sleep(1)
        self.__click__(self.__centerBR__)
        sleep(1)
        self.__click__(self.__centerSword__)
        sleep(1)
        self.__click__(self.__centerShield__) 
        sleep(1)

        self.__click__(self.__centerRetry__)

    def test_retry(self):
        ret = pyautogui.screenshot(region=self.__locRetry__) 
        ret.show()

##### GAME METHODS #####

    def __runGame__(self):           

        while not self.exit.is_set():
            if not self.pause.is_set():
                if self.__nphase__ != 2:
                    self.__click__(self.__centerShield__)
                try:
                    self.__phase2__()
                except ValueError:
                    continue

                self.__click__(self.__centerSword__)
                try:
                    self.__phase3__()
                except ValueError:
                    continue                          

                self.__updateThreshs__() 
                       
    def __phase2__(self):
        wfile("\tIn __phase2__")
        self.__focusValue__ = True      
        self.__nphase__ = 2

        regen = -1

        while(regen < self.__regenThresh__ and not self.exit.is_set()):
            if not self.pause.is_set():
                sleep(0.5)
                self.__click__(self.__centerTR__)
                result_ocr = self.__screenToString__(region=self.__locTR__)  
            
                processed_result = self.__processString__(result_ocr) 
                if processed_result == []:
                    wfile("No match in regen")   
                    continue    
                regen = self.__letterToNumber__(processed_result)
                wfile("Regen: {}".format(regen))

        defense = -1
        
        while(defense < self.__defenseThresh__ and not self.exit.is_set()):
            if not self.pause.is_set():
                sleep(0.5)
                self.__click__(self.__centerBR__)
                result_ocr = self.__screenToString__(region=self.__locBR__)
                    
                processed_result = self.__processString__(result_ocr)    
                if processed_result == []:
                    wfile("No match in defense")   
                    continue     
                defense = self.__letterToNumber__(processed_result)
                wfile("Defense: {}".format(defense))

        pv = -1

        while(pv < self.__pvThresh__ and not self.exit.is_set()):
            if not self.pause.is_set():
                sleep(0.5)
                self.__click__(self.__centerTL__)
                result_ocr = self.__screenToString__(region=self.__locTL__)      
                
                processed_result = self.__processString__(result_ocr)   
                if processed_result == []:
                    wfile("No match in pv")   
                    continue      
                pv = self.__letterToNumber__(processed_result)
                wfile("pv: {}".format(pv))

        # Need to check pv price here and store the value.
        self.__pvPrice__ = self.__getPvPrice__()
        
        wfile("End of Phase 2.")

    def __phase3__(self):
        wfile("\tIn __phase3__")
        self.__focusValue__ = False 
        self.__nphase__ = 3        

        attaquePrice = -1

        wfile("attaquePrice = {}".format(attaquePrice))
        wfile("pvPrice = {}".format(self.__pvPrice__))
        wfile("self.exit.is_set() = {}".format(self.exit.is_set()))
        
        while(attaquePrice < self.__pvPrice__ and not self.exit.is_set()):   
            if not self.pause.is_set():        
                sleep(0.5)
                self.__click__(self.__centerTL__)
                result_ocr = self.__screenToString__(region=self.__locTL__)    
                
                processed_result = self.__processString__(result_ocr)    
                if processed_result == []:
                        wfile("No match in attaque")   
                        continue     
                attaquePrice = self.__letterToNumber__(processed_result)

        wfile("End of Phase 3.")

    def __updateThreshs__(self): 
        self.__regenThresh__ += self.__regenIncr__
        self.__defenseThresh__ += self.__defenseIncr__
        self.__pvThresh__ += self.__pvIncr__

    def __searchDiamonds__(self):

        wfile("---------------------In searchDiamonds---------------------")

        while not self.exit.is_set():
            
            diamond = pyautogui.locateOnScreen('./images/DiamondPopUp2.png', region=self.__locDiamond__)

            if diamond != None:            
                wfile("\t\t\tDIAMOND FOUND !!")
                print("DIAMOND FOUND !! :)")
                
                # TODO: Need to pause the runGame process here
                self.pause.set()
                self.__click__(self.__centerDiamond__)
                # TODO: Unpause the runGame process here
                self.pause.clear()
                sleep(5)

    # def __get_tournament__(self):

    #     wfile("---------------------In getTournament---------------------")

    #     while not self.exit.is_set():
    #         year, month, day, hour, min = map(int, strftime("%Y %m %d %H %M").split())

    #         if(hour == 2 and min <= 10):
    #             wfile("IT'S 2AM !!!")

    #             tournamentScreen = pyautogui.locateOnScreen('./images/Tournament.png', region=self.main_screen)           
                        
    #             if(tournamentScreen != None):                      
    #                 self.pause.set()     
    #                 self.__click__(self.__centerTournament__)
    #                 sleep(5)
    #                 self.__click__(self.__centerStart__)
    #                 self.pause.clear()                

    def appManager(self):
        nb_game = 0
      
        while not self.exit.is_set():
            runGame = Process(target=self.__runGame__)
            searchDiamond = Process(target=self.__searchDiamonds__)
           
            try:
                # In this part, we launch to game thread.
                wfile("\n\n/!\ Debut du jeu ! /!\ \n\n")
                
                runGame.start()
                searchDiamond.start()

                nb_game += 1
                
                # In this part, we have to search if the ending screen is displayed. 
                # If yes, then kill the runGame thread.        
                # Then click on Retry and start a new runGame thread.

                if not self.pause.is_set():
                    while not self.exit.is_set():                              
                        endingscreen = pyautogui.locateOnScreen('./images/Retry.png', region=self.main_screen)           
                        
                        if(endingscreen != None):        
                            searchDiamond.kill()            
                            runGame.kill()

                            wfile(f"\n\n/!\ Fin de la game {nb_game} ! /!\ \n\n")

                            self.__click__(self.__centerRetry__)
                            break
            except ValueError:
                wfile("HUGO DIS MOI SI TU VOIS CE MESSAGE !!!!!!")
                searchDiamond.kill()
                runGame.kill()
                continue 

    def quit_app(self):
        while not self.exit.is_set():           
            if keyboard.is_pressed("space"):
                print("Shutting Down the app")
                wfile("Shutting Down the app")
                self.exit.set()
                exit()                     

def main():
      
    if __name__== "__main__" :
         
        freeze_support()  

        # print("Press Space to start the  AI.") 
 
        # while not keyboard.is_pressed("space"):
        #     pass  

        tower = TowerAI() 
        
        Process(target=tower.quit_app).start()
        
        
        tower.appManager()     
       
        print("Fin du programme")     
      
main() 