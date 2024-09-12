import boto3
import json

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition' , region_name = 'ap-northeast-1')
dynamoDBTableName = 'employee-dsa'

dynamodb = boto3.resource('dynamodb' , region_name = 'ap-northeast-1')
employeeTable = dynamodb.Table(dynamoDBTableName)

bucketName = 'visitor-pictures-dsa'

def lambda_handler(event , context):
    print(event)
    objectKey = event['queryStringParameters']['objectKey']
    image_bytes = s3.get_object(Bucket = bucketName , Key = objectKey)['Body'].read()
    response = rekognition.search_faces_by_images(
        CollectionID = 'employees',
        Image = {'Byter' : image_bytes}
    )

    for match in response['FaceMatches']:
        print(match['Face']['FaceId'] , match['Face']['Confidence'])

        face = employeeTable.get_item(
            key = {
                'recognition-id' : match['Face']['FaceId']
            }
        )
        if 'Item' in face:
            print('Person found: ' , face['Item'])
            return buildResponse(200 , {
                'Message' : 'Success',
                'firstName' : face['Item']['firstName'],
                'lastName' : face['Item']['lastName']
            })
    
    print('Person could not be recognised')
    return buildResponse(403 , {'Message' : 'Person could not be found'})

def buildResponse(statusCode , body = None):
    response = {
        'statusCode' : statusCode,
        'headers' : {
            'Content-Type' : 'application/json',
            'Access-Control-Allow-Orgin' : '*'

        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    return response