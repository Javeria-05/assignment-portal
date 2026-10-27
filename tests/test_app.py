import json
import pytest
from app import create_app


@pytest.fixture
def ctx(tmp_path):
    data_file = tmp_path / "subs.json"
    app = create_app(str(data_file))
    app.config["TESTING"] = True
    return app.test_client(), data_file


def form(**override):
    data = {
        "name": "Javeria Irum",
        "reg_no": "FA23-BSE-063",
        "title": "DevOps Lab Midterm",
        "submission_url": "https://github.com/javeria/assignment-portal",
    }
    data.update(override)
    return data


def test_valid_submission_is_saved_and_listed(ctx):
    client, data_file = ctx
    r = client.post("/", data=form())
    assert b"Submission saved successfully" in r.data
    assert b"Javeria Irum" in client.get("/").data
    assert len(json.loads(data_file.read_text())) == 1


def test_missing_registration_number_is_rejected(ctx):
    client, data_file = ctx
    r = client.post("/", data=form(reg_no=""))
    assert b"Registration number is required" in r.data
    assert not data_file.exists()


def test_invalid_url_is_rejected_and_not_saved(ctx):
    client, data_file = ctx
    r = client.post("/", data=form(submission_url="not-a-url"))
    assert b"Invalid submission URL" in r.data
    assert not data_file.exists()