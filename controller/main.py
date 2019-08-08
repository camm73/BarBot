import RPi.GPIO as GPIO
import time
import tkinter as tk
import traceback
import threading
import json

class Main():

    def __init__(self):
        self.pumps = [26, 19, 13, 6, 5, 21, 20, 16]
        self.cocktailNames = {}
        self.cocktailIngredients = {}
        self.cocktailAmounts = {}
        self.cocktailButtons = {}
        self.pumpMap = {}
        self.pumpFull = {}
        self.cocktailCount = 0
        self.pumpTime = 18
        self.cleanTime = 6
        self.shotVolume = 44 #mL
        self.busy_flag = False
        self.window = None

        #Mode 0 is GUI, Mode 1 is Buttons
        self.setMode()

        self.setupPins()
        self.loadPumpMap()
        self.loadCocktails()
        
        #Button Mode
        if(self.mode == 1):
            self.buttonThread = threading.Thread(target=self.setupButtons)
            self.buttonThread.daemon = True
            self.buttonThread.start()
            self.buttonThread.join()
        elif(self.mode == 0):
            print("GUI MODE!")
        GPIO.cleanup()
        exit()

    #Sets up pins by setting gpio mode and setting initial output
    def setupPins(self):
        try:
            print("Setting up pump pins...")
            GPIO.setmode(GPIO.BCM)
            for pin in self.pumps:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.HIGH)
            print("Pins successfully setup!")
        except Exception as e:
            print("Error setting up pump pins: " + str(e))
            exit(1)

    #Test function that runs all of the pumps for 3 seconds each
    def testPumps(self):
        try:
            for pin in self.pumps:
                GPIO.output(pin, GPIO.LOW)
                print("Turning on pin " + str(pin))
                time.sleep(3)
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(1)
        except KeyboardInterrupt:
            print('Exitting early')
            GPIO.cleanup()
            exit()

    def loadCocktails(self):
        #Load cocktails from json file
        data = {}
        with open('cocktails.json', 'r') as file:
            data = json.load(file)

        i = 0
        #Loads all cocktail details into separate python objects
        for cocktails in data['cocktails']:
            self.cocktailNames[i] = (str(data['cocktails'][i]['name']))
            self.cocktailIngredients[i] = data['cocktails'][i]['ingredients']
            self.cocktailAmounts[i] = data['cocktails'][i]['amounts']
            i = i+1
        self.cocktailCount = i

    
    #Loads pump/ingredient map from json file
    def loadPumpMap(self):
        data = {}
        with open('pumpMap.json', 'r') as file:
            data = json.load(file)

        #print('Here is the data: ' + str(data))
        self.pumpFull = data
        
        mapObject = {}
        for item in data:
            mapObject[item] = data[item]["pump"]
        #Store pumpMap data in pumpMap dict
        self.pumpMap = mapObject

    #Function that crafts the cocktail requested
    def makeCocktail(self, num):
        if(self.busy_flag):
            #TODO add some feedback message
            print('Busy making cocktail!')
            return
        print('Making cocktail ' + str(self.cocktailNames[num]))
        self.busy_flag = True
        self.setupPins()

        #Now we need to turn on pumps for respective ingredients for specified times
        i = 0
        waitTime = 0
        biggestAmt = 0
        for ingredient in self.cocktailIngredients[num]:
            pumpThread = threading.Thread(target=self.pumpToggle, args=[self.pumpMap[ingredient], self.cocktailAmounts[num][i]])
            pumpThread.start()

            #Adjust volume tracking for each of the pumps
            print('Ingredient: ' + str(ingredient))
            self.adjustVolumeData(ingredient, self.cocktailAmounts[num][i])

            if(self.cocktailAmounts[num][i] > biggestAmt):
                biggestAmt = self.cocktailAmounts[num][i]
            i += 1
        
        waitTime = biggestAmt*self.pumpTime
        print('Wait Time: ' + str(waitTime))
        time.sleep(waitTime + 2)
        print("Done making cocktail!")

        self.busy_flag = False

    #Toggles specific pumps for specific amount of time
    def pumpToggle(self, num, amt):
        pumpPinIndex = num - 1
        pumpPin = self.pumps[pumpPinIndex]
        GPIO.output(pumpPin, GPIO.LOW)
        time.sleep(self.pumpTime*amt)
        GPIO.output(pumpPin, GPIO.HIGH)

    #Cleans Pumps by flushin them for time specified in self.cleanTime
    def cleanPumps(self):
        '''
        for pump in self.pumps:
            GPIO.output(pump, GPIO.LOW)
            time.sleep(self.cleanTime)
            GPIO.output(pump, GPIO.HIGH)
            print('Cleaned Pump ' + str(pump))
        '''

        print('Cleaning pumps!')
        for pump in self.pumps:
            GPIO.output(pump, GPIO.LOW)

        time.sleep(self.cleanTime)

        for pump in self.pumps:
            GPIO.output(pump, GPIO.HIGH)


    def setupButtons(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.OUT)
        GPIO.output(23, GPIO.HIGH)

        GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        while True:
            try:
                if (GPIO.input(24) == GPIO.HIGH):
                    self.makeCocktail(2)
            except KeyboardInterrupt:
                break

    
    def setMode(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        time.sleep(0.25)
        pinInput = GPIO.input(12)
        print('Mode Input: ' + str(pinInput))
        if(pinInput != 0):
            self.mode = 0
        else:
            self.mode = 1

    def adjustVolumeData(self, ingredientName, shotAmount):
        print('Value: ' + self.pumpFull[ingredientName]['volume'])
        newVal = int(self.pumpFull[ingredientName]['volume']) - (self.shotVolume*shotAmount)
        print('New Value: ' + str(newVal))
        self.pumpFull[ingredientName]['volume'] = str(newVal)
        self.writePumpData()


    def writePumpData(self):
        with open('pumpMap.json', 'w') as file:
            json.dump(self.pumpFull, file)
        

'''
if __name__ == '__main__':
    main = Main()
    GPIO.cleanup()
    print('Done')
'''