import json
import os
import requests
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

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

report = {
    "repository": os.environ.get("GITHUB_REPOSITORY"),
    "branch": os.environ.get("GITHUB_REF_NAME"),
    "commit_sha": os.environ.get("GITHUB_SHA"),
    "run_id": os.environ.get("GITHUB_RUN_ID"),
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "status": status,
    "total_tests": passed + failed,
    "passed": passed,
    "failed": failed,
    "tests": tests
}

url = "http://127.0.0.1:5001/report"
print(f"Sending report to {url} ...")
try:
    response = requests.post(url, json=report, timeout=5)
    print(f"Response: {response.status_code}")
except Exception as e:
    print(f"Failed to send to localhost: {e}")