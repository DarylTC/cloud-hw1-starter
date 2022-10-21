import random
import boto3
import json
import requests
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection

def send_email(location,cuisine,num_of_people,dining_date,dining_time,email,ddbResultList):
    SENDER = 'dc4676@nyu.edu' # must be verified in AWS SES Email
    RECIPIENT = email # must be verified in AWS SES Email
    AWS_REGION = 'us-east-1'
    SUBJECT = 'Your %s Restaurant Recommendations for %s'%(cuisine.capitalize(),dining_date)
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Hey")                
    # The HTML body of the email.
    htmlPTag = []
    for rest in ddbResultList:
        name = rest['Item']['name']['S']
        address1 = rest['Item']['location']['M']['address1']['S']
        address2 = rest['Item']['location']['M']['address2']['S']
        city = rest['Item']['location']['M']['city']['S']
        state = rest['Item']['location']['M']['state']['S']
        zip_code = rest['Item']['location']['M']['zip_code']['S']
        phone = rest['Item']['display_phone']['S']
        # full_address_phone = '%s \n %s \n %s \n %s, \n %s %s \n %s'%(name, address1,address2,city,state,zip_code,phone)
        rating = rest['Item']['rating']['S']
        review_count = rest['Item']['review_count']['S']
        image_url = rest['Item']['image_url']['S']
        pTag = '''
        <p><b>%s</b>
        <br>
        %s %s
        <br>
        %s,
        <br>
        %s %s
        <br>
        %s
        <br>
        Rating: %s
        <br>
        Number of reviews: %s
        </p>
        <img src=%s width="500" height="600">
        <br>
        '''%(name,address1,address2,city,state,zip_code,phone,rating,review_count,image_url)
        htmlPTag.append(pTag)

    body =''
    for p in htmlPTag:
        body += p

    BODY_HTML = '''
    <html>
    <head></head>
    <body>
    <h3>Below are our %d restaurants recommendations for %s at %s for party of %s:</h3>
    %s
    <br>
    <p> Hope you enjoy! </p>
    </body>
    </html>
    '''%(len(ddbResultList),dining_date,dining_time,num_of_people,body)    
    # The character encoding for the email.
    CHARSET = 'UTF-8'

    # Create a new SES resource and specify a region.
    ses = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = ses.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
        
                        'Data': BODY_HTML
                    },
                    'Text': {
        
                        'Data': BODY_TEXT
                    },
                },
                'Subject': {

                    'Data': SUBJECT
                },
            },
            Source=SENDER
        )
    except:
        raise

def lambda_handler(event, context):
    eventList = event['Records']
    for event in eventList:
        messageBody = json.loads(event['body'])
        location = messageBody['location']
        cuisine = messageBody['cuisine']
        num_of_people = messageBody['num_of_people']
        dining_date = messageBody['dining_date']
        dining_time = messageBody['dining_time']
        email = messageBody['email']
        print(location,cuisine,num_of_people,dining_date,dining_time,email)
        ##############################################
        region = 'us-east-1' # For example, us-west-1
        service = 'es'
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
        
        host = 'https://search-restaurants-flptbbafdcdgbwky3u3j3b3fxi.us-east-1.es.amazonaws.com' # The OpenSearch domain endpoint with https://
        index = 'restaurants'
        url = host + '/' + index + '/_search'
        
        # Put the user query into the query DSL for more accurate search results.
        # Note that certain fields are boosted (^).
        query = {
            "size": 5,
            "query": {
                "multi_match": {
                    "query": cuisine,
                    "fields": ["category"]
                }
            }
        }
        # Elasticsearch 6.x requires an explicit Content-Type header
        headers = { "Content-Type": "application/json" }
    
        # Make the signed HTTP request
        r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
        results = json.loads(r.text)
        resultContent = results['hits']['hits']
        idList = []
        for result in resultContent:
            idList.append(result['_id'])
        print(idList)
        # if doing only 1
        # print(random.choice(idList))
        # if giving, say, 5
        random.shuffle(idList)
        print(idList)
        
        # querying DynamoDB using id
        ddb = boto3.client('dynamodb')
        ddbResultList = []
        for id in range(0,5):
            data = ddb.get_item(
                TableName='yelp-restaurants',
                Key={
                    'id':{
                        'S':idList[id]
                    }
                }
            )
            ddbResultList.append(data)
        print(ddbResultList)

        # sending email
        send_email(location,cuisine,num_of_people,dining_date,dining_time,email,ddbResultList)

    return {
        'statusCode': 200,
        'body': json.dumps('Done!')
    }










#another approach#

# from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
# import boto3
# import json

# def lambda_handler(event, context):
#     eventList = event['Records']
#     for event in eventList:
#         messageBody = json.loads(event['body'])
#         location = messageBody['location']
#         cuisine = messageBody['cuisine']
#         num_of_people = messageBody['num_of_people']
#         dining_date = messageBody['dining_date']
#         dining_time = messageBody['dining_time']
#         email = messageBody['email']
#         print(location,cuisine,num_of_people,dining_date,dining_time,email)
#         ##############################################

#         host = 'search-restaurants-flptbbafdcdgbwky3u3j3b3fxi.us-east-1.es.amazonaws.com' # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
#         region = 'us-east-1' # e.g. us-west-1

#         credentials = boto3.Session().get_credentials()
#         auth = AWSV4SignerAuth(credentials, region)
#         index_name = 'restaurants'

#         client = OpenSearch(
#             hosts = [{'host': host, 'port': 443}],
#             http_auth = auth,
#             use_ssl = True,
#             verify_certs = True,
#             connection_class = RequestsHttpConnection
#         )

#         q = cuisine
#         query = {
#         'size': 5,
#         'query': {
#             'multi_match': {
#             'query': q,
#             'fields': ['category']
#             }
#         }
#         }

#         response = client.search(
#             body = query,
#             index = index_name
#         )

#         print('\nSearch results:')
#         print(response)
#################################
