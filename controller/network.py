from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from main import Main
import threading
import time

app = FlaskAPI(__name__)
main = Main()

@app.route('/<string:name>/', methods=['GET'])
def callMakeCocktail(name):
    main.makeCocktail(main.cocktailNumbers[name])
    return 'Making cocktail ' + name + '\n'

def startAPI():
    app.run(debug=False)

@app.route('/test', methods=['GET'])
def test():
    main.makeCocktail(2)
    return "Pouring shot"

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