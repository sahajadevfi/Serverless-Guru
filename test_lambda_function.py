import os
import json
import boto3
import pytest
from moto import mock_aws

os.environ["AWS_ACCESS_KEY_ID"] = "fake_access_key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "fake_secret_key"
os.environ["AWS_SESSION_TOKEN"] = "fake_session_token"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

from lambda_function import lambda_handler

@pytest.fixture
def setup_dynamodb():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        
        table = dynamodb.create_table(
            TableName="ItemsTable",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
        table.wait_until_exists()
        yield table 


def test_create_item(setup_dynamodb):
    event = {"httpMethod": "POST", "body": json.dumps({"id": "123", "name": "Test Item"})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 201
    assert "Test Item" in response["body"]

def test_get_item(setup_dynamodb):
    setup_dynamodb.put_item(Item={"id": "123", "name": "Test Item"})

    event = {"httpMethod": "GET", "queryStringParameters": {"id": "123"}}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    assert "Test Item" in response["body"]

def test_update_item(setup_dynamodb):
    setup_dynamodb.put_item(Item={"id": "123", "name": "Old Name"})
    event = {"httpMethod": "PUT", "body": json.dumps({"id": "123", "name": "New Name"})}
    response = lambda_handler(event, None)
    assert response["statusCode"] == 200

def test_delete_item(setup_dynamodb):
    setup_dynamodb.put_item(Item={"id": "123", "name": "Test Item"})
    event = {"httpMethod": "DELETE", "body": json.dumps({"id": "123"})}
    response = lambda_handler(event, None)
    assert response["statusCode"] == 200
