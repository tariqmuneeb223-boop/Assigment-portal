import pytest
from app import app, submissions

# This fixture automatically clears the submissions list before every single test
@pytest.fixture(autouse=True)
def clear_submissions():
    submissions.clear()
    yield

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_valid_submission_saved(client):
    """Test 1: Complete details and a valid submission URL -> Saved and displayed."""
    response = client.post("/submit", data={
        "name": "Tariq Muneeb",
        "reg_no": "Sp23-BCs-024",
        "title": "MID lab",
        "url": "https://smart-city-ai-service.onrender.com/health"
    }, follow_redirects=True)
    
    # Check that it succeeded (200 OK after redirect)
    assert response.status_code == 200
    # Check that it was saved in memory
    assert len(submissions) == 1
    assert submissions[0]["name"] == "Tariq Muneeb"
    # Check that it appears in the HTML page
    assert b"Tariq Muneeb" in response.data

def test_missing_reg_no_rejected(client):
    """Test 2: Missing registration number -> Rejected with validation message."""
    response = client.post("/submit", data={
        "name": "Ali",
        "reg_no": "", # Missing!
        "title": "Lab 2",
        "url": "https://example.com/file.pdf"
    })
    
    # Check that it was rejected (400 Bad Request)
    assert response.status_code == 400
    # Check the error message appears on the page
    assert b"Registration number is required" in response.data
    # Check it was NOT saved
    assert len(submissions) == 0

def test_invalid_url_rejected(client):
    """Test 3: Invalid submission URL -> Rejected and not saved."""
    response = client.post("/submit", data={
        "name": "Sara",
        "reg_no": "FA22-BCS-001",
        "title": "Lab 3",
        "url": "not-a-valid-url" # Invalid!
    })
    
    # Check that it was rejected
    assert response.status_code == 400
    # Check the error message appears
    assert b"Invalid submission URL" in response.data
    # Check it was NOT saved
    assert len(submissions) == 0