from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from main import Main
import threading
import time

app = FlaskAPI(__name__)
main = Main()

@app.route('/<string:name>/', methods=['GET'])
def callMakeCocktail(name):
    res = main.makeCocktail(main.cocktailNumbers[name])
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


def startAPI():
    app.run(debug=False)


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