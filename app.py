from flask import Flask, request, jsonify
import boto3
import json
import logging
from email_utils import send_priority_email

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

app = Flask(__name__)

bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

@app.route('/submit', methods=['POST'])
def get_form_data():
    data = request.get_json()
    logging.info(f"📥 Received from form: {data}")

    payload = {
        "name": data.get("name", ""),
        "organization": data.get("organization", ""),
        "email": data.get("email", ""),
        "country": data.get("country", ""),
        "reason": data.get("reason", "")
    }

    try:
        reason = payload["reason"]

        prompt = f"""
        You are a classifier. Read the user message below and return ONLY a JSON object.

        User Reason:
        {reason}

        Return JSON ONLY in this exact format:
        {{
        "category": "Billing | Technical | Other",
        "priority": "High | Medium | Low",
        "summary": "Write a one sentence summary"
        }}
        NO explanation. ONLY JSON.
        """

        response = bedrock.invoke_model(
            modelId="amazon.titan-text-lite-v1",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"inputText": prompt})
        )

        raw = json.loads(response["body"].read())

        # Titan returns this structure:
        # {"results":[{"outputText":"..."}]}
        output_text = raw["results"][0]["outputText"].strip()

        logging.info(f"🧠 Bedrock raw output: {output_text}")

        try:
            parsed_output = json.loads(output_text)
        except:
            parsed_output = {"raw_text": output_text}

        priority = parsed_output.get("priority", "Low")
        logging.info(f"🧠 Parsed Bedrock output: {priority}")
        logging.info("📧 Sending alert email...")
        send_priority_email(priority, payload, parsed_output)

        return jsonify({"success": True, "bedrock_output": parsed_output}), 200

    except Exception as e:
        logging.error(f"❌ Error in /submit: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
