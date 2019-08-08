from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from main import Main
import threading

app = FlaskAPI(__name__)

@app.route('/makeCocktail?<string:name>/', methods=['POST'])
def callMakeCocktail(name):
    pass

def startAPI():
    app.run(debug=False)

if __name__ == "__main__":
    apiThread = threading.Thread(target=startAPI)
    apiThread.daemon = True
    apiThread.start()
    #This will be where we will instantiate the controller from
    main = Main()
    print('Exitting!')
