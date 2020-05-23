from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient, AWSIoTMQTTClient
import time
import json

class IoTManager():

    def __init__(self, main):
        self.main = main
        self.iotDetails = {}
        self.thingName = 'BarBot'
        
        #Load AWS IoT Core details from json file
        with open('./certs/iotDetails.json', 'r') as file:
            self.iotDetails = json.load(file)

        self.mqttClient = AWSIoTMQTTClient('barbot')
        self.mqttClient.configureEndpoint(self.iotDetails['endpoint'], 8883)
        self.mqttClient.configureCredentials('./certs/root-CA.crt', './certs/BarBot.private.key', './certs/BarBot.cert.pem')

        self.mqttClient.configureOfflinePublishQueueing(0)
        self.mqttClient.configureDrainingFrequency(2)
        self.mqttClient.configureConnectDisconnectTimeout(15)
        self.mqttClient.configureMQTTOperationTimeout(5)

        self.mqttClient.connect()
        self.mqttClient.subscribe('barbot-main', 1, self.parse_message)
        print('Connected to AWS IoT Core!')

        #Setup Shadow handler
        self.shadow_client = AWSIoTMQTTShadowClient('barbot-shadow')
        self.shadow_client.configureEndpoint(self.iotDetails['endpoint'], 8883)
        self.shadow_client.configureCredentials('./certs/root-CA.crt', './certs/BarBot.private.key', './certs/BarBot.cert.pem')
        self.shadow_client.configureAutoReconnectBackoffTime(1, 32, 20)
        self.shadow_client.configureConnectDisconnectTimeout(10)
        self.shadow_client.configureMQTTOperationTimeout(5)

        self.shadow_client.connect()
        print("Connected to BarBot's IoT Shadow")

        self.shadow_handler = self.shadow_client.createShadowHandlerWithName(self.thingName, True)

    def parse_message(self, client, userdata, message):
        real_message = json.loads(message.payload)
        action = real_message['action']
        data = real_message['data']

        if(action == 'makeCocktail'):
            self.main.makeCocktail(data.lower())
        elif(action == 'alcoholMode'):
            if(data == True or data == False):
                main.alcoholMode = data
            else:
                print('Not a valid alcoholMode setting!')
        elif(action == 'getMenu'):
            cocktailArray = self.main.getCocktailList()
            retPackage = {
                'action': 'response',
                'data': cocktailArray
            }
            
            #Update the shadow
            self.update_shadow(retPackage)
        elif(action == 'message'):
            print(data)

    #Updates BarBot's IoT shadow    
    def update_shadow(self, jsonData):
        self.shadow_handler.shadowUpdate(json.dumps(jsonData), self.update_callback, 5)

    #Callback function for BarBot's IoT
    def update_callback(self, payload, responseStatus, token):
        if(responseStatus == 'timeout'):
            print('There was a timeout updating the shadow')
        elif(responseStatus == 'accepted'):
            print("Successfully updated barbot's shadow")
        elif(responseStatus == 'rejected'):
            print("Shadow update was rejected")