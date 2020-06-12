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
    availableCocktails = main.getCocktailList()
    print("GETTING COCKTAIL LIST")

    iotObj = {
        'state': {
            'desired': {
                'menu': availableCocktails
            }
        }
    }

    #Update menu in device shadow
    shadow_thread = threading.Thread(target=iotManager.update_shadow, args=[iotObj])
    shadow_thread.daemon = True
    shadow_thread.start()
    #iotManager.update_shadow(iotObj)

    return availableCocktails


@app.route('/addRecipe/', strict_slashes=False, methods=['POST'])
def addCocktailRecipe():
    return main.addCocktailRecipe(request.json)

@app.route('/alcoholMode/', strict_slashes=False, methods=['POST'])
def setAlcoholMode():
    main.setAlcoholMode(request.json['enable'])
    return 'true'

@app.route('/bottlePercent/<string:name>/', strict_slashes=False, methods=['GET'])
def getBottlePercent(name):
    return main.getBottlePercentage(name)

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

#TODO Move this into a method inside main.py
@app.route('/volume/<string:ingredient>/', strict_slashes=False, methods=['GET'])
def getIngredientVolume(ingredient):
    vol = main.getIngredientVolume(ingredient)
    return vol


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