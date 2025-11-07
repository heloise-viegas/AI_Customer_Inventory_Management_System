🚀 Automating Google Form Submissions with AWS Bedrock (via Flask API) using Google Apps Script

This project connects a Google Form to a backend API (e.g., Flask on AWS EC2) that uses Amazon Bedrock for intelligent classification of customer messages.

Whenever someone submits the form, the data is automatically sent to your backend — no manual intervention needed.

🧩 Architecture Overview
Google Form → Google Apps Script → Backend API → Amazon Bedrock → Response Logged

🪄 Features

✅ Automatically triggers on every Google Form submission
✅ Sends form data securely to your backend endpoint
✅ Supports Bedrock AI analysis or any other API integration
✅ Logs all submissions and responses in Google Apps Script
✅ Works with ngrok for quick HTTPS testing

🧰 Prerequisites

A Google Form

Access to Google Apps Script

A backend API endpoint (e.g., Flask running locally or on EC2)

(Optional) ngrok for tunneling local servers

🧱 Step 1. Create a Google Form

Create a new form called Customer Inquiry Form with these fields:

Label	Type
Name	Short answer
Organization	Short answer
Email	Short answer
Country	Short answer
Reason for Contacting	Paragraph
🧩 Step 2. Open Google Apps Script

From the form editor:

⋮ (three dots in top-right) → Script editor


You’ll be redirected to the Apps Script project linked to your form (container-bound).

🧠 Step 3. Add the Apps Script

Paste this code inside the editor:

function onFormSubmit(e) {
  Logger.log("📦 Raw event: " + JSON.stringify(e, null, 2));

  if (e && e.response) {
    var itemResponses = e.response.getItemResponses();
    var payload = {};

    itemResponses.forEach(function(item) {
      var title = item.getItem().getTitle();
      var answer = item.getResponse();
      payload[title] = answer;
      Logger.log(title + ": " + answer);
    });

    try {
      var url = "https://YOUR_NGROK_URL_OR_PUBLIC_API/submit"; // Replace with your endpoint
      var options = {
        method: "post",
        contentType: "application/json",
        payload: JSON.stringify(payload)
      };
      var response = UrlFetchApp.fetch(url, options);
      Logger.log("✅ API Response: " + response.getContentText());
    } catch (err) {
      Logger.log("❌ Error sending to API: " + err);
    }
  } else {
    Logger.log("⚠️ Missing form response event data");
  }
}

function setupTriggerProper() {
  const form = FormApp.getActiveForm();
  ScriptApp.newTrigger("onFormSubmit")
    .forForm(form)
    .onFormSubmit()
    .create();
}

⚙️ Step 4. Set Up the Trigger

In the Apps Script editor:

Click Triggers (clock icon on the left).

Add a new trigger with these settings:

Function: onFormSubmit

Event source: From form

Event type: On form submit

Save and authorize when prompted.

🌐 Step 5. Create a Public Endpoint (with ngrok)

If your backend is running locally or on EC2, use ngrok to create a public HTTPS tunnel.

Install ngrok
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.tgz
tar -xvzf ngrok-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

Authenticate ngrok
ngrok config add-authtoken YOUR_AUTHTOKEN

Run ngrok
ngrok http 5000


You’ll get an output like:

Forwarding  https://abcd1234.ngrok-free.app -> http://localhost:5000


Copy that public HTTPS URL and replace this line in your Apps Script:

var url = "https://abcd1234.ngrok-free.app/submit";

🧾 Step 6. Test the Integration

Submit your Google Form

Go to Apps Script → Executions

You’ll see logs like:

✅ API Response: { "success": true, "bedrock_output": {...} }


You can also check your backend logs (if you’ve implemented them).

🧩 Step 7. Keep ngrok Running in the Background (Optional)

Create a systemd service to keep ngrok active:

sudo nano /etc/systemd/system/ngrok.service


Paste this:

[Unit]
Description=ngrok tunnel
After=network.target

[Service]
ExecStart=/usr/local/bin/ngrok http 5000
Restart=always
User=ubuntu
WorkingDirectory=/home/ubuntu
StandardOutput=append:/var/log/ngrok.log
StandardError=append:/var/log/ngrok.log

[Install]
WantedBy=multi-user.target


Enable & start it:

sudo systemctl enable ngrok
sudo systemctl start ngrok

✅ End-to-End Test Summary
Step	Description	Status
Google Form created	5 fields	✅
Apps Script added	Trigger setup done	✅
Backend exposed via ngrok	HTTPS URL active	✅
Form submission tested	Logs captured	✅
API response logged	Bedrock integrated	✅
🧠 Example Log Output
📦 Raw event: {...}
Name: John Doe
Organization: Example Corp
Email: john@example.com
Country: India
Reason for Contacting: Need support with setup
✅ API Response: {"success": true, "category": "Support", "priority": "Medium"}

💡 Summary

You’ve successfully automated Google Form submissions using:

Google Apps Script to capture responses

HTTP POST integration to your backend

ngrok for secure tunneling

Amazon Bedrock (or any AI model) for intelligent classification

This approach is simple, cloud-friendly, and fully customizable — perfect for automating lead capture, support triage, or workflow processing.
