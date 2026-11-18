from flask import Flask, request, jsonify
import json
import datetime

app = Flask(__name__)

@app.route("/report", methods=["POST"])
def receive_report():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    data["received_at"] = datetime.datetime.now().isoformat()

    with open("test-report.json", "w") as f:
        json.dump(data, f, indent=4)

    print("\n" + "="*40)
    print(f"✅ RECEIVED REPORT! Status: {data.get('status')}")
    print("Saved to test-report.json")
    print("="*40 + "\n")

    return jsonify({"message": "Report saved successfully"}), 200

if __name__ == "__main__":
    print("Receiver listening on http://127.0.0.1:5001/report")
    app.run(host="127.0.0.1", port=5001, debug=False)