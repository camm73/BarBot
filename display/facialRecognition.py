import boto3
import os
import datetime
import time
import pygame
import pygame.camera
from pygame.locals import *


class FacialRecognition():
    
    def __init__(self):
        #Initialize pygame library
        pygame.init()
        pygame.camera.init()
        
        #Start Camera
        self.cam = pygame.camera.Camera("/dev/video0", (1280, 720))
        time.sleep(0.1)

        #Global Definitions
        self.collectionId='barbotFaces' #collection name
        self.bucket = 'barbot-facial-recognition' #S3 bucket name
        self.imageDir = os.getcwd() + '/faces/'

        self.s3_client = boto3.client(
            's3',
            region_name='us-east-1',)

        #Rekognition Client Setup
        self.rek_client=boto3.client('rekognition',
            region_name='us-east-1',)

    def findFace(self):
        #Take an image of the person
        self.cam.start()
        pyImg = self.cam.get_image()
        timeStamp = datetime.datetime.now().isoformat()
        imagePath = self.imageDir + timeStamp + '.jpg'
        pygame.image.save(pyImg, "test.jpg")

        personName = ''
        confidence = None
        #Check the image against rekognition
        with open("test.jpg", 'rb') as image:
            try: #match the captured imges against the indexed faces
                match_response = self.rek_client.search_faces_by_image(CollectionId=self.collectionId, Image={'Bytes': image.read()}, MaxFaces=1, FaceMatchThreshold=85)
                if match_response['FaceMatches']:
                    personName = match_response['FaceMatches'][0]['Face']['ExternalImageId'].replace("-", " ")
                    confidence = match_response['FaceMatches'][0]['Face']['Confidence']
                    print(personName)
                    print('Confidence: ' + str(confidence))
                else:
                    print('No faces matched')
            except Exception as e:
                print('No face detected')
        
        #Remove image file
        os.remove("test.jpg")
        self.cam.stop()

        if personName == '':
            return False

        return personName

    #TODO: Add a face to the rekognition collection
    def indexFace(self):
        pass


if __name__ == "__main__":
    faceRecog = FacialRecognition()
    faceRecog.findFace()




