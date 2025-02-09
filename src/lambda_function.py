import json
import boto3
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE', 'ItemsTable')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    http_method = event.get("httpMethod", "")
    path = event.get("path", "")
    body = json.loads(event.get("body", "{}")) if event.get("body") else {}
    
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
    
    update_expression = "SET " + ", ".join(f"{k} = :{k}" for k in data if k != "id")
    expression_values = {f":{k}": v for k, v in data.items() if k != "id"}
    
    try:
        table.update_item(
            Key={"id": data["id"]},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
        return {"statusCode": 200, "body": json.dumps({"message": "Item updated"})}
    except ClientError as e:
        return {"statusCode": 500, "body": json.dumps({"message": str(e)})}

def delete_item(data):
    if "id" not in data:
        return {"statusCode": 400, "body": json.dumps({"message": "Missing item ID"})}
    
    try:
        table.delete_item(Key={"id": data["id"]})
        return {"statusCode": 200, "body": json.dumps({"message": "Item deleted"})}
    except ClientError as e:
        return {"statusCode": 500, "body": json.dumps({"message": str(e)})}