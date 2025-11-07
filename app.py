from flask import Flask, request, jsonify
import boto3
import json
app = Flask(__name__)   # creates flask application object 

bedrock=boto3.client(service_name="bedrock-runtime", region_name="ap-south-1")  # create Bedrock client
  
# A decorator used to tell the application 
# which URL is associated function 
@app.route('/submit',methods=['POST'])       # route to display the message
def get_form_data():    #binds function to route
    data = request.get_json()
    print("📥 Received from form:", data)

    # Extract the user's message/reason
    reason = data.get("reason", "No message provided")

    # Construct the prompt for Titan
    prompt = f"""
    You are a smart customer support assistant.
    Analyze the following customer message and classify it.

    Message: "{reason}"

    Return your response in JSON format with these fields:
    - category: One of [Sales Inquiry, Billing, Support, General]
    - priority: One of [Low, Medium, Urgent, Very Urgent]
    - short_summary: A short one-sentence summary of what the customer wants.
    """

    try:
        # Call Amazon Titan Text Express
        response = bedrock.invoke_model(
            modelId="amazon.titan-text-express-v1",
            body=json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 256,
                    "temperature": 0.3
                }
            }),
            accept="application/json",
            contentType="application/json"
        )

        # Parse Bedrock's response
        result = json.loads(response['body'].read())
        output_text = result.get("results", [{}])[0].get("outputText", "").strip()

        print("🧠 Bedrock raw output:", output_text)

        # Try to cleanly parse the model's JSON if it outputs valid JSON text
        try:
            parsed_output = json.loads(output_text)
        except Exception:
            parsed_output = {"raw_text": output_text}

        return jsonify({
            "success": True,
            "bedrock_output": parsed_output
        }), 200

    except Exception as e:
        print("❌ Error in Bedrock call:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

  
if __name__=='__main__': # run the application if app.py is executed directly
   app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
