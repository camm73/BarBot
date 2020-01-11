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


#Perform a table scan to return a list of all of the recipes
def getAllRecipes():
    newCocktails = {}
    try:
        response = table.scan()

        for i in response['Items']:
            cocktailData = json.dumps(i, cls=DecimalEncoder)
            newCocktails[i['cocktailName']] = cocktailData

        while 'LastEvaluatedKey' in response:
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey']
            )

            for i in response['Items']:
                cocktailData = json.dumps(i, cls=DecimalEncoder)
                newCocktails[cocktailData['cocktailName']] = cocktailData

    except Exception as e:
        print(e)
        return {}

    return newCocktails


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

