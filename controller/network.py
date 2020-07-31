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
import RPi.GPIO as GPIO

app = FlaskAPI(__name__) #Create REST API object
main = Main() #Starts the primary initalization of BarBot
iot_manager = IoTManager(main) #Start AWS IoT Manage (TODO: Enable or disable this in settings)

#Makes a specific cocktail
@app.route('/cocktail/<string:name>/', strict_slashes=False, methods=['GET'])
def call_make_cocktail(name):
    res = main.make_cocktail(name)
    if(res != 'true'):
        print("Issues making cocktail: " + name + "\n" + "Response: " + str(res))
    else:
        print('Made cocktail ' + name + '\n')
    return res

#Starts the clean function
@app.route('/clean/', strict_slashes=False, methods=['GET'])
def call_clean_pumps():
    res = main.clean_pumps(remove_ignore=True)
    return res

#Returns the ingredients in a specific cocktail
@app.route('/ingredients/<string:cocktail>/', strict_slashes=False, methods=['GET'])
def get_ingredients(cocktail):
    res = main.get_ingredients(cocktail)
    print(res)

    return res

#Returns the bottle name for a specific pump number
@app.route('/bottleName/<int:num>/', strict_slashes=False, methods=['GET'])
def get_bottle_name(num):
    return main.get_bottle_name(num)

#Gets number of bottles that the barbot supports
@app.route('/pumpSupportDetails/', strict_slashes=False, methods=['GET'])
def get_pump_support_details():
    return main.get_pump_support_details()

#Removes a specific bottle from its pump
@app.route('/removeBottle/<string:bottle_name>/', strict_slashes=False, methods=['GET'])
def remove_bottle(bottle_name):
    res = main.remove_bottle(bottle_name)
    return res

#Removes all bottles from their pumps
@app.route('/removeAllBottles/', strict_slashes=False, methods=['GET'])
def remove_all_bottles():
    res = main.remove_all_bottles()
    return res

#Adds a new bottle to a specific pump (TODO: CHANGE THIS TO A POST METHOD)
@app.route('/addBottle/<string:bottle_name>/pump/<int:pump_num>/volume/<string:volume>/originalVolume/<string:original_volume>/', strict_slashes=False, methods=['GET'])
#@app.route('/addBottle/<string:bottleName>?pump=<int:pumpNum>&volume=<int:volume>&originalVolume=<int:originalVolume>/', strict_slashes=False, methods=['GET'])
def add_bottle(bottle_name, pump_num, volume, original_volume):
    try:
        main.add_bottle(bottle_name, pump_num, volume, original_volume)
        return 'true'
    except Exception as e:
        print("Failed adding bottle in app!")
        traceback.print_exc()
        return 'false'


#Adds a new bottle to the list of available bottles (not to a pump)
@app.route('/newBottle/<string:bottle_name>/alcohol=<string:is_alcohol>', strict_slashes=False, methods=['GET'])
def add_new_bottle(bottle_name, is_alcohol):
    main.add_new_bottle_to_list(bottle_name.lower())

    #Add to alcohol list if it is alcohol
    if(is_alcohol == 'true'):
        main.add_to_alcohol_list(bottle_name.lower())

    return 'true'

#Get the list of bottles available to be added to pumps
@app.route('/getBottles/', strict_slashes=False, methods=['GET'])
def get_new_bottles():
    return list(main.new_bottles)

#Get all bottles including those already on pumps (TODO: Move this processing to the main class)
@app.route('/getAllBottles/', strict_slashes=False, methods=['GET'])
def get_all_bottles():
    all_bottles = list(main.new_bottles)

    for bottle in main.pump_map.keys():
        all_bottles.append(bottle)

    return all_bottles

#Simple heartbeat poll to check for connection
@app.route('/heartbeat/', strict_slashes=False, methods=['GET'])
def heartbeat():
    return "online"

#Returns the current volume a specific bottle
@app.route('/volume/<string:bottle_name>/', strict_slashes=False, methods=['GET'])
def get_bottle_volume(bottle_name):
    vol = main.get_bottle_volume(bottle_name)
    if(vol == -1.0):
        return 'N/A'
    else:
        return str(vol)

#Gets the initial volume of a bottle
@app.route('/initVolume/<string:bottle_name>/', strict_slashes=False, methods=['GET'])
def get_bottle_init_volume(bottle_name):
    vol = main.get_bottle_init_volume(bottle_name)
    if(vol == -1.0):
        return 'N/A'
    else:
        return str(vol)

#Gets the list of available cocktails
@app.route('/cocktailList/', strict_slashes=False, methods=['GET'])
def get_cocktail_list():
    available_cocktails = main.get_cocktail_list()

    iot_obj = {
        'state': {
            'desired': {
                'menu': available_cocktails
            }
        }
    }

    #Update menu in device shadow
    shadow_thread = threading.Thread(target=iot_manager.update_shadow, args=[iot_obj])
    shadow_thread.daemon = True
    shadow_thread.start()
    #iotManager.update_shadow(iotObj)

    return available_cocktails

#Adds a cocktail recipe to local cache and Dynamo
@app.route('/addRecipe/', strict_slashes=False, methods=['POST'])
def add_cocktail_recipe():
    return main.add_cocktail_recipe(request.json)

#Disables or enables alcohol mode
@app.route('/alcoholMode/', strict_slashes=False, methods=['POST'])
def set_alcohol_mode():
    main.set_alcohol_mode(request.json['enable'])
    return 'true'

#Gets the current percentage full for a bottle
@app.route('/bottlePercent/<string:name>/', strict_slashes=False, methods=['GET'])
def get_bottle_percent(name):
    return main.get_bottle_percentage(name)

#Gets the current state of alcohol mode
@app.route('/getAlcoholMode/', strict_slashes=False, methods=['GET'])
def get_alcohol_mode():
    return json.dumps(main.alcohol_mode)

#Turns on a specific pump number
@app.route('/pumpOn/<int:num>/', strict_slashes=False, methods=['GET'])
def pump_on(num):
    main.pump_on(num)
    return "Pump on!\n"

#Turns off a specific pump number
@app.route('/pumpOff/<int:num>/', strict_slashes=False, methods=['GET'])
def pump_off(num):
    main.pump_off(num)
    return "Pump off!\n"

#Turns on a particular air pressure pump (number is same as associated solenoid)
@app.route('/pressureOn/<int:num>/', strict_slashes=False, methods=['GET'])
def pressure_on(num):
    main.pressure_on(num)
    return 'true'

#Turns off a particular air pressure pump (number is same as associated solenoid)
@app.route('/pressureOff/<int:num>/', strict_slashes=False, methods=['GET'])
def pressure_off(num):
    main.pressure_off(num)
    return 'true'

#Calibrates a specific pump to the provided time for a 1.5 fl oz shot pour
@app.route('/calibrate/<int:num>/time/<float:time>/', strict_slashes=False, methods=['GET'])
@app.route('/calibrate/<int:num>/time/<int:time>/', strict_slashes=False, methods=['GET'])
def calibrate_pump(num, time):
    res = main.calibrate_pump(num, time)
    return res

#Reverses the polarity on the peristaltic pumps
@app.route('/reverse/', strict_slashes=False, methods=['GET'])
def reverse_polarity():
    polarity_normal = main.reverse_polarity()
    print('polarityNormal: ' + str(polarity_normal))
    return str(polarity_normal) + '\n'

#Gets full volume object for an ingredient
@app.route('/volume/<string:ingredient>/', strict_slashes=False, methods=['GET'])
def get_ingredient_volume(ingredient):
    vol = main.get_ingredient_volume(ingredient)
    return vol

#Refreshes all local caches
@app.route('/refreshRecipes/', strict_slashes=False, methods=['GET'])
def refresh_recipes():
    res = main.refresh_cocktail_files()
    return res

#Adds or removes a specific ingredient from the "ignore list"
@app.route('/ignoreIngredient/', strict_slashes=False, methods=['POST'])
def ignore_ingredient():
    #param check
    if('action' not in request.json or 'ingredient' not in request.json):
        print('Error ignoring ingredient')
        return 'false'

    action = request.json['action'] #Add or remove
    item = request.json['ingredient']  #Name of ingredient

    if(action == 'add'):
        #Add item
        main.add_ignore_item(item)
    elif(action == 'remove'):
        #Remove item
        main.remove_ignore_item(item)
    else:
        #Unknown action error
        print('Error ignoring ingredient')
        return 'false'
    
    return 'true'


#Get the list of ingredients that are ignored for menu purposes
@app.route('/getIgnoreIngredients/', strict_slashes=False, methods=['GET'])
def get_ignore_ingredients():
    res = main.get_ignore_ingredients()

    return res

#Tells BarBot to fetch and install updates
@app.route('/update/', strict_slashes=False, methods=['GET'])
def update():
    main.update()
    return 'true'

#Triggers BarBot reset
@app.route('/reboot/', strict_slashes=False, methods=['GET'])
def reboot():
    main.reboot()
    return 'true'

#Start the REST API
def start_API():
    app.run(debug=False, host='0.0.0.0')

#Starts the api thread and keeps an infinite loop that can be broken with Ctrl-C
if __name__ == "__main__":
    api_thread = threading.Thread(target=start_API)
    api_thread.daemon = True
    api_thread.start()

    while True:
        try:
            pass
        except KeyboardInterrupt:
            GPIO.cleanup()
            break
    print('Exitting...')