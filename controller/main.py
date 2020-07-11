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
        #[26, 19, 13, 6, 5, 21, 20, 16] GPIOS FOR PUMPS
        self.polarityPins = [17, 27] #Pin 17 is #1 and Pin #27 is #2
        self.polarityNormal = True
        self.cocktailIngredients = {}
        self.cocktailAmounts = {}
        self.cocktailButtons = {}
        self.cocktailAvailable = {}
        self.ignoreList = set()
        self.alcoholList = set()
        self.alcoholMode = False
        self.newBottles = set()
        self.pumpMap = {}
        self.pumpData = {}
        self.cocktailCount = 0
        self.cleanTime = 8  #Regular Time: 12 seconds
        self.shotVolume = 44 #mL
        self.busy_flag = False
        self.window = None

        self.loadPumpConfig() #Load configuration of pumpMap and pumpData
        self.setupPins()
        self.loadNewBottles()
        self.loadAlcoholList()
        self.loadIgnoreList()
        self.updateLocalRecipes() #Updates local recipes to match cloud; loads recipes locally; checks cocktail availablity


    #Sets up pins by setting gpio mode and setting initial output
    def setupPins(self):
        try:
            print("Setting up pump pins...")
            GPIO.setmode(GPIO.BCM)
            for pump in self.pumpData:

                GPIO.setup(self.pumpData[pump]['gpio'], GPIO.OUT)
                GPIO.output(self.pumpData[pump]['gpio'], GPIO.HIGH)

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


    #Load pump configuration
    def loadPumpConfig(self):
        data = []
        with open('pumpConfig.json', 'r') as file:
            data = json.load(file)

        for pump in data:
            self.pumpData[pump['pumpNum']] = {
                "pumpNum": pump['pumpNum'],
                "gpio": pump['gpio'],
                "type": pump['type'],
                "pumpTime": pump['pumpTime']
            }

            #Make sure there is a bottle on the pump
            if(pump['currentBottle'] != {}):
                self.pumpMap[pump['currentBottle']['name']] = {
                    "name": pump['currentBottle']['name'],
                    "volume": pump['currentBottle']['volume'],
                    "originalVolume": pump['currentBottle']['originalVolume'],
                    "pumpNum": pump['pumpNum'] #Should be removed before writing back to file
                }


    #Test function that runs all of the pumps for 3 seconds each
    def testPumps(self):
        try:
            for pump in self.pumpData:
                GPIO.output(self.pumpData[pump]['gpio'], GPIO.LOW)
                print("Turning on pin " + str(pump['gpio']))
                time.sleep(3)
                GPIO.output(self.pumpData[pump]['gpio'], GPIO.HIGH)
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
            cocktailName = str(data['cocktails'][i]['name'])
            self.cocktailIngredients[cocktailName] = data['cocktails'][i]['ingredients']
            self.cocktailAmounts[cocktailName] = data['cocktails'][i]['amounts']
            self.cocktailAvailable[cocktailName] = self.isAvailable(cocktailName)
            print(cocktailName + " available: " + str(self.cocktailAvailable[cocktailName]))
            i = i+1
        self.cocktailCount = i


    #Loads the list of ingredients to ignore when considering availablity & making cocktail
    def loadIgnoreList(self):
        data = None

        with open('ignoreList.json', 'r') as file:
            data = json.load(file)
        
        self.ignoreList = set(data)


    #Write ignore list to file
    def writeIgnoreList(self):
        ignoreArr = list(self.ignoreList)

        with open('ignoreList.json', 'w') as file:
            json.dump(ignoreArr, file)

        print('Updated ignore list file')


    #Loads the list of ingredients that are alcohol
    def loadAlcoholList(self):
        data = {}

        with open('alcohol.json', 'r') as file:
            data = json.load(file)
        
        for key in data:
            if(data[key] == True):
                self.alcoholList.add(key)

    #Adds item to ignore list
    def addIgnoreItem(self, item):
        print('Adding: ' + item + ' to ignore list!')
        self.ignoreList.add(item)
        self.writeIgnoreList() #Update local storage
        self.loadCocktails()  #Reload cocktails with new ignored ingredients

    #Removes item from ignore list
    def removeIgnoreItem(self, item):
        if(item in self.ignoreList):
            print('Removing ' + item + ' from ignore list!')
            self.ignoreList.remove(item)
            self.writeIgnoreList()  #Updates local storage file
            self.loadCocktails()  #Reload cocktail list

    #Get ignore ingredient list
    def getIgnoreIngredients(self):
        return list(self.ignoreList)

    
    #Writes alcohol list to file
    def writeAlcoholList(self):

        data = {}

        allBottles = self.newBottles

        #Add bottles that are currently on pumps
        for bottle in self.pumpMap.keys():
            allBottles.add(bottle)

        #Go through all ingredients and construct object
        for ingredient in allBottles:
            #print(ingredient + ": " + str(ingredient in self.alcoholList))
            if(ingredient in self.alcoholList):
                data[ingredient] = True
            else:
                data[ingredient] = False

        with open('alcohol.json', 'w') as file:
            json.dump(data, file)

        print('Updated alcohol list file')

    
    #Add a bottle to alcohol list
    def addToAlcoholList(self, bottleName):
        self.alcoholList.add(bottleName)
        self.writeAlcoholList()

    #Get number/details of bottles supported by Barbot
    def getPumpSupportDetails(self):
        pumpArr = []

        #Get details of every pump
        for num in self.pumpData:
            pumpObj = {
                "pumpNum": num,
                "pumpTime": self.pumpData[num]['pumpTime'],
                "type": self.pumpData[num]['type']
            }
            pumpArr.append(pumpObj)

        pumpArr.sort(key= lambda e: e['pumpNum'])

        return pumpArr    
    
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
            self.loadCocktails()
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
        if(not self.alcoholMode):
            for ingredient in self.cocktailIngredients[cocktailName]:
                if(ingredient not in self.pumpMap.keys() and ingredient not in self.ignoreList):
                    print(ingredient + " not available!")
                    return False
                elif(ingredient in self.ignoreList):
                    print("CAN IGNORE INGREDIENT: " + ingredient + '  FOR COCKTAIL: ' + cocktailName)
            return True
        else:
            for ingredient in self.cocktailIngredients[cocktailName]:
                if(ingredient in self.alcoholList):
                    if(ingredient not in self.pumpMap.keys() and ingredient not in self.ignoreList):
                        print(ingredient + " not available!")
                        return False
            return True

    
    #Load new bottles
    def loadNewBottles(self):
        with open('bottles.json', 'r') as file:
            data = json.load(file)

        self.newBottles = set(data)
        print('NEW BOTTLES:')
        print(self.newBottles)


    #Write bottles list to the bottles.json file
    def writeNewBottles(self):
        with open('bottles.json', 'w') as file:
            json.dump(list(self.newBottles), file)

    
    #Adds new bottle to the bottle list
    def addNewBottleToList(self, bottleName):
        print("ADDING " + bottleName + " TO BOTTLE LIST")
        if(bottleName.lower() not in self.newBottles):
            self.newBottles.add(bottleName.lower())
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
            print('Busy making cocktail!')
            return 'busy'
        
        #Check whether the cocktail is available or not
        if(not self.cocktailAvailable[cocktailName]):
            print('This cocktail is not avialable!')
            return 'available'
        
        #Check whether there are enough ingredients
        if(not self.canMakeCocktail(cocktailName)):
            print('Not enough ingredients to make this cocktail.')
            return 'ingredients'
        
        try:
            print('Making cocktail ' + cocktailName)
            self.busy_flag = True
            self.setupPins()

            #Now we need to turn on pumps for respective ingredients for specified times
            i = 0
            waitTime = 0
            biggestTime = 0
            for ingredient in self.cocktailIngredients[cocktailName]:
                #Skip pumping non-alcohol ingredients
                if(self.alcoholMode and ingredient not in self.alcoholList):
                    print(ingredient + ' is not alcohol. Skipping to next ingredient...')
                    continue

                if(ingredient in self.ignoreList):
                    print(ingredient + ' is in ignore list. Skipping to next ingredient...')
                    continue

                print('Starting pump for ingredient: ' + ingredient)
                #Create threads to handle running the pumps
                pumpThread = threading.Thread(target=self.pumpToggle, args=[self.pumpMap[ingredient]['pumpNum'], self.cocktailAmounts[cocktailName][i]])
                pumpThread.start()

                #Adjust volume tracking for each of the pumps
                print('Ingredient: ' + str(ingredient))
                self.adjustVolumeData(ingredient, self.cocktailAmounts[cocktailName][i])

                if(self.cocktailAmounts[cocktailName][i] > biggestTime):
                    biggestTime = (self.cocktailAmounts[cocktailName][i]) * self.pumpData[self.pumpMap[ingredient]['pumpNum']]['pumpTime']
                i += 1
            
            waitTime = biggestTime
            print('Wait Time: ' + str(waitTime))
            time.sleep(waitTime + 2)
            self.busy_flag = False
            print("Done making cocktail!")

            #Update Stat tracking in the cloud
            incrementCocktail(cocktailName)

        except Exception as e:
            print(e)
            self.busy_flag = False
            return 'error'
        return 'true'

    #Toggles specific pumps for specific amount of time
    def pumpToggle(self, num, amt):
        pumpPin = self.pumpData[num]['gpio']
        GPIO.output(pumpPin, GPIO.LOW)
        time.sleep(self.pumpData[num]['pumpTime']*amt)
        GPIO.output(pumpPin, GPIO.HIGH)

    #Turns on a specific pump for indefinite amount of time
    def pumpOn(self, num):
        pumpPin = self.pumpData[num]['gpio']
        print('Turning on pump: ' + str(num))
        GPIO.output(pumpPin, GPIO.LOW)

    #Turns off a specific pump for indefinite amount of time
    def pumpOff(self, num):
        pumpPin = self.pumpData[num]['gpio']
        print("Turning off pump: " + str(num))
        GPIO.output(pumpPin, GPIO.HIGH)

    
    #Calibrates a specific pump by setting it's specific pumping time
    def calibratePump(self, pumpNum, time):
        try:
            self.pumpData[pumpNum]['pumpTime'] = time
            self.writePumpData()
        except Exception as e:
            print('ERROR: CALIBRATING PUMP FAILED')
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

        if(not removeIgnore):
            self.busy_flag = True

        for pump in self.pumpData:
            if(removeIgnore and self.pumpData[pump]['type'] == 'regular'):
                GPIO.output(self.pumpData[pump]['gpio'], GPIO.LOW)
            elif(not removeIgnore):
                GPIO.output(self.pumpData[pump]['gpio'], GPIO.LOW)

        time.sleep(self.cleanTime)

        for pump in self.pumpData:
            if(removeIgnore and self.pumpData[pump]['type'] == 'regular'):
                GPIO.output(self.pumpData[pump]['gpio'], GPIO.HIGH)
            elif(not removeIgnore):
                GPIO.output(self.pumpData[pump]['gpio'], GPIO.HIGH)
        
        if(not removeIgnore):
            self.busy_flag = False
        
        return 'true'


    def adjustVolumeData(self, ingredientName, shotAmount):
        print('Value: ' + str(self.pumpMap[ingredientName]['volume']))
        newVal = round(float(self.pumpMap[ingredientName]['volume'])) - (self.shotVolume*shotAmount)
        print('New Value: ' + str(newVal))
        self.pumpMap[ingredientName]['volume'] = str(newVal)
        self.writePumpData()


    #Assemble ingredient info packet for mobile app
    def getIngredientVolume(self, ingredient):
        volObj = {}
        volObj['ingredient'] = ingredient
        volObj['volume'] = self.pumpMap[ingredient]['volume']
        volObj['originalVolume'] = self.pumpMap[ingredient]['originalVolume']
        percent = (int(volObj['volume']) / int(volObj['originalVolume']))*100
        volObj['percent'] = round(percent)

        return volObj

    
    def canMakeCocktail(self, name):
        i = 0
        for ingredient in self.cocktailIngredients[name]:
            #Check for alcohol mode
            if(self.alcoholMode and ingredient not in self.alcoholList):
                continue
            #Check for ignore list
            if(ingredient in self.ignoreList):
                continue

            availableAmt = round(float(self.pumpMap[ingredient]['volume']))
            needAmt = round(float(self.cocktailAmounts[name][i]))*self.shotVolume
            print('Ingredient: ' + ingredient + '   availableAmt: ' + str(availableAmt) + '   needAmt: ' + str(needAmt))
            if((availableAmt - needAmt) < 0):
                return False
        return True


    #Get the cocktail list from available ingredients
    def getCocktailList(self):
        availableCocktails = []
        count = 0
        for cocktailName in self.cocktailIngredients.keys():

            if(self.cocktailAvailable[cocktailName]):
                availableCocktails.append(cocktailName)
                count += 1
            else:
                print('Cocktail: ' + cocktailName + ' is not available!')

        return availableCocktails

    
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
        recipe = {}

        i = 0
        for ingredient in self.cocktailIngredients[name]:
            recipe[ingredient] = float(self.cocktailAmounts[name][i])
            i += 1

        return recipe

    def getBottlePercentage(self, bottleName):
        try:
            now = self.getBottleVolume(bottleName)
            full = self.getBottleInitVolume(bottleName)
            if(now == -1 or full == -1):
                return 'N/A'
            percent = (now/full)*100
            return str(int(percent))
        except Exception as e:
            print('Error getting bottle percentage!')
            print(e)
            return 'N/A'

    #Gets the current volume of a bottle
    def getBottleVolume(self, bottleName):
        if(bottleName in self.pumpMap):
            vol = round(float(self.pumpMap[bottleName]['volume']))
            return vol
        else:
            return -1

    #Gets the initial volume of a bottle
    def getBottleInitVolume(self, bottleName):
        if(bottleName in self.pumpMap):
            vol = round(float(self.pumpMap[bottleName]['originalVolume']))
            return vol
        else:
            return -1

    def getBottleName(self, bottleNum):
        try:

            #TODO: Make this more efficient; maybe have a hashmap
            for ingredient in self.pumpMap:
                if(self.pumpMap[ingredient]['pumpNum'] == bottleNum):
                    bottleName = ingredient
                    return bottleName
            return 'N/A'
        except Exception as e:
            print('Error getting bottle name!')
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
        
        try:
            self.busy_flag = True
            #First reverse the polarity
            self.reversePolarity()

            #Make a copy of the bottles
            totalBottles = list(self.pumpMap.keys())

            #Next remove all bottles
            for bottleName in totalBottles:
                self.removeBottle(bottleName, skipPumps=True)
            
            #Refresh files after removing all bottles
            self.refreshCocktailFiles()
            
            #Run a the clean function to turn on all pumps
            self.cleanPumps(removeIgnore=True)
            
            #Finally reverse the polarity again
            self.reversePolarity()
            self.busy_flag = False
        except Exception as e:
            print(e)
            return 'error'
        return 'true'

    #Remove bottle from pumpMap
    def removeBottle(self, bottleName, skipPumps=False):
        pumpNum = self.pumpMap[bottleName]['pumpNum']
        
        #Skip pumping if not a regular pump
        if(self.pumpData[pumpNum]['type'] != 'regular'):
            skipPumps = True

        if(bottleName in self.pumpMap and not self.busy_flag and not skipPumps):
            self.busy_flag = True
            
            #Reverse pump polarity
            self.reversePolarity()
            
            #Turn on the designated pump
            self.pumpOn(pumpNum)

            #Pause for a few seconds
            time.sleep(self.cleanTime)

            self.pumpOff(pumpNum)

            self.reversePolarity()
            self.busy_flag = False
        elif(self.busy_flag and not skipPumps):
            return 'busy'
        
        #Try to remove bottleName from pumpMap
        try:
            self.pumpMap.pop(bottleName)
        except KeyError as e:
            print('Error removing bottle')
            print(e)
            return 'false'

        self.addNewBottleToList(bottleName)

        #Don't want to refresh too many times
        if(not skipPumps):
            self.refreshCocktailFiles()

        return 'true'

    #Adds bottle to pumpMap
    def addBottle(self, bottleName, pumpNum, volume, originalVolume):
        self.pumpMap[bottleName] = {}
        self.pumpMap[bottleName]['name'] = bottleName
        self.pumpMap[bottleName]['pumpNum'] = pumpNum
        self.pumpMap[bottleName]['volume'] = volume
        self.pumpMap[bottleName]['originalVolume'] = originalVolume
        self.removeBottleFromList(bottleName)
        self.refreshCocktailFiles()

    def writePumpData(self):
        mainArr = []
        pumpsDone = set()

        for ingredient in self.pumpMap:
            pumpNum = self.pumpMap[ingredient]['pumpNum']
            dataObj = self.pumpData[pumpNum].copy()
            mapObj = self.pumpMap[ingredient].copy()
            mapObj.pop('pumpNum')
            dataObj['currentBottle'] = mapObj
            pumpsDone.add(pumpNum)

            mainArr.append(dataObj)

        #Add pumps that aren't in pumpMap already (i.e. no bottle connected)
        for pump in self.pumpData:
            if(pump in pumpsDone):
                continue
            
            dataObj = self.pumpData[pump]
            mapObj = {}
            dataObj['currentBottle'] = mapObj
            pumpsDone.add(pump)

            mainArr.append(dataObj)
        
        with open('pumpConfig.json', 'w') as file:
            json.dump(mainArr, file)

        print('Wrote pump config to file')


    def refreshCocktailFiles(self):
        try:
            print("Refreshing cocktail files...")
            self.writePumpData()
            self.loadPumpConfig()
            self.updateLocalRecipes()
            self.loadCocktails()
            self.loadAlcoholList()
            self.loadIgnoreList()
        except Exception as e:
            print(e)
            return 'error'
        return 'true'
        

'''
if __name__ == '__main__':
    main = Main()
    GPIO.cleanup()
    print('Done')
'''