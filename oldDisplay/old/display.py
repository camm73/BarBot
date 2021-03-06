import sys
import time
import json
import tkinter as tk
from tkinter.font import Font
import requests
import urllib.parse
import subprocess
import socket
import subprocess
import threading
from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
import traceback
import FacialRecognition

app = FlaskAPI(__name__)

#HOSTNAME = barbotdisplay.local
class Display():
    
    #====================TODO====================#
    #Need to create local rest api endpoints for the existing
    #cocktail making functions and other information retrieval.#

    def __init__(self):
        self.cocktailButtons = {}
        self.window = None
        #self.controllerHost = 'http://' + self.getIpAddress() + ':5000'
        self.controllerHost = 'http://barbot.local:5000'
        print('Host address is: ' + self.controllerHost)
        self.cocktailNames = []
        self.getCocktailNames()
        self.facialRecog = FacialRecognition()
        self.createGUI()
    
    #TODO change this to be the static ip address of the pi
    def getCocktailNames(self):
        try:
            res = requests.get(self.controllerHost + '/cocktailList/')
            
            if(res.status_code != 200):
                print('There was an error!')
                return
            else:
                self.cocktailNames = res.json()
                print(self.cocktailNames)
        except Exception:
            print('Error getting cocktail names')
            exit(1)

    def makeCocktail(self, name):
        urlName = urllib.parse.quote(name)
        res = requests.get(self.controllerHost + '/cocktail/' +  urlName + '/')
        if(res.status_code != 200):
            print('There was an error!')
            return
        self.facialRecog.findFace()


    def cleanPumps(self):
        res = requests.get(self.controllerHost + '/clean/')

        if(res.status_code != 200):
            print('There was an error!')

    #Creates the GUI interface for selecting a cocktail
    def createGUI(self):
        self.window = tk.Tk()
        self.window.grid()
        self.window.geometry('640x440')
        self.window.title('BarBot - Beta Version 1.0')
        i = 0
        buttonCol = 0
        buttonRow = 0
        cocktailButtonFont = Font(family='Helvetica', size=24, weight="normal")
        for drink in self.cocktailNames:
            if(buttonCol == 3):
                buttonCol = 0
                buttonRow += 1
            name = self.cocktailNames[i]
            self.cocktailButtons[i] = tk.Button(self.window, text=name, font=cocktailButtonFont, width = 10, height =5, command= lambda name=name: self.makeCocktail(name))
            self.cocktailButtons[i].grid(column=buttonCol, row=buttonRow)
            buttonCol += 1
            i = i+1
        buttonCol = 1
        buttonRow += 1
        cleanButton = tk.Button(self.window, text='Clean Pumps', width = 8, height = 4, command=self.cleanPumps)
        cleanButton.grid(row=buttonRow, column=buttonCol)
        buttonRow += 1
        stopButton = tk.Button(self.window, text='STOP', width = 10, height = 5, command=self.window.destroy)
        stopButton.grid(row=buttonRow, column=buttonCol)
        '''
        buttonRow += 1
        buttonCol -=1
        offlineButton = tk.Button(self.window, text='Go Offline', width = 6, height = 2, command=self.triggerControllerOffline)
        offlineButton.grid(row=buttonRow, column=buttonCol)
        buttonCol += 1
        onlineButton = tk.Button(self.window, text='Go Online', width = 6, height = 2, command=self.triggerControllerOnline)
        onlineButton.grid(row=buttonRow, column=buttonCol)
        '''
        self.window.mainloop()


    def triggerControllerOffline(self):
        try:
            res = requests.get(self.controllerHost + '/offline/')
        except Exception:
            print('Error going offline')
            exit(1)

    def triggerControllerOnline(self):
        try:
            res = requests.get(self.controllerHost + '/online/')
        except Exception:
            print('Error going online')
            exit(1)

    def getIpAddress(self):
        try:
            print('Retrieving ip address...')
            addr = socket.gethostbyname('barbot.local')
            print('Controller IP Address: ' + addr)
            return addr
        except socket.gaierror:
            print('ERROR RESOLVING BARBOT HOSTNAME!')
            exit(1)

@app.route('/offline/', methods=['GET'])
def goOffline():
    offlineThread = threading.Thread(target=executeOffline)
    offlineThread.daemon = True
    offlineThread.start()

    return status.HTTP_200_OK

@app.route('/online/', methods=['GET'])
def goOnline():
    try:
        onlineThread = threading.Thread(target=executeOnline)
        onlineThread.daemon = True
        onlineThread.start()
    except Exception as e:
        print(e)
        traceback.print_stack()
    
    return status.HTTP_200_OK

def executeOnline():
    print('HERE')
    time.sleep(5)
    subprocess.call(['/home/pi/BarBotOffline/display/goOnline'])
    print('After Here')

def executeOffline():
    time.sleep(5)
    subprocess.call(['/home/pi/BarBotOffline/display/goOffline'])

def startAPI():
    app.run(debug=False, host='0.0.0.0')
    print('API Started!')


if __name__ == "__main__":
    apiThread = threading.Thread(target=startAPI)
    apiThread.daemon = True
    apiThread.start()
    display = Display()
    print('Exitting...')
    
