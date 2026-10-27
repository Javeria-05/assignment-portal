import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

tests = []
try:
    root = ET.parse("report.xml").getroot()
    for tc in root.iter("testcase"):
        result, msg = "passed", None
        for tag in ("failure", "error"):
            el = tc.find(tag)
            if el is not None:
                result = "failed"
                msg = el.get("message") or (el.text or "")[:500]
        if tc.find("skipped") is not None:
            result = "skipped"
        tests.append({"name": tc.get("name"), "result": result,
                      "failure_message": msg})
except Exception as e:
    tests.append({"name": "test-execution", "result": "failed",
                  "failure_message": f"Could not read test results: {e}"})

passed = sum(t["result"] == "passed" for t in tests)
failed = sum(t["result"] == "failed" for t in tests)

report = {
    "repository": os.getenv("GITHUB_REPOSITORY", "local"),
    "branch": os.getenv("GITHUB_REF_NAME", "local"),
    "commit_sha": os.getenv("GITHUB_SHA", "local"),
    "pipeline_run_id": os.getenv("GITHUB_RUN_ID", "local"),
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "tests": tests,
    "total": len(tests),
    "passed": passed,
    "failed": failed,
    "overall_status": "passed" if failed == 0 and len(tests) > 0 else "failed",
}

with open("report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

lines = [
    f"Repository: {report['repository']}",
    f"Branch: {report['branch']}",
    f"Commit: {report['commit_sha']}",
    f"Overall: {report['overall_status'].upper()}",
    f"Total: {report['total']}  Passed: {passed}  Failed: {failed}",
    "",
]
for t in tests:
    line = f"- {t['name']}: {t['result']}"
    if t["failure_message"]:
        line += f" ({t['failure_message'][:150]})"
    lines.append(line)
with open("summary.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

url = os.getenv("RECEIVER_URL", "http://localhost:9000/report")
req = urllib.request.Request(
    url, data=json.dumps(report).encode(),
    headers={"Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print("Report delivered:", r.status)
except Exception as e:
    print("Failed to deliver report:", e)
    sys.exit(1)