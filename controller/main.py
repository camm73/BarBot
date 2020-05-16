import RPi.GPIO as GPIO
import time
import tkinter as tk
import traceback
import threading
from recipe import uploadRecipe, getRecipe, getAllRecipes
from utils import nameToUpper
from cocktailStats import incrementCocktail
import json

class Main():

    def __init__(self):
        self.pumps = [26, 19, 13, 6, 5, 21, 20, 16]
        self.polarityPins = [17, 27] #Pin 17 is #1 and Pin #27 is #2
        self.pumpTimes = [23, 23, 23, 23.7, 23, 23, 23, 23]
        self.polarityNormal = True
        self.cocktailNames = {}
        self.cocktailIngredients = {}
        self.cocktailAmounts = {}
        self.cocktailButtons = {}
        self.cocktailNumbers = {}
        self.cocktailAvailable = {}
        self.alcoholList = []
        self.alcoholMode = False
        self.newBottles = []
        self.pumpMap = {}
        self.pumpNumbers = {}
        self.pumpFull = {}
        self.cocktailCount = 0
        #self.pumpTime = 23.7 #23.7s is exactly one shot on pump 4
        self.cleanTime = 8  #Regular Time: 12 seconds
        self.shotVolume = 44 #mL
        self.busy_flag = False
        self.window = None

        #Mode 0 is GUI, Mode 1 is Buttons
        self.setMode()

        self.setupPins()
        self.loadPumpMap()
        self.loadNewBottles()
        #self.loadCocktails()  REMOVED TO REPLACE WITH updateLocalRecipes
        self.updateLocalRecipes()
        self.loadAlcoholList()


        #Button Mode
        if(self.mode == 1):
            self.buttonThread = threading.Thread(target=self.setupButtons)
            self.buttonThread.daemon = True
            self.buttonThread.start()
        elif(self.mode == 0):
            print("GUI MODE!")

    #Sets up pins by setting gpio mode and setting initial output
    def setupPins(self):
        try:
            print("Setting up pump pins...")
            GPIO.setmode(GPIO.BCM)
            for pin in self.pumps:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.HIGH)

            #Turn on signal for #1 relay
            GPIO.setup(self.polarityPins[0], GPIO.OUT)
            GPIO.output(self.polarityPins[0], GPIO.LOW)

            # Turn off signal for #2 relay
            GPIO.setup(self.polarityPins[1], GPIO.OUT)
            GPIO.output(self.polarityPins[1], GPIO.HIGH)
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

        self.cocktailAvailable = {}
        i = 0
        #Loads all cocktail details into separate python objects
        for cocktails in data['cocktails']:
            self.cocktailNames[i] = (str(data['cocktails'][i]['name']))
            self.cocktailIngredients[i] = data['cocktails'][i]['ingredients']
            self.cocktailAmounts[i] = data['cocktails'][i]['amounts']
            self.cocktailNumbers[str(data['cocktails'][i]['name'])] = i
            self.cocktailAvailable[str(data['cocktails'][i]['name'])] = self.isAvailable(str(data['cocktails'][i]['name']))
            print(self.cocktailNames[i] + " available: " + str(self.cocktailAvailable[str(data['cocktails'][i]['name'])]))
            i = i+1
        self.cocktailCount = i


    #Loads the list of ingredients that are alcohol
    def loadAlcoholList(self):
        data = {}

        with open('alcohol.json', 'r') as file:
            data = json.load(file)
        
        for key in data:
            if(data[key] == True):
                self.alcoholList.append(key)

    
    #Add cocktail recipe to BarBot-Recipes Table in DynamoDB
    def addCocktailRecipe(self, recipe):
        if(uploadRecipe(recipe)):
            #TODO: Need to update the local recipe list json file
            res = self.updateLocalRecipes()
            if(res == False):
                return 'false'
            return 'true'
        return 'false'

    #Updates cocktails.json with data from the Dynamodb table
    def updateLocalRecipes(self):
        newRecipeRaw = getAllRecipes()

        if(newRecipeRaw == {}):
            print('Error getting recipes from DynamoDB')
            return False

        newCocktailJSON = {'cocktails': []}

        for rec in newRecipeRaw:
            amountItem = json.loads(newRecipeRaw[rec])['amounts']
            
            ingredientArr = []
            amountsArr = []
            for ingredient in amountItem:
                ingredientArr.append(ingredient)
                amountsArr.append(amountItem[ingredient])
            
            newItew = {
                "name": rec,
                "ingredients": ingredientArr,
                "amounts": amountsArr
            }

            newCocktailJSON['cocktails'].append(newItew)

        with open('cocktails.json', 'w') as file:
            json.dump(newCocktailJSON, file)

        print('Wrote new cocktails to file')

        self.loadCocktails()

        return True


    #Scans through the ingredients on each pump and the ingredients needed for this cocktail to determine availability
    def isAvailable(self, cocktailName):
        cocktailNumber = self.cocktailNumbers[cocktailName]
        
        if(not self.alcoholMode):
            for ingredient in self.cocktailIngredients[cocktailNumber]:
                if(ingredient not in self.pumpMap.keys()):
                    print(ingredient + " not available!")
                    return False
            return True
        else:
            for ingredient in self.cocktailIngredients[cocktailNumber]:
                if(ingredient in self.alcoholList):
                    if(ingredient not in self.pumpMap.keys()):
                        print(ingredient + " not available!")
                        return False
            return True
    
    #Loads pump/ingredient map from json file (ALSO SET PUMP NUMBERS)
    def loadPumpMap(self):
        data = {}
        with open('pumpMap.json', 'r') as file:
            data = json.load(file)

        #print('Here is the data: ' + str(data))
        self.pumpFull = data
        self.pumpNumbers = {}
        
        mapObject = {}
        for item in data:
            mapObject[item] = data[item]["pump"]
            self.pumpNumbers[data[item]["pump"]] = item
        #Store pumpMap data in pumpMap dict
        self.pumpMap = mapObject

    
    #Load new bottles
    def loadNewBottles(self):
        with open('bottles.json', 'r') as file:
            data = json.load(file)

        self.newBottles = data
        print(self.newBottles)


    #Write bottles list to the bottles.json file
    def writeNewBottles(self):
        with open('bottles.json', 'w') as file:
            json.dump(self.newBottles, file)

    
    #Adds new bottle to the bottle list
    def addNewBottleToList(self, bottleName):
        print("ADDING " + bottleName + " TO BOTTLE LIST")
        if(bottleName.lower() not in self.newBottles):
            self.newBottles.append(bottleName.lower())
            self.writeNewBottles()
        else:
            print('Bottle: ' + bottleName + "  is already in the list")


    #Removes bottle from bottle list
    def removeBottleFromList(self, bottleName):
        if(bottleName in self.newBottles):
            self.newBottles.remove(bottleName)
            self.writeNewBottles()
        else:
            print("Bottle: " + bottleName + "  not in list to begin with!")


    #Function that crafts the cocktail requested
    def makeCocktail(self, cocktailName):
        if(self.busy_flag):
            #TODO add some feedback message
            print('Busy making cocktail!')
            return 'busy'
        num = self.cocktailNumbers[cocktailName]
        
        #Check whether the cocktail is available or not
        if(not self.cocktailAvailable[cocktailName]):
            print('This cocktail is not avialable!')
            return 'available'
        
        #Check whether there are enough ingredients
        if(not self.canMakeCocktail(cocktailName)):
            print('Not enough ingredients to make this cocktail.')
            return 'ingredients'
        
        print('Making cocktail ' + str(self.cocktailNames[num]))
        self.busy_flag = True
        self.setupPins()

        #Now we need to turn on pumps for respective ingredients for specified times
        i = 0
        waitTime = 0
        biggestAmt = 0
        biggestPumpNum = -1
        for ingredient in self.cocktailIngredients[num]:
            #Skip pumping non-alcohol ingredients
            if(self.alcoholMode and ingredient not in self.alcoholList):
                print(ingredient + ' is not alcohol. Skipping to next ingredient...')
                continue

            #Create threads to handle running the pumps
            pumpThread = threading.Thread(target=self.pumpToggle, args=[self.pumpMap[ingredient], self.cocktailAmounts[num][i]])
            pumpThread.start()

            #Adjust volume tracking for each of the pumps
            print('Ingredient: ' + str(ingredient))
            self.adjustVolumeData(ingredient, self.cocktailAmounts[num][i])

            if(self.cocktailAmounts[num][i] > biggestAmt):
                biggestAmt = self.cocktailAmounts[num][i]
                biggestPumpNum = self.pumpMap[ingredient]
            i += 1
        
        waitTime = biggestAmt*self.pumpTimes[biggestPumpNum-1] #Must subtract 1 to get right index
        print('Wait Time: ' + str(waitTime))
        time.sleep(waitTime + 2)
        print("Done making cocktail!")

        #Update Stat tracking in the cloud
        incrementCocktail(cocktailName)

        self.busy_flag = False
        return 'true'

    #Toggles specific pumps for specific amount of time
    def pumpToggle(self, num, amt):
        pumpPinIndex = num - 1
        pumpPin = self.pumps[pumpPinIndex]
        GPIO.output(pumpPin, GPIO.LOW)
        time.sleep(self.pumpTimes[pumpPinIndex]*amt)
        GPIO.output(pumpPin, GPIO.HIGH)

    #Turns on a specific pump for indefinite amount of time
    def pumpOn(self, num):
        pumpPinIndex = num - 1
        pumpPin = self.pumps[pumpPinIndex]
        print('Turning on pump: ' + str(num))
        GPIO.output(pumpPin, GPIO.LOW)

    #Turns off a specific pump for indefinite amount of time
    def pumpOff(self, num):
        pumpPinIndex = num - 1
        pumpPin = self.pumps[pumpPinIndex]
        print("Turning off pump: " + str(num))
        GPIO.output(pumpPin, GPIO.HIGH)

    
    #Calibrates a specific pump by setting it's specific pumping time
    def calibratePump(self, pumpNum, time):
        indexNum = pumpNum - 1
        try:
            ingredient = self.pumpNumbers[pumpNum]
            self.pumpTimes[indexNum] = time
            self.pumpFull[ingredient]['pumpTime'] = time
            self.writePumpData()
        except Exception as e:
            print(e)
            return 'false'

        return 'true' #Success
    
    #Reverse the polarity of the motors
    def reversePolarity(self):
        if(self.polarityNormal):
            #Turn off signal for #1 relay
            GPIO.output(self.polarityPins[0], GPIO.HIGH)

            #Turn on signal for #2 relay
            GPIO.output(self.polarityPins[1], GPIO.LOW)
            self.polarityNormal = False
        else:
            #Turn on signal for #1 relay
            GPIO.output(self.polarityPins[0], GPIO.LOW)

            # Turn off signal for #2 relay
            GPIO.output(self.polarityPins[1], GPIO.HIGH)

            self.polarityNormal = True
        
        print('Done reversing polarities!')
        return self.polarityNormal


    #Cleans Pumps by flushin them for time specified in self.cleanTime
    def cleanPumps(self, removeIgnore=False):
        if(self.busy_flag and not removeIgnore):
            return 'busy'

        print('Cleaning pumps!')

        self.busy_flag = True
        for pump in self.pumps:
            GPIO.output(pump, GPIO.LOW)

        time.sleep(self.cleanTime)

        for pump in self.pumps:
            GPIO.output(pump, GPIO.HIGH)
        
        if(not removeIgnore):
            self.busy_flag = False
        
        return 'true'


    def setupButtons(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.OUT)
        GPIO.output(23, GPIO.HIGH)

        GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        while True:
            try:
                '''
                if (GPIO.input(24) == GPIO.HIGH):
                    print('This GPIO was triggered')
                    self.makeCocktail('vodka shot')
                '''
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
        newVal = round(float(self.pumpFull[ingredientName]['volume'])) - (self.shotVolume*shotAmount)
        print('New Value: ' + str(newVal))
        self.pumpFull[ingredientName]['volume'] = str(newVal)
        self.writePumpData()

    
    def canMakeCocktail(self, name):
        cocktailNum = self.cocktailNumbers[name]
        i = 0
        for ingredient in self.cocktailIngredients[cocktailNum]:
            #Check for alcohol mode
            if(self.alcoholMode and ingredient not in self.alcoholList):
                continue
            availableAmt = round(float(self.pumpFull[ingredient]['volume']))
            needAmt = round(float(self.cocktailAmounts[cocktailNum][i]))*self.shotVolume
            print('Ingredient: ' + name + '   availableAmt: ' + str(availableAmt) + '   needAmt: ' + str(needAmt))
            if((availableAmt - needAmt) < 0):
                return False
        return True

    
    #Get the ingredients of a specific cocktail from DynamoDB (CLOUD ONLY VERSION)
    def getCloudIngredients(self, name):
        response = getRecipe(name)
        recipe = {}

        #Convert Decimals back to floats
        for key in response['amounts']:
            recipe[key] = float(response['amounts'][key])

        return recipe

    def getIngredients(self, name):
        print("GETTING INGREDIENTS")
        cocktailNum = self.cocktailNumbers[name]
        recipe = {}

        i = 0
        for ingredient in self.cocktailIngredients[cocktailNum]:
            recipe[ingredient] = float(self.cocktailAmounts[cocktailNum][i])
            i += 1

        return recipe

    def getBottlePercentage(self, bottleNum):
        try:
            bottleName = self.pumpNumbers[bottleNum]
            now = self.getBottleVolume(bottleName)
            full = self.getBottleInitVolume(bottleName)
            percent = (now/full)*100
            return str(int(percent))
        except Exception as e:
            print(e)
            return 'N/A'

    #Gets the current volume of a bottle
    def getBottleVolume(self, bottleName):
        if(bottleName in self.pumpFull):
            vol = round(float(self.pumpFull[bottleName]['volume']))
            return vol
        else:
            return -1.0

    #Gets the initial volume of a bottle
    def getBottleInitVolume(self, bottleName):
        vol = round(float(self.pumpFull[bottleName]['originalVolume']))
        return vol

    def getBottleName(self, bottleNum):
        try:
            bottleName = self.pumpNumbers[bottleNum]
            print('Bottle Name: ' + bottleName)
            return bottleName
        except Exception as e:
            print(e)
            return 'N/A'


    #Enables Barbot's "alcohol mode" (only outputting ingredients that alcohol)
    def setAlcoholMode(self, modeSetting):
        self.alcoholMode = modeSetting
        self.refreshCocktailFiles()
        print("Alcohol mode: " + str(modeSetting))

    
    #Remove all bottles from pumps
    def removeAllBottles(self):

        if(self.busy_flag):
            return 'busy'

        self.busy_flag = True
        #First reverse the polarity
        self.reversePolarity()

        #Make a copy of the bottles
        totalBottles = list(self.pumpFull.keys())

        #Next remove all bottles
        for bottleName in totalBottles:
            self.removeBottle(bottleName, skipPumps=True)
        
        #Run a the clean function to turn on all pumps
        self.cleanPumps(removeIgnore=True)
        self.reversePolarity()
        self.busy_flag = False
        #Finally reverse the polarity again
        return 'true'

    #Remove bottle from pumpFull and pumpMap.json
    def removeBottle(self, bottleName, skipPumps=False):
        if(bottleName in self.pumpFull and not self.busy_flag and not skipPumps):
            self.busy_flag = True
            
            #Reverse pump polarity
            self.reversePolarity()
            
            #Turn on the designated pump
            pumpNum = self.pumpMap[bottleName]
            self.pumpOn(pumpNum)

            #Pause for a few seconds
            time.sleep(self.cleanTime)

            self.pumpOff(pumpNum)
            self.busy_flag = False
        elif(self.busy_flag and not skipPumps):
            return 'busy'
        
        #Try to remove bottleName from pumpFull array
        try:
            self.pumpFull.pop(bottleName)
        except KeyError as e:
            print(e)
            return 'false'

        self.addNewBottleToList(bottleName)
        self.refreshCocktailFiles()

        return 'true'

    #Adds bottle to pumpFull and pumpMap.json
    def addBottle(self, bottleName, pumpNum, volume, originalVolume):
        self.pumpFull[bottleName] = {}
        self.pumpFull[bottleName]['pump'] = pumpNum
        self.pumpFull[bottleName]['volume'] = volume
        self.pumpFull[bottleName]['pumpTime'] = 26
        self.pumpFull[bottleName]['originalVolume'] = originalVolume
        self.removeBottleFromList(bottleName)
        self.refreshCocktailFiles()

    def writePumpData(self):
        with open('pumpMap.json', 'w') as file:
            json.dump(self.pumpFull, file)


    def refreshCocktailFiles(self):
        self.writePumpData()
        self.loadPumpMap()
        self.loadCocktails()
        self.loadAlcoholList()
        

'''
if __name__ == '__main__':
    main = Main()
    GPIO.cleanup()
    print('Done')
'''