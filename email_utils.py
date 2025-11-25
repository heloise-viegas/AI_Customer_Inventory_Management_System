import boto3
import logging
import traceback

PRIORITY_EMAIL_MAP = {
    "High": "heloiseviegas03@gmail.com",
    "Medium": "heloiseviegas03@gmail.com",
    "Low": "heloiseviegas03@gmail.com"
}

ses = boto3.client("ses", region_name="ap-south-1")

def send_priority_email(priority, payload, bedrock_output):
    email = PRIORITY_EMAIL_MAP.get(priority, "")

    logging.info("📧 Preparing email...")
    logging.info(f"📧 Priority = {priority}")
    logging.info(f"📧 Sending to = {email}")

    subject = f"[{priority}] New Customer Inquiry Received"
    body = f""" "{bedrock_output}" """
    

    try:
        response = ses.send_email(
            Source="heloiseviegas03@gmail.com",
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}}
            }
        )
        logging.info(f"✅ Email sent successfully: {response}")

    except Exception as e:
        logging.error("❌ ERROR sending email!")
        logging.error(str(e))
        logging.error(traceback.format_exc())
