from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient, AWSIoTMQTTClient
import time
import json
from os import path

#Class manages interfacing with AWS IoT Core
class IoTManager():

    #Initializes device details and creates IoT Core MQTT connection
    def __init__(self, main):
        self.main = main
        self.iot_details = {}
        self.thing_name = 'BarBot'
        self.disabled = False #TODO: load this from the settings file

        if not path.exists('./certs/iotDetails.json'):
            self.disabled = True
            print('IoT files don\'t exist')
            return
        
        #Load AWS IoT Core details from json file
        with open('./certs/iotDetails.json', 'r') as file:
            self.iot_details = json.load(file)

        self.mqtt_client = AWSIoTMQTTClient('barbot')
        self.mqtt_client.configureEndpoint(self.iot_details['endpoint'], 8883)
        self.mqtt_client.configureCredentials('./certs/root-CA.crt', './certs/BarBot.private.key', './certs/BarBot.cert.pem')

        self.mqtt_client.configureOfflinePublishQueueing(0)
        self.mqtt_client.configureDrainingFrequency(2)
        self.mqtt_client.configureConnectDisconnectTimeout(15)
        self.mqtt_client.configureMQTTOperationTimeout(5)

        try:
            self.mqtt_client.connect()
            self.mqtt_client.subscribe('barbot-main', 1, self.parse_message)
            print('Connected to AWS IoT Core!')

            #Setup Shadow handler
            self.shadow_client = AWSIoTMQTTShadowClient('barbot-shadow')
            self.shadow_client.configureEndpoint(self.iot_details['endpoint'], 8883)
            self.shadow_client.configureCredentials('./certs/root-CA.crt', './certs/BarBot.private.key', './certs/BarBot.cert.pem')
            self.shadow_client.configureAutoReconnectBackoffTime(1, 32, 20)
            self.shadow_client.configureConnectDisconnectTimeout(10)
            self.shadow_client.configureMQTTOperationTimeout(5)

            self.shadow_client.connect()
            print("Connected to BarBot's IoT Shadow")

            self.shadow_handler = self.shadow_client.createShadowHandlerWithName(self.thing_name, True)
        except Exception as e:
            print(e)
            self.disabled = True

    #Parses incoming message from MQTT topic and routes to proper function
    def parse_message(self, client, userdata, message):
        if(self.disabled):
            return
        real_message = json.loads(message.payload)
        action = real_message['action']
        print('Received MQTT message with action: ' + str(action))
        if('data' in real_message):
            data = real_message['data']

        if(action == 'makeCocktail'):
            self.main.make_cocktail(data.lower())
        elif(action == 'alcoholMode'):
            if(data == True or data == False):
                self.main.set_alcohol_mode(data)
            else:
                print('Not a valid alcoholMode setting!')
        elif(action == 'getMenu'):
            cocktail_array = self.main.get_cocktail_list()
            ret_package = {
                'state': {
                    'desired': {
                        'menu': cocktail_array
                    }
                }
            }
            
            #Update the shadow
            self.update_shadow(ret_package)
        elif(action == 'message'):
            print(data)
        elif(action == 'pumpOn'):
            self.main.pump_on(int(data))
        elif(action == 'pumpOff'):
            self.main.pump_off(int(data))

    #Updates BarBot's IoT shadow    
    def update_shadow(self, json_data):
        if(self.disabled):
            return
        self.shadow_handler.shadowUpdate(json.dumps(json_data), self.update_callback, 5)

    #Callback function for BarBot's IoT
    def update_callback(self, payload, response_status, token):
        if(self.disabled):
            return
        if(response_status == 'timeout'):
            print('There was a timeout updating the shadow')
        elif(response_status == 'accepted'):
            print("Successfully updated barbot's shadow")
        elif(response_status == 'rejected'):
            print("Shadow update was rejected")
            print(payload)

    #Send a message to response MQTT topic
    def send_response(self, data):
        self.mqtt_client.publish('barbot-response', json.dumps(data), 0)