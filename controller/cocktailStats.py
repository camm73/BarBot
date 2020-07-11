import json
import boto3

dynamodb = boto3.client('dynamodb')

#Update the number of times a specific cocktail has been created
def increment_cocktail(cocktail_name):
    try:
        res = dynamodb.update_item(
            TableName='BarBot-cocktailStats',
            Key={
                'cocktailName': {
                    'S': cocktail_name
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
        print(cocktail_name + ' not in database yet. Creating...')
        dynamodb.put_item(
            TableName='BarBot-cocktailStats',
            Item={
                'cocktailName': {
                    'S': cocktail_name
                },
                'count': {
                    'N': '1'
                }
            }
        )