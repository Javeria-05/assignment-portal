import json
import os
from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, render_template, request


def is_valid_url(url):
    if " " in url:
        return False
    p = urlparse(url)
    return p.scheme in ("http", "https") and bool(p.netloc)


def create_app(data_file=None):
    app = Flask(__name__)
    app.config["DATA_FILE"] = data_file or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "submissions.json"
    )

    def load():
        path = app.config["DATA_FILE"]
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(items):
        with open(app.config["DATA_FILE"], "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)

    def validate(form):
        errors = []
        if not form.get("name", "").strip():
            errors.append("Name is required")
        if not form.get("reg_no", "").strip():
            errors.append("Registration number is required")
        if not form.get("title", "").strip():
            errors.append("Assignment title is required")
        url = form.get("submission_url", "").strip()
        if not url:
            errors.append("Submission URL is required")
        elif not is_valid_url(url):
            errors.append("Invalid submission URL")
        return errors

    @app.route("/", methods=["GET", "POST"])
    def index():
        errors, message, form_data = [], None, {}
        if request.method == "POST":
            errors = validate(request.form)
            if errors:
                form_data = request.form
            else:
                items = load()
                items.append({
                    "name": request.form["name"].strip(),
                    "reg_no": request.form["reg_no"].strip(),
                    "title": request.form["title"].strip(),
                    "submission_url": request.form["submission_url"].strip(),
                    "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                save(items)
                message = "Submission saved successfully"
        return render_template("index.html", errors=errors, message=message,
                               submissions=load(), form=form_data)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)