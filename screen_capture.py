import threading
from time import sleep

import pyautogui
from screeninfo import get_monitors

import pytesseract

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

    __focusValue__ = True

    centerRetry = None # TODO: define.

    # This section gets the main monitor's features (x and y start position, width and height).
    def __init__(self):
        monitor = get_monitors()[0]
        self.main_screen = (monitor.x, monitor.y, monitor.width, monitor.height)
        #print(main_screen)

        stat_box_width = 532 # 1065 / 2
        stat_box_height = 215 # 430 / 2

        X_stat_box = self.main_screen[0] + 1385
        Y_stat_box = 1380

        stride = 10

        # loc variables contain starting X and Y, then Width and Height of the box.
        self.__locTL__ = (X_stat_box + stat_box_width / 2, Y_stat_box, stat_box_width / 2, stat_box_height)
        # center variables contains the center of the boxes, to click later when needed.
        self.__centerTL__ = (X_stat_box + stat_box_width / 2, Y_stat_box + stat_box_height / 2)

        self.__locTR__ = (X_stat_box + stat_box_width + stride + stat_box_width / 2, Y_stat_box, stat_box_width / 2, stat_box_height)
        self.__centerTR__ = (X_stat_box + stat_box_width + stride + stat_box_width / 2, Y_stat_box + stat_box_height / 2) 

        self.__locBR__ = (X_stat_box + stat_box_width + stride + stat_box_width / 2, Y_stat_box + stat_box_height, stat_box_width / 2, stat_box_height)
        self.__centerBR__ = (X_stat_box + stat_box_width + stride + stat_box_width / 2, Y_stat_box + stat_box_height + stat_box_height / 2)

        # Need to find the Sword, Shield, Star position and centers. Same proccess than before.
        X_tab_box = self.main_screen[0] + 1357
        Y_tab_box = 1973

        tab_box_width = 279.5 #559 / 2
        tab_box_height = 106

        self.__locSword__ = (X_tab_box, Y_tab_box, tab_box_width, tab_box_height)
        self.__centerSword__ = (X_tab_box + tab_box_width / 2, Y_tab_box + tab_box_height / 2)

        self.__locShield__ = (X_tab_box + tab_box_width + stride / 4, Y_tab_box, tab_box_width, tab_box_height)
        self.__centerShield__ = (X_tab_box + tab_box_width + stride / 4 + tab_box_width / 2, Y_tab_box + tab_box_height / 2)

##### PROCESSING METHODS #####
    def __click__(self, item):
        pyautogui.click(x=item[0], y=item[1], clicks=1, button='left')

    def __screenToString__(self, region):

        screen_to_ocr = pyautogui.screenshot(region=region)
        screen_to_ocr = np.array(screen_to_ocr)
        res, threshed_screen = cv.threshold(screen_to_ocr, 127, 255, cv.THRESH_BINARY_INV)

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
        print("In processShieldString")   
        self.__focusValue__ = False     
        x = x.split("\n")

        if(x[0][0] in ['x']):
            x = x[1:]                  
     
        print(x)
        x = [i.replace(',', '.') for i in x]
        x = [i.replace('$ ', '') for i in x]
        x = [i.replace('/sec', '') for i in x]       
        # If Shield, returns value (x[0]), else returns price (x[1])
        return x[0] if self.__focusValue__ else x[1]

    def __getPvPrice__(self):
        result_ocr = self.__screenToString__(region=self.__locTL__)  
        
        x = result_ocr.split("\n")[2:3]
        x = [i.replace(',', '.') for i in x]
        x = [i.replace('$ ', '') for i in x]                
            
        return self.__letterToNumber__(x[0])  


 ##### TEST METHODS #####       

    def test_ocr(self):      
        sleep(5)

        all_loc = [self.__locTL__, self.__locTR__, self.__locBR__]
        for loc in all_loc:
           
            result_ocr = self.__screenToString__(region=loc)        
            processed_result = self.__processShieldString__(result_ocr)        
            value = self.__letterToNumber__(processed_result)
            print(value)

    def test_pv_price(self):
        sleep(5)
        self.__getPvPrice__()    

    def test_attaque_price(self):
        sleep(5)       
        Degats_OCR = self.__screenToString__(region=self.__locTL__)
        res = self.__processSwordString__(Degats_OCR)
        value = self.__letterToNumber__(res)
        print(value)

##### GAME METHODS #####

    def runGame(self):           

        while(True):

            self.__phase2__()
            self.__phase3__()

            self.__updateThreshs__()

            # Infinite Loop for the moment.
            # TODO: Need to create a thread that look for the ending screen, then stop this loop (thread) by updating playing with False.

    def __phase2__(self):
        self.__focusValue__ = True
        self.__click__(self.__centerShield__)

        regen = -1

        while(regen < self.__regenThresh__):
            sleep(0.5)
            self.__click__(self.__centerTR__)
            result_ocr = self.__screenToString__(region=self.__locTR__)        
            processed_result = self.__processShieldString__(result_ocr)        
            regen = self.__letterToNumber__(processed_result)

        defense = -1
        
        while(defense < self.__defenseThresh__):
            sleep(0.5)
            self.__click__(self.__centerBR__)
            result_ocr = self.__screenToString__(region=self.__locBR__)        
            processed_result = self.__processShieldString__(result_ocr)        
            defense = self.__letterToNumber__(processed_result)

        pv = -1

        while(pv < self.__pvThresh__):
            sleep(0.5)
            self.__click__(self.__centerTL__)
            result_ocr = self.__screenToString__(region=self.__locTL__)        
            processed_result = self.__processShieldString__(result_ocr)        
            pv = self.__letterToNumber__(processed_result)

        # Need to check pv price here and store the value.
        self.__pvPrice__ = self.__getPvPrice__()
        
        print("End of Phase 2.")

    def __phase3__(self):
        self.__focusValue__ = False
        self.__click__(self.__centerSword__)

        attaquePrice = -1

        while(attaquePrice < self.__pvPrice__):
            sleep(0.5)
            self.__click__(self.__centerTL__)
            result_ocr = self.__screenToString__(region=self.__locTL__)        
            processed_result = self.__processSwordString__(result_ocr)        
            attaquePrice = self.__letterToNumber__(processed_result)

        print("End of Phase 3.")

    def __updateThreshs__(self):
        self.__regenThresh__ += self.__regenIncr__
        self.__defenseThresh__ += self.__defenseIncr__
        self.__pvThresh__ += self.__pvIncr__


    def stopGame(self):
        # In this part, we have to search if the ending screen is displayed. 
        # If yes, then kill the runGame thread.        
        # Then click on Retry and start a new runGame thread.
        while(True):
            # TODO: Ask for EndingScreen.png
            endingscreen = pyautogui.locateOnScreen('./images/EndingScreen.png', region=self.main_screen)
            print(endingscreen)
            if(endingscreen != None):
                # TODO: Kill runGame thread.

                # Click on retry.
                self.__click__(self.centerRetry)

                # TODO: Start runGame thread.

        

def main():
   
    if __name__== "__main__" :
        
        tower = TowerAI()
        tower.test_ocr()
        
        #threading.Thread(target=TowerAI.runGame).start()
        #threading.Thread(target=TowerAI.stopGame).start()
        

main()