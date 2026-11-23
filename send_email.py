import os
import sys
import xml.etree.ElementTree as ET
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    tree = ET.parse("test-results.xml")
    root = tree.getroot()
    tests, passed, failed = [], 0, 0
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

try:
    sender_email = os.environ.get("EMAIL_USER")
    sender_password = os.environ.get("EMAIL_PASS")
    receiver_email = os.environ.get("EMAIL_TO")

    if sender_email and sender_password and receiver_email:
        print("Preparing to send email...")
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"Pipeline Report: {status.upper()}"

        body = f"Overall Status: {status.upper()}\nTotal Tests: {passed + failed}\nPassed: {passed}\nFailed: {failed}\n\nIndividual Results:\n"
        for t in tests:
            body += f"\n- {t['name']}: {t['result'].upper()}"
            if t['result'] == 'failed':
                body += f" (Error: {t.get('message', 'Unknown')})"

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
    else:
        print("Skipping email: Email secrets not configured.")
except Exception as e:
    print(f"Failed to send email: {e}")