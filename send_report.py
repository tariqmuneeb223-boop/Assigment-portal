import json
import os
import requests
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

xml_file = "test-results.xml"

try:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    tests = []
    passed = 0
    failed = 0
    
    for testcase in root.iter('testcase'):
        name = testcase.get('name')
        failure = testcase.find('failure')
        
        if failure is not None:
            failed += 1
            tests.append({"name": name, "result": "failed", "message": failure.get('message')})
        else:
            passed += 1
            tests.append({"name": name, "result": "passed"})
            
    status = "passed" if failed == 0 else "failed"
    
except Exception as e:
    print(f"Error parsing XML: {e}")
    sys.exit(1)

report = {
    "repository": os.environ.get("GITHUB_REPOSITORY"),
    "branch": os.environ.get("GITHUB_REF_NAME"),
    "commit_sha": os.environ.get("GITHUB_SHA"),
    "run_id": os.environ.get("GITHUB_RUN_ID"),
    "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
    "status": status,
    "total_tests": passed + failed,
    "passed": passed,
    "failed": failed,
    "tests": tests
}

# 1. Send to localhost receiver
url = "http://127.0.0.1:5001/report"
print(f"Sending report to {url} ...")
try:
    response = requests.post(url, json=report)
    print(f"Response: {response.status_code}")
except Exception as e:
    print(f"Failed to send to localhost: {e}")

# 2. Send Email
try:
    sender_email = os.environ.get("EMAIL_USER")
    sender_password = os.environ.get("EMAIL_PASS")
    receiver_email = os.environ.get("EMAIL_TO")

    if sender_email and sender_password and receiver_email:
        print("Preparing to send email...")
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"Pipeline Report: {status.upper()} - {os.environ.get('GITHUB_REPOSITORY')}"

        # Create the email body
        body = f"""
        DevOps Pipeline Test Report
        ===========================
        Repository: {report['repository']}
        Branch: {report['branch']}
        Commit: {report['commit_sha']}
        
        Overall Status: {status.upper()}
        
        Total Tests: {report['total_tests']}
        Passed: {passed}
        Failed: {failed}
        
        Individual Test Results:
        """
        for t in tests:
            body += f"\n- {t['name']}: {t['result'].upper()}"
            if t['result'] == 'failed':
                body += f" (Error: {t.get('message', 'Unknown')})"

        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        
        print("✅ Email sent successfully!")
    else:
        print("Skipping email: Email secrets not configured.")
        
except Exception as e:
    print(f"Failed to send email: {e}")