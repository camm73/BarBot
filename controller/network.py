from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from main import Main
import threading
import time
import subprocess
import requests

app = FlaskAPI(__name__)
main = Main()

host = 'http://barbotdisplay:5000'

@app.route('/<string:name>/', methods=['GET'])
def callMakeCocktail(name):
    res = main.makeCocktail(name)
    if(res == False):
        return "Issues making cocktail: " + name + "\n"
    return 'Making cocktail ' + name + '\n'

@app.route('/clean/', methods=['GET'])
def callCleanPumps():
    main.cleanPumps()
    
    return "Cleaning pumps!"

@app.route('/cocktailList/', methods=['GET'])
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

@app.route('/bottleVolumes/', methods=['GET'])
def getAllVolumes():
    return main.pumpFull

@app.route('/volume/<string:ingredient>/', methods=['GET'])
def getIngredientVolume(ingredient):
    vol = {}
    vol['ingredient'] = ingredient
    vol['volume'] = main.pumpFull[ingredient]['volume']
    vol['originalVolume'] = main.pumpFull[ingredient]['originalVolume']
    percent = (int(vol['volume']) / int(vol['originalVolume']))*100
    vol['percent'] = round(percent)
    return vol

@app.route('/offline/', methods=['GET'])
def goOffline():
    try:
        res = requests.get(host + '/offline/')

        time.sleep(5)

        subprocess.call(['./goOffline'])
        print('Going offline')

    except Exception as error:
        print(error)
        print('Going offline failed')
        exit(1)

@app.route('/online/', methods=['GET'])
def goOnline():
    #Call display's goOnline REST endpoint first
    try:
        res = requests.get(host + '/online/')

        time.sleep(5)

        subprocess.call(['./goOnline'])
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