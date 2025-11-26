# Smart Customer Inverntory with AWS Bedrock (via Flask API & Google Apps Script)

This project connects a Google Form to a backend API (a Flask app running on EC2) and uses Amazon Bedrock for intelligent classification of customer messages. Form submissions are automatically forwarded to your backend — no manual intervention required.

Architecture
-----------
Google Form → Google Apps Script → Backend API → Amazon Bedrock → Response Logged → Email Alert 

Features
--------
- ✅ Automatically triggers on every Google Form submission
- ✅ Sends form data securely to your backend endpoint
- ✅ Supports Bedrock AI analysis or any other API integration
- ✅ Logs all submissions and responses in Google Apps Script
- ✅ Send email to resective teams based on urgency of the request
- ✅ Works with ngrok for quick HTTPS testing

Prerequisites
-------------
- A Google Form
- Access to Google Apps Script
- A backend API endpoint (e.g., Flask running locally or on EC2)
- (Optional) ngrok for tunneling local servers
- Access to AWS

Step 1 — Create the Google Form
-------------------------------
Create a new form named `Customer Inquiry Form` with the following fields:

| Label                  | Type          |
|------------------------|---------------|
| Name                   | Short answer  |
| Organization           | Short answer  |
| Email                  | Short answer  |
| Country                | Short answer  |
| Reason for Contacting  | Paragraph     |

Step 2 — Open Google Apps Script
--------------------------------
From the form editor:
- Click the three dots (⋮) at the top-right → **Script editor**

You’ll be redirected to the Apps Script project that is container-bound to your form.

Step 3 — Add the Apps Script
----------------------------
Paste the following code into the Apps Script editor:

```javascript
function onFormSubmit(e) {
  Logger.log("📦 Raw event: " + JSON.stringify(e, null, 2));

  // Ensure the event object exists
  if (!e) {
    Logger.log("⚠️ Missing event object — did this trigger from a form?");
    return;
  }

  // Capture item responses (safer than namedValues)
  var itemResponses = e.response.getItemResponses();
  var payload = {};

  itemResponses.forEach(function(item) {
    var title = item.getItem().getTitle();
    var response = item.getResponse();
    payload[title] = response;
    Logger.log("📝 " + title + ": " + response);
  });

  // Prepare your Flask API endpoint
  var url = "https://pauletta-hiltless-gordon.ngrok-free.dev/submit";

  // Prepare options
  var options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true // <-- capture error responses too
  };

  try {
    // Send to Flask
    var response = UrlFetchApp.fetch(url, options);

    // Log everything about the Bedrock/Flask response
    Logger.log("✅ Status: " + response.getResponseCode());
    Logger.log("✅ Flask/Bedrock response: " + response.getContentText());
  } catch (err) {
    Logger.log("❌ Error sending to Flask/Bedrock: " + err);
  }
}

function setupTriggerProper() {
  // Optional safety cleanup of duplicates
  const allTriggers = ScriptApp.getProjectTriggers();
  allTriggers.forEach(t => {
    if (t.getHandlerFunction() === "onFormSubmit") {
      ScriptApp.deleteTrigger(t);
    }
  });

  const form = FormApp.getActiveForm();
  ScriptApp.newTrigger("onFormSubmit")
    .forForm(form)
    .onFormSubmit()
    .create();
  Logger.log("✅ Clean trigger created successfully");
}

```

Step 4 — Set Up the Trigger
---------------------------
In the Apps Script editor:
- Click **Triggers** (clock icon on the left)
- Add a new trigger with:
  - Function: `onFormSubmit`
  - Event source: `From form`
  - Event type: `On form submit`
- Save and authorize when prompted

Step 5 — Create a Public Endpoint (with ngrok)
----------------------------------------------
- Create the main app.py file. This conatins the main logic that receives the form data and sends it to Bedrock. If a valid resonse is received from Bedrock, then it triggers an email via ses. The email functionality is in email_utils.y file.
  
Step 6 — Create a Public Endpoint (with ngrok)
----------------------------------------------
If your backend is running locally or on an instance without a public IP, use ngrok to create a public HTTPS tunnel.

Install ngrok:
```bash
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.tgz
tar -xvzf ngrok-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

Authenticate ngrok:
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

Run ngrok (example for a Flask app on port 5000):
```bash
ngrok http 5000
```

You’ll see an output such as:
```
Forwarding  https://abcd1234.ngrok-free.app -> http://localhost:5000
```

Copy the public HTTPS URL and replace the URL in the Apps Script:
```js
var url = "https://abcd1234.ngrok-free.app/submit";
```

Step 7 — Test the Integration
-----------------------------
- Submit the Google Form.
- In Apps Script → Executions, you should see logs like:
  - "✅ API Response: { "success": true, "bedrock_output": {...} }"<img width="1919" height="651" alt="image" src="https://github.com/user-attachments/assets/b01a5484-4e72-4c46-9b73-5e765d79f504" />

- Check your backend logs to confirm receipt and processing.

Step 8 — Keep ngrok Running in the Background (Optional)
-------------------------------------------------------
Create a systemd service to keep ngrok active (example):

Create `/etc/systemd/system/ngrok.service` with:

```ini
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
```

Enable & start it:
```bash
sudo systemctl enable ngrok
sudo systemctl start ngrok
```

End-to-End Test Summary
-----------------------
| Step                             | Description                         | Status |
|----------------------------------|-------------------------------------|--------|
| Google Form created              | 5 fields                            | ✅     |
| Apps Script added                | Trigger setup done                  | ✅     |
| Backend exposed via ngrok        | HTTPS URL active                    | ✅     |
| Form submission tested           | Logs captured                       | ✅     |
| API response logged              | Bedrock integrated                  | ✅     |

Example Log Output
------------------
```
📦 Raw event: {...}
Name: John Doe
Organization: Example Corp
Email: john@example.com
Country: India
Reason for Contacting: Need support with setup
✅ API Response: {"success": true, "category": "Support", "priority": "Medium"}
```
Step 9 — Send smart Alerts based on priority
-----------------------------
- Create and configure email ID for SES
- Create a email_utils.py to send emails using ses function
  ```bash
            response = ses.send_email(
            Source="heloiseviegas03@gmail.com",
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}}
            }
        )
  ```
- Create a policy to allow EC2 to use SES
  ```bash
  {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": "*"
        }
    ]
  }
  ```

Summary
-------
You’ve automated Google Form submissions using:
- Google Apps Script to capture responses
- HTTP POST integration to your backend
- ngrok for secure tunneling (optional)
- Amazon Bedrock (or any AI model) for intelligent classification
- Amazon SES to send email alerts<img width="1315" height="208" alt="image" src="https://github.com/user-attachments/assets/aef25f80-bd99-4f5f-9942-0136f6784e60" />


This setup is simple, cloud-friendly, and fully customizable — ideal for automating lead capture, support triage, or workflow processing.

- Generate a ready-to-deploy Flask endpoint example that accepts the form payload and calls Bedrock
- Add automated tests or CI instructions
- Add environment / security notes for production deployment
