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
        self.cocktailCount = 0
        self.pumpTime = 3
        self.cleanTime = 6
        self.busy_flag = False

        self.setupPins()
        self.loadPumpMap()
        self.loadCocktails()
        self.windowThread = threading.Thread(target=self.createGUI)
        self.windowThread.start()
        self.windowThread.join()
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
        
        #Store pumpMap data in pumpMap dict
        self.pumpMap = data

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
        for ingredient in self.cocktailIngredients[num]:
            pumpThread = threading.Thread(target=self.pumpToggle, args=[self.pumpMap[ingredient], self.cocktailAmounts[num][i]])
            pumpThread.start()
            waitTime += self.cocktailAmounts[num][i]
            i += 1
        
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
        for pump in self.pumps:
            GPIO.output(pump, GPIO.LOW)
            time.sleep(self.cleanTime)
            GPIO.output(pump, GPIO.HIGH)
            print('Cleaned Pump ' + str(pump))

    #Creates the GUI interface for selecting a cocktail
    def createGUI(self):
        window = tk.Tk()
        window.grid()
        window.geometry('800x400')
        window.title('BarBot - Beta Version 1.0')
        i = 0
        for drink in self.cocktailNames:
            name = self.cocktailNames[i]
            self.cocktailButtons[i] = tk.Button(window, text=name, width = 20, height =10, command= lambda i=i: self.makeCocktail(i))
            self.cocktailButtons[i].pack()
            i = i+1
        stopButton = tk.Button(window, text='STOP', width = 4, height = 2, command=window.destroy)
        stopButton.pack()
        cleanButton = tk.Button(window, text='Clean Pumps', width = 8, height = 4, command=self.cleanPumps)
        cleanButton.pack()
        window.mainloop()



if __name__ == '__main__':
    main = Main()
    GPIO.cleanup()
    print('Done')
        
