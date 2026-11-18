from flask import Flask, request, render_template_string, redirect
from urllib.parse import urlparse

app = Flask(__name__)
submissions = []

def is_valid_url(url):
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except:
        return False

def validate(data):
    errors = []
    if not data.get("name", "").strip():
        errors.append("Name is required")
    if not data.get("reg_no", "").strip():
        errors.append("Registration number is required")
    if not data.get("title", "").strip():
        errors.append("Assignment title is required")
    url = data.get("url", "").strip()
    if not url:
        errors.append("Submission URL is required")
    elif not is_valid_url(url):
        errors.append("Invalid submission URL")
    return errors

# ---------- HTML template ----------
# Kept as a string so we don't need a templates/ folder.
PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Assignment Submission Portal</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 700px; margin: 40px auto; }
    input { display: block; margin: 6px 0 12px; padding: 6px; width: 100%; }
    .error { color: red; }
    .success { color: green; }
    table { border-collapse: collapse; width: 100%; margin-top: 20px; }
    th, td { border: 1px solid #ccc; padding: 6px; text-align: left; }
  </style>
</head>
<body>
  <h2>Assignment Submission Portal</h2>

  {% if errors %}
    <ul class="error">
      {% for e in errors %}<li>{{ e }}</li>{% endfor %}
    </ul>
  {% endif %}

  <form method="POST" action="/submit">
    <label>Name</label>
    <input name="name" value="{{ form.name or '' }}">
    <label>Registration Number</label>
    <input name="reg_no" value="{{ form.reg_no or '' }}">
    <label>Assignment Title</label>
    <input name="title" value="{{ form.title or '' }}">
    <label>Submission URL</label>
    <input name="url" value="{{ form.url or '' }}">
    <button type="submit">Submit</button>
  </form>

  <h3>Saved Submissions ({{ submissions|length }})</h3>
  {% if submissions %}
  <table>
    <tr><th>Name</th><th>Reg No</th><th>Title</th><th>URL</th></tr>
    {% for s in submissions %}
    <tr>
      <td>{{ s.name }}</td>
      <td>{{ s.reg_no }}</td>
      <td>{{ s.title }}</td>
      <td>{{ s.url }}</td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
    <p>No submissions yet.</p>
  {% endif %}
</body>
</html>
"""

def render_page(errors=None, form=None):
    return render_template_string(
        PAGE,
        errors=errors or [],
        form=form or {},
        submissions=submissions,
    )

@app.route("/")
def index():
    return render_page()

@app.route("/submit", methods=["POST"])
def submit():
    data = {
        "name": request.form.get("name", ""),
        "reg_no": request.form.get("reg_no", ""),
        "title": request.form.get("title", ""),
        "url": request.form.get("url", ""),
    }
    errors = validate(data)
    if errors:
        # Reject: re-render with errors, do NOT save
        return render_page(errors=errors, form=data), 400

    # Valid: save and redirect
    submissions.append({
        "name": data["name"].strip(),
        "reg_no": data["reg_no"].strip(),
        "title": data["title"].strip(),
        "url": data["url"].strip(),
    })
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)