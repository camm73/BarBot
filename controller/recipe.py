import boto3
import time
import json
import decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('BarBot-Recipe')

def uploadRecipe(recipe):
    try:
        amountItem = getAmounts(recipe)

        exampleObject = {
            'cocktailName': recipe['name'],
            'ingredients': recipe['ingredients'],
            'amounts': amountItem
        }
        
        response = table.put_item(
            Item={
                'cocktailName': recipe['name'].lower(), #MUST BE LOWERCASE BECAUSE DYNAMO IS CASE SENSITIVE FOR KEYS
                'ingredients': recipe['ingredients'],
                'amounts': amountItem
            }
        )
        
        print('Successfully uploaded recipe: ' + recipe['name'])
        return True

    except Exception as e:
        print(e)
        return False

def getAmounts(recipe):
    data = {}
    for i in range(0, len(recipe['ingredients'])):
        data[recipe['ingredients'][i]] = decimal.Decimal(str(recipe['amounts'][i]))
    
    return data

def getRecipe(recipeName):

    try:
        response = table.get_item(
            Key={
                'cocktailName': recipeName.lower() #MUST BE LOWERCASE
            }
        )
    except Exception as e:
        print(e)
        return {}
    else:
        recipe = response['Item']
        print('Successfully retrieved recipe from database')
        return recipe