---

DATADOG LOGS TO AWS LAMBDA FUNCTION URL (HTTP LOG FORWARDING)

This document describes how to forward logs from Datadog Log Forwarding (Custom HTTP Destination) to an AWS Lambda Function URL for testing.

---

PREREQUISITES

* Datadog account with Logs enabled
* AWS account with permission to(can use Datadog - tse-sandbox AWS account):
  * Create Lambda functions
  * Create Lambda Function URLs
  * View CloudWatch Logs
* Python 3.x+ Lambda runtime

---

STEP 1 — CREATE THE LAMBDA FUNCTION

1. Open AWS Console → Lambda
2. Click "Create function"
3. Choose:
   * Author from scratch
   * Runtime: Python 3.9+
4. Create the function
5. Copy the function code and deploy

---

STEP 2 — CREATE A LAMBDA FUNCTION URL

1. Open the Lambda function
2. Go to Configuration → Function URL
3. Click "Create function URL"
4. Set:
   * Auth type: NONE
5. Save and copy the Function URL
   Example:
   https://<id>.lambda-url.<region>.on.aws

---

STEP 3 — CREATE DATADOG LOG FORWARDING DESTINATION

1. Open Datadog
2. Go to Logs → Configuration
3. Open Log Archiving & Forwarding
4. Select Log Forwarding
5. Click "New Destination"
6. Configure:

   * Type: Custom destination
   * Protocol: HTTP
   * Endpoint: Lambda Function URL

Add request header:

x-dd-secret: abc123abc

Add filter (recommended for testing):

source:dummydog
URL: https://datadoghq.atlassian.net/wiki/spaces/TS/pages/1381269949/Dummydog+-+Send+Test+Logs+Events

Save the destination.

---

STEP 4 — VERIFY DELIVERY

1. Generate logs that match the filter (example: source:dummydog)
2. Open AWS Console → CloudWatch → Logs
3. Open the Lambda log group
4. Confirm logs are being received

---

NOTES

* This uses Datadog Log Forwarding, not Log Archiving
* Logs are forwarded in batches
* Payloads are typically gzipped
* Intended for testing and prototyping only

---

