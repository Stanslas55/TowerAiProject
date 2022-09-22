from multiprocessing import Process, freeze_support
import multiprocessing
from time import sleep
from sys import exit
import keyboard

import pyautogui
from screeninfo import get_monitors

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

import cv2 as cv
import numpy as np

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

    # This section gets the main monitor's features (x and y start position, width and height).
    def __init__(self):
        monitor = get_monitors()[0]
        self.main_screen = (monitor.x, monitor.y, monitor.width, monitor.height)
        #print(main_screen)

        stat_box_width = 532 / 2 # 1065 / 2
        stat_box_height = 215 / 2 # 430 / 2

        X_stat_box = self.main_screen[0] + 1385 / 2
        Y_stat_box = 1380 / 2

        X_retry = self.main_screen[0] + 771
        Y_retry = 783

        stride = 5

        # loc variables contain starting X and Y, then Width and Height of the box.
        self.__locTL__ = (X_stat_box + stat_box_width / 2, Y_stat_box + 30, stat_box_width / 2 - 15, stat_box_height - 45)
        # center variables contains the center of the boxes, to click later when needed.
        self.__centerTL__ = (X_stat_box + stat_box_width / 2, Y_stat_box + stat_box_height / 2)

        self.__locTR__ = (X_stat_box + stat_box_width + stride + stat_box_width / 2, Y_stat_box + 29, stat_box_width / 2 - 15, stat_box_height - 45)
        self.__centerTR__ = (X_stat_box + stat_box_width + stride + stat_box_width / 2, Y_stat_box + stat_box_height / 2) 

        self.__locBR__ = (X_stat_box + stat_box_width + stride + stat_box_width / 2, Y_stat_box + stat_box_height + 35, stat_box_width / 2 - 40, stat_box_height - 45)
        self.__centerBR__ = (X_stat_box + stat_box_width + stride + stat_box_width / 2, Y_stat_box + stat_box_height + stat_box_height / 2)

        # Need to find the Sword, Shield, Star position and centers. Same proccess than before.
        X_tab_box = self.main_screen[0] + 1357 / 2
        Y_tab_box = 1973 / 2

        tab_box_width = 279.5 / 2 #559 / 2
        tab_box_height = 106 / 2

        self.__locSword__ = (X_tab_box, Y_tab_box, tab_box_width, tab_box_height)
        self.__centerSword__ = (X_tab_box + tab_box_width / 2, Y_tab_box + tab_box_height / 2)

        self.__locShield__ = (X_tab_box + tab_box_width + stride / 4, Y_tab_box, tab_box_width, tab_box_height)
        self.__centerShield__ = (X_tab_box + tab_box_width + stride / 4 + tab_box_width / 2, Y_tab_box + tab_box_height / 2)

        self.__locRetry__ = (X_retry, Y_retry, 173, 90)
        self.__centerRetry__ = (X_retry + 87, Y_retry + 45)

        self.exit = multiprocessing.Event()

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
            print("Problème")
            return -1

        if 'K' in x:
            return int(round(float(x.replace('K', '')) * 1000))

        if 'M' in x:       
            return int(round(float(x.replace('M', '')) * 1000000))

        return int(round(float(x)))

    def __processString__(self, x):          
        x = x.split("\n")
        
        # print(x)
        

        if(x[0][0] in ['x']):
            x = x[1:]                    
    
        x = [i.replace(',', '.') for i in x]
        x = [i.replace('$ ', '') for i in x]
        x = [i.replace('/sec', '') for i in x]       
        # If Shield, returns value (x[0]), else returns price (x[1])
        return x[0] if self.__focusValue__ else x[1]

    def __getPvPrice__(self):
        result_ocr = self.__screenToString__(region=self.__locTL__)  
        
        x = result_ocr.split("\n")
        
        if(x[0][0] in ['x']):
            x = x[1:]  

        x = [i.replace(',', '.') for i in x]
        x = [i.replace('$ ', '') for i in x]                
            
        return self.__letterToNumber__(x[1])  


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

            self.__phase2__()
            self.__phase3__()

            self.__updateThreshs__()           

    def __phase2__(self):
        self.__focusValue__ = True
        self.__click__(self.__centerShield__)

        regen = -1

        while(regen < self.__regenThresh__ and not self.exit.is_set()):
            sleep(0.5)
            self.__click__(self.__centerTR__)
            result_ocr = self.__screenToString__(region=self.__locTR__)  
            if result_ocr == ['']:
                continue
            processed_result = self.__processString__(result_ocr)        
            regen = self.__letterToNumber__(processed_result)
            print("Regen: ", regen)

        defense = -1
        
        while(defense < self.__defenseThresh__ and not self.exit.is_set()):
            sleep(0.5)
            self.__click__(self.__centerBR__)
            result_ocr = self.__screenToString__(region=self.__locBR__)
            if result_ocr == ['']:
                print("OK")
                continue        
            processed_result = self.__processString__(result_ocr)        
            defense = self.__letterToNumber__(processed_result)
            print("Defense: ", defense)

        pv = -1

        while(pv < self.__pvThresh__ and not self.exit.is_set()):
            sleep(0.5)
            self.__click__(self.__centerTL__)
            result_ocr = self.__screenToString__(region=self.__locTL__)      
            if result_ocr == ['']:
                continue  
            processed_result = self.__processString__(result_ocr)        
            pv = self.__letterToNumber__(processed_result)
            print("pv: ", pv)

        # Need to check pv price here and store the value.
        self.__pvPrice__ = self.__getPvPrice__()
        
        print("End of Phase 2.")

    def __phase3__(self):
        self.__focusValue__ = False
        self.__click__(self.__centerSword__)

        attaquePrice = -1

        while(attaquePrice < self.__pvPrice__ and not self.exit.is_set()):
            sleep(0.5)
            self.__click__(self.__centerTL__)
            result_ocr = self.__screenToString__(region=self.__locTL__)    
            if result_ocr == ['']:
                continue    
            processed_result = self.__processString__(result_ocr)        
            attaquePrice = self.__letterToNumber__(processed_result)

        print("End of Phase 3.")

    def __updateThreshs__(self):
        self.__regenThresh__ += self.__regenIncr__
        self.__defenseThresh__ += self.__defenseIncr__
        self.__pvThresh__ += self.__pvIncr__

    def appManager(self):
      
        while not self.exit.is_set():
            # In this part, we launch to game thread.
            print("\n\n/!\ Debut du jeu ! /!\ \n\n")
            runGame = Process(target=self.__runGame__)
            runGame.start()
            # In this part, we have to search if the ending screen is displayed. 
            # If yes, then kill the runGame thread.        
            # Then click on Retry and start a new runGame thread.
            while not self.exit.is_set():                              
                endingscreen = pyautogui.locateOnScreen('./images/Retry.png', region=self.main_screen)           
                
                if(endingscreen != None):                    
                    runGame.kill()
                    print("\n\n/!\ Fin du jeu ! /!\ \n\n")
                    sleep(5)
                    self.__click__(self.__centerRetry__)
                    break

    def quit_app(self):
        while(not self.exit.is_set()):           
            if keyboard.is_pressed("space"):
                print("Shutting Down the app")
                self.exit.set()
                exit()            

def main():
   
    if __name__== "__main__" :
        freeze_support()  

        print("Press Space to start the AI.")

        while not keyboard.is_pressed("space"):
            pass 

        tower = TowerAI()
        Process(target=tower.quit_app).start()
        
        tower.appManager()     
       
        print("Fin du programme")     
      
main()