const AWS = require('aws-sdk');
AWS.config.region = 'us-east-1';
let lambda = new AWS.Lambda();

exports.handler = async (event) => {
    console.log(AWS.VERSION);
    let inputBody = event.messages[0].unstructured.text;
    console.log(inputBody);
    
    let lexService = new AWS.LexRuntime();
    let paramsToLex = {
      botName: "Restaurant_Recommender",
      botAlias: "dev",
      userId: "cloud",
      inputText: inputBody
    };
    let lexResult = await lexService.postText(paramsToLex).promise();
    console.log(lexResult);
    console.log(lexResult.message);  
  // ----------------------------------------------------------------------------
    let msgType = "unstructured";

    // body message has to be in array format
    let successMsg =[
        {
          "type": msgType,
          "unstructured": {
            "id": "string",
            /* change to lexResult message for now*/
            "text": lexResult.message,
            "timestamp": "string"
          }
        }
    ];
    
    // reponses:
    const successResponse = {
        statusCode: 200,
        headers: {
            "Access-Control-Allow-Origin": "*",
        },
        body: successMsg,
    };
    
    // Return: current assignment will return 200 only:
    const response = successResponse;
    return response;
};
