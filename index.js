exports.handler = async (event) => {
    console.log(event.messages);

    let msgType = "unstructured";

    // body message has to be in array format
    let successMsg =[
        {
          "type": msgType,
          "unstructured": {
            "id": "string",
            "text": "Application under development. Search functionality will be implemented in Assignment 2",
            "timestamp": "string"
          }
        }
    ];
    console.log(successMsg);
    
    let unauthErrorMsg =[
        {
          "type": "unstructured",
          "unstructured": {
            "id": "string",
            "text": "This is unauthErrorMsg.",
            "timestamp": "string"
          }
        }
    ];
    console.log(unauthErrorMsg);
    let unexpectedErrorMsg =[
        {
          "type": "unstructured",
          "unstructured": {
            "id": "string",
            "text": "This is unexpectedErrorMsg.",
            "timestamp": "string"
          }
        }
    ];
    console.log(unexpectedErrorMsg);


    // reponses:
    const errResponse = {
        statusCode: 403,
        headers: {
            "Access-Control-Allow-Origin": "*",
        },
        body: unexpectedErrorMsg,
    };
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
