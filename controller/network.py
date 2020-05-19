from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from main import Main
from iotBridge import IoTManager
import threading
import time
import json
import subprocess
import requests
import traceback

#####TESTING IMPORTS#######
from recipe import getAllRecipes
############################

app = FlaskAPI(__name__)
main = Main()
iotManager = IoTManager(main)

@app.route('/cocktail/<string:name>/', strict_slashes=False, methods=['GET'])
def callMakeCocktail(name):
    res = main.makeCocktail(name)
    if(res != 'true'):
        print("Issues making cocktail: " + name + "\n" + "Response: " + str(res))
    else:
        print('Made cocktail ' + name + '\n')
    return res

@app.route('/clean/', strict_slashes=False, methods=['GET'])
def callCleanPumps():
    res = main.cleanPumps()
    return res

@app.route('/ingredients/<string:cocktail>/', strict_slashes=False, methods=['GET'])
def getIngredients(cocktail):
    res = main.getIngredients(cocktail)
    print(res)

    return res

@app.route('/bottleName/<int:num>/', strict_slashes=False, methods=['GET'])
def getBottleName(num):
    #print(main.getBottleName(num))
    return main.getBottleName(num)

@app.route('/removeBottle/<string:bottleName>/', strict_slashes=False, methods=['GET'])
def removeBottle(bottleName):
    res = main.removeBottle(bottleName)
    return res

@app.route('/removeAllBottles/', strict_slashes=False, methods=['GET'])
def removeAllBottles():
    res = main.removeAllBottles()
    return res

@app.route('/addBottle/<string:bottleName>/pump/<int:pumpNum>/volume/<string:volume>/originalVolume/<string:originalVolume>/', strict_slashes=False, methods=['GET'])
#@app.route('/addBottle/<string:bottleName>?pump=<int:pumpNum>&volume=<int:volume>&originalVolume=<int:originalVolume>/', strict_slashes=False, methods=['GET'])
def addBottle(bottleName, pumpNum, volume, originalVolume):
    try:
        main.addBottle(bottleName, pumpNum, volume, originalVolume)
        return 'true'
    except Exception as e:
        print("Failed adding bottle in app!")
        traceback.print_exc()
        return 'false'


@app.route('/newBottle/<string:bottleName>/alcohol=<string:isAlcohol>', strict_slashes=False, methods=['GET'])
def addNewBottle(bottleName, isAlcohol):
    main.addNewBottleToList(bottleName.lower())

    #Add to alcohol list if it is alcohol
    if(isAlcohol == 'true'):
        main.addToAlcoholList(bottleName.lower())

    return 'true'

@app.route('/getBottles/', strict_slashes=False, methods=['GET'])
def getNewBottles():
    return list(main.newBottles)

@app.route('/getAllBottles/', strict_slashes=False, methods=['GET'])
def getAllBottles():
    allBottles = list(main.newBottles)

    for bottle in main.pumpMap.keys():
        allBottles.append(bottle)

    return allBottles

@app.route('/heartbeat/', strict_slashes=False, methods=['GET'])
def heartbeat():
    return "online"


@app.route('/volume/<string:bottleName>/', strict_slashes=False, methods=['GET'])
def getBottleVolume(bottleName):
    vol = main.getBottleVolume(bottleName)
    if(vol == -1.0):
        return 'N/A'
    else:
        return str(vol)


@app.route('/initVolume/<string:bottleName>/', strict_slashes=False, methods=['GET'])
def getBottleInitVolume(bottleName):
    vol = main.getBottleInitVolume(bottleName)
    if(vol == -1.0):
        return 'N/A'
    else:
        return str(vol)


@app.route('/cocktailList/', strict_slashes=False, methods=['GET'])
def getCocktailList():
    availableCocktails = []
    count = 0
    for i in main.cocktailNames:
        cocktailName = main.cocktailNames[i]

        if(main.cocktailAvailable[cocktailName]):
            availableCocktails.append(cocktailName)
            count += 1
        else:
            print('Cocktail: ' + cocktailName + ' is not available!')
    return availableCocktails


@app.route('/addRecipe/', strict_slashes=False, methods=['POST'])
def addCocktailRecipe():
    return main.addCocktailRecipe(request.json)

@app.route('/alcoholMode/', strict_slashes=False, methods=['POST'])
def setAlcoholMode():
    main.setAlcoholMode(request.json['enable'])
    return 'true'

@app.route('/bottleVolumes/', strict_slashes=False, methods=['GET'])
def getAllVolumes():
    return main.pumpFull

@app.route('/bottlePercent/<int:num>/', strict_slashes=False, methods=['GET'])
def getBottlePercent(num):
    return main.getBottlePercentage(num)

@app.route('/getAlcoholMode/', strict_slashes=False, methods=['GET'])
def getAlcoholMode():
    return json.dumps(main.alcoholMode)

@app.route('/pumpOn/<int:num>/', strict_slashes=False, methods=['GET'])
def pumpOn(num):
    main.pumpOn(num)
    return "Pump on!\n"

@app.route('/pumpOff/<int:num>/', strict_slashes=False, methods=['GET'])
def pumpOff(num):
    main.pumpOff(num)
    return "Pump off!\n"

@app.route('/calibrate/<int:num>/time/<float:time>/', strict_slashes=False, methods=['GET'])
@app.route('/calibrate/<int:num>/time/<int:time>/', strict_slashes=False, methods=['GET'])
def calibratePump(num, time):
    res = main.calibratePump(num, time)
    return res

@app.route('/reverse/', strict_slashes=False, methods=['GET'])
def reversePolarity():
    polarityNormal = main.reversePolarity()
    print('polarityNormal: ' + str(polarityNormal))
    return str(polarityNormal) + '\n'

@app.route('/volume/<string:ingredient>/', strict_slashes=False, methods=['GET'])
def getIngredientVolume(ingredient):
    vol = {}
    vol['ingredient'] = ingredient
    vol['volume'] = main.pumpFull[ingredient]['volume']
    vol['originalVolume'] = main.pumpFull[ingredient]['originalVolume']
    percent = (int(vol['volume']) / int(vol['originalVolume']))*100
    vol['percent'] = round(percent)
    return vol

@app.route('/offline/', strict_slashes=False, methods=['GET'])
def goOffline():
    try:
        res = requests.get('http://barbotdisplay:5000/offline/')

        time.sleep(5)

        subprocess.call(['/home/pi/BarBotOffline/controller/goOffline'])
        print('Going offline')

    except Exception as error:
        print(error)
        print('Going offline failed')
        exit(1)

@app.route('/online/', strict_slashes=False, methods=['GET'])
def goOnline():
    #Call display's goOnline REST endpoint first
    try:
        res = requests.get('http://192.168.4.1:5000/online/')

        time.sleep(5)

        subprocess.call(['/home/pi/BarBotOffline/controller/goOnline'])
        print('Going online')

    except Exception as error:
        print('Going online failed')
        print(error)
        exit(1)

def startAPI():
    app.run(debug=False, host='0.0.0.0')


if __name__ == "__main__":
    apiThread = threading.Thread(target=startAPI)
    apiThread.daemon = True
    apiThread.start()
    #This will be where we will instantiate the controller from
    while True:
        try:
            pass
        except KeyboardInterrupt:
            break
    print('Exitting...')