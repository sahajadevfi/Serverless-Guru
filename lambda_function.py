import json
import boto3
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table_name = os.environ.get('DYNAMODB_TABLE', 'ItemsTable')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    http_method = event.get("httpMethod", "")
    path = event.get("path", "")
    body = json.loads(event.get("body", "{}")) if event.get("body") else {}
    print(f'body is {body}')
    if http_method == "POST":
        return create_item(body)
    elif http_method == "GET":
        return get_item(event.get("queryStringParameters", {}))
    elif http_method == "PUT":
        return update_item(body)
    elif http_method == "DELETE":
        return delete_item(body)
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Unsupported HTTP method"})
        }

def create_item(data):
    try:
        table.put_item(Item=data)
        return {"statusCode": 201, "body": json.dumps({"message": "Item created", "item": data})}
    except ClientError as e:
        return {"statusCode": 500, "body": json.dumps({"message": str(e)})}

def get_item(params):
    if not params or "id" not in params:
        return {"statusCode": 400, "body": json.dumps({"message": "Missing item ID"})}
    
    try:
        response = table.get_item(Key={"id": params["id"]})
        item = response.get("Item")
        if not item:
            return {"statusCode": 404, "body": json.dumps({"message": "Item not found"})}
        return {"statusCode": 200, "body": json.dumps(item)}
    except ClientError as e:
        return {"statusCode": 500, "body": json.dumps({"message": str(e)})}

def update_item(data):
    if "id" not in data:
        return {"statusCode": 400, "body": json.dumps({"message": "Missing item ID"})}
    try:
        id = data["id"]
        new_value = data.get("value", "")
        response = table.update_item(
            Key={"id": id},
            UpdateExpression="SET #val = :value",
            ExpressionAttributeNames={"#val": "value"},
            ExpressionAttributeValues={":value": new_value},
            ReturnValues="UPDATED_NEW"
        )
        return {"statusCode": 200, "body": f'item updated: {data}'}
    except ClientError as e:
        return {"statusCode": 500, "body": json.dumps({"message": str(e)})}

def delete_item(data):
    if "id" not in data:
        return {"statusCode": 400, "body": json.dumps({"message": "Missing item ID"})}
    
    try:
        table.delete_item(Key={"id": data["id"]})
        return {"statusCode": 200, "body": json.dumps({"message": "Item del eted"})}
    except ClientError as e:
        return {"statusCode": 500, "body": json.dumps({"message": str(e)})}