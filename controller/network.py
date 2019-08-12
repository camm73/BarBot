from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from main import Main
import threading
import time

app = FlaskAPI(__name__)
main = Main()

@app.route('/<string:name>/', methods=['GET'])
def callMakeCocktail(name):
    res = main.makeCocktail(name)
    if(res == False):
        return "Issues making cocktail: " + name + "\n"
    return 'Making cocktail ' + name + '\n'

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
    pass

@app.route('/online/', methods=['GET'])
def goOnline():
    pass

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