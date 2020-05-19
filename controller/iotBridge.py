from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json

class IoTManager():

    def __init__(self, main):
        self.main = main
        self.iotDetails = {}
        
        #Load AWS IoT Core details from json file
        with open('./certs/iotDetails.json', 'r') as file:
            self.iotDetails = json.load(file)

        mqttClient = AWSIoTMQTTClient('barbot')
        mqttClient.configureEndpoint(self.iotDetails['endpoint'], 8883)
        mqttClient.configureCredentials('./certs/root-CA.crt', './certs/BarBot.private.key', './certs/BarBot.cert.pem')

        mqttClient.configureOfflinePublishQueueing(0)
        mqttClient.configureDrainingFrequency(2)
        mqttClient.configureConnectDisconnectTimeout(15)
        mqttClient.configureMQTTOperationTimeout(5)

        mqttClient.connect()
        print('Connected to AWS IoT Core!')

        mqttClient.subscribe('barbot-main', 1, self.parse_message)

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
        elif(action == 'message'):
            print(data)