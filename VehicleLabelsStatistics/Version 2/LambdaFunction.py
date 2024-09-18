import json
import boto3

dynamodb_client = boto3.client('dynamodb')
rekognition_client = boto3.client('rekognition')

def lambda_handler(event, context):
    # Get S3 object information
    s3_info = event['Records'][0]['s3']
    bucket_name = s3_info['bucket']['name']
    image_name = s3_info['object']['key']

    # Call the Rekognition service
    response = rekognition_client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': image_name
            }
        },
        MaxLabels=10
    )
    
    # Extract label information
    labels = response['Labels']

    if labels:
        for label in labels:
            # Prepare the DynamoDB item
            dynamodb_item = {
                'ImageName': {'S': image_name},  # Partition Key
                'LabelName': {'S': label['Name']},  # Sort Key
                'Confidence': {'N': str(label['Confidence'])}  # Confidence score
            }

            # Store the results in DynamoDB
            dynamodb_client.put_item(
                TableName='trafficlabels',
                Item=dynamodb_item
            )
        print(f"Labels stored for {image_name}")
    else:
        print(f"No labels found for {image_name}")

    return {
        'statusCode': 200,
        'body': json.dumps(f"Processing complete for {image_name}")
    }