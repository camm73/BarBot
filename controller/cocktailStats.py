import json
import boto3

dynamodb = boto3.client('dynamodb')

#Update the number of times a specific cocktail has been created
def incrementCocktail(cocktailName):
    try:
        res = dynamodb.update_item(
            TableName='BarBot-cocktailStats',
            Key={
                'cocktailName': {
                    'S': cocktailName
                }
            },
            ExpressionAttributeNames= {
                '#count': 'count'
            },
            ExpressionAttributeValues = {
                ':inc': {
                    'N': '1'
                }
            },
            UpdateExpression="SET #count = #count + :inc",
            ReturnValues='UPDATED_NEW'
        )
    except Exception as e:
        print(cocktailName + ' not in database yet. Creating...')
        dynamodb.put_item(
            TableName='BarBot-cocktailStats',
            Item={
                'cocktailName': {
                    'S': cocktailName
                },
                'count': {
                    'N': '1'
                }
            }
        )