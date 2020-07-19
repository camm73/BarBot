# BarBot
BarBot is an open source automated bartender platform controlled by Raspberry Pi. BarBot can support up to 10 ingredients (2 carbonated, 8 non-carbonated) and provides a dynamic menu containing all cocktails that can be made from the available ingredients. BarBot can be controlled by the user through a [mobile app](https://github.com/camm73/BarBotApp), through [an Alexa Skill](https://github.com/camm73/barbot-alexa-skill), or through any other interface by using the Flask REST API hosted by the Raspberry Pi.

## Features
* Raspberry Pi Zero W controller
* 8 peristaltic pumps for non-carbonated ingredients (controlled by an 8-relay module)
* 2 solenoid valves and 2 pressurization air pumps for dispensing carbonated ingredients (controlled by a 4-relay module)
* Polarity switch relay for reversing pump direction, allowing for easy ingredient removal
* Flask REST API for controlling BarBot functions over local network
* AWS database/storage for storing cocktail recipes (DynamoDB Table), historical cocktail order data (DynamoDB Table), and cocktail preview images (S3 Bucket)
* [Alexa Skill](https://github.com/camm73/barbot-alexa-skill)
* [Mobile App](https://github.com/camm73/BarBotApp)

## Documentation and Build Instructions
The goal of BarBot is to provide an open source platform for building an automated bartender that can be customized to the user's desires. The following documentation provides build instructions for the BarBot and installation instructions for all software/cloud resources, however, the user is encouraged to modify the project how they see fit.

[BarBot Documentation](https://barbot-pi-images.s3.amazonaws.com/Barbot+Documentation.docx)
