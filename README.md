# Assignment Submission Portal

## Run the application
pip install -r requirements.txt
python app.py        # open http://127.0.0.1:5000

## Run the tests
python -m pytest -v

## Start the report receiver
python receiver/receiver.py   # listens on http://127.0.0.1:9000/report
# Reports are saved as receiver/test-report.json

## CI
GitHub Actions workflow (.github/workflows/ci.yml) runs on every push
using a self-hosted runner on the local machine, sends the JSON report
to the receiver, emails the result, and deploys site/ to GitHub Pages
only when all tests pass on main.
Email secrets needed: MAIL_USERNAME, MAIL_PASSWORD, MAIL_TO.