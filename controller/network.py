from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions

app = FlaskAPI(__name__)

@app.route('/makeCocktail?<string:name>/', methods=['POST'])
def callMakeCocktail(name):
    pass

if __name__ == "__main__":
    app.run(debug=True)