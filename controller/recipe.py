import boto3
import time
import json
import decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('BarBot-Recipe')

#Uploads the provided recipe to dynamodb
def upload_recipe(recipe):
    try:
        amount_item = get_amounts(recipe)

        example_object = {
            'cocktailName': recipe['name'],
            'ingredients': recipe['ingredients'],
            'amounts': amount_item
        }
        
        response = table.put_item(
            Item={
                'cocktailName': recipe['name'].lower(), #MUST BE LOWERCASE BECAUSE DYNAMO IS CASE SENSITIVE FOR KEYS
                'ingredients': recipe['ingredients'],
                'amounts': amount_item
            }
        )
        
        print('Successfully uploaded recipe: ' + recipe['name'])
        return True

    except Exception as e:
        print(e)
        return False

#Get the amounts for a recipe in Dynamo
def get_amounts(recipe):
    data = {}
    for i in range(0, len(recipe['ingredients'])):
        data[recipe['ingredients'][i]] = decimal.Decimal(str(recipe['amounts'][i]))
    
    return data

#Fetches a recipe from dynamo
def get_recipe(recipe_name):
    try:
        response = table.get_item(
            Key={
                'cocktailName': recipe_name.lower() #MUST BE LOWERCASE
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
def get_all_recipes():
    new_cocktails = {}
    try:
        response = table.scan()

        for i in response['Items']:
            cocktail_data = json.dumps(i, cls=DecimalEncoder)
            new_cocktails[i['cocktailName']] = cocktail_data

        while 'LastEvaluatedKey' in response:
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey']
            )

            for i in response['Items']:
                cocktail_data = json.dumps(i, cls=DecimalEncoder)
                new_cocktails[cocktail_data['cocktailName']] = cocktail_data

    except Exception as e:
        print(e)
        return {}

    return new_cocktails


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

