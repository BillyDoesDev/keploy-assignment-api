def test_api_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "yep, here it goes again [Server's online!]"}


# def test_add_and_get_student(client):
#     student = {
#         "name": "Test User",
#         "email": "test@example.com",
#         "course": "Biology",
#         "gpa": 3.5
#     }

#     # Add student
#     res = client.post("/students/", json=student)
#     assert res.status_code == 201
#     body = res.json()
#     assert "id" in body
#     student_id = body["id"]

#     # Get same student
#     res = client.get(f"/students/{student_id}")
#     assert res.status_code == 200
#     assert res.json()["name"] == "Test User"

from unittest.mock import patch
def test_add_and_get_student(client):
    mock_student = {
        "_id": "507f1f77bcf86cd799439011",
        "name": "Test User",
        "email": "test@example.com",
        "course": "Biology",
        "gpa": 3.5
    }

    with patch("scripts.manage_db.create_student", return_value=mock_student), \
         patch("scripts.manage_db.show_student", return_value=mock_student):

        res = client.post("/students/", json=mock_student)
        assert res.status_code == 201
        body = res.json()
        assert body["name"] == "Test User"

        res = client.get(f"/students/{mock_student['_id']}")
        assert res.status_code == 200
        assert res.json()["course"] == "Biology"


def test_weather(client):
    res = client.get("/weather/London")
    assert res.status_code == 200
    assert "temperature_c" in res.json()


def test_apod(client):
    res = client.get("/apod")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_xkcd(client):
    res = client.get("/xkcd")
    assert res.status_code == 200
    assert "title" in res.json()
