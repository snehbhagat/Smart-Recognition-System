import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition' , region_name = 'ap-northeast-1')
dynamoDBTableName = 'employee-dsa'

dynamodb = boto3.resource('dynamodb' , region_name = 'ap-northeast-1')
employeeTable = dynamodb.Table(dynamoDBTableName)

def lambda_handler(event , context):
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['name']

    try:
        response = index_employee_image(bucket , key)
        print(response)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            faceID = response['FaceRecords'][0]['Face']['FaceId']
            name = key.split('.')[0].split('_')
            firstName = name[0]
            lastName = name[1]
            register_employee(faceID , firstName , lastName)
        return response
    except Exception as e:
        print(e)
        print('Error fetching images {} from the bucket {} ' .format(key , bucket))
        raise e

def index_employee_image(bucket , key):
    response = rekognition.index_faces(
        Image = {
            'S3Object' :
            {
                'Bucket' : bucket,
                'Name' : key
            }
        },
        CollectionID = "employees"
    )
    return response

def register_employee(faceID , firstName , lastName):
    employeeTable.put_item(
        Item = {
            'recognition-id' : faceID,
            'firstName' : firstName,
            'lastName' : lastName
        }
    )