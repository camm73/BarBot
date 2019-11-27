import boto3
import time
import json
import decimal

def uploadRecipe(recipe):
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.Table('BarBot')

        amountItem = getAmounts(recipe)

        exampleObject = {
            'cocktailName': recipe['name'],
            'ingredients': recipe['ingredients'],
            'amounts': amountItem
        }

        return exampleObject
        
        response = table.put_item(
            Item={
                'cocktailName': recipe['name'],
                'ingredients': recipe['ingredients'],
                'amounts': amountItem
            }
        )
    except Exception as e:
        print(e)
        return False

def getAmounts(recipe):
    data = {}
    for i in range(0, len(recipe['ingredients'])):
        data[recipe['ingredients'][i]] = recipe['amounts'][i]
    
    return data