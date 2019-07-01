import RPi.GPIO as GPIO
import time

class Main():

    def __init__(self):
        self.pumps = [26, 19, 13, 6, 5, 21, 20, 16]

        self.setupPins()
        self.getInput()

    def setupPins(self):
        try:
            print("Setting up pump pins...")
            for pin in self.pumps:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.HIGH)
            print("Pins successfully setup!")
        except Exception as e:
            print("Error setting up pump pins: " + str(e))

    def getInput(self):
        #TODO wait for input from the user and then make the cocktail
        #This is where the main loop will be held
        for pin in self.pumps:
            GPIO.output(pin, GPIO.LOW)
            print("Turning on pin " + str(pin))
            time.sleep(1)
            GPIO.output(pin, GPIO.HIGH)



if __name__ == '__main__':
    main = Main()
    print('Done')
        
