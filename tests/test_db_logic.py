import pytest
import mongomock
from bson import ObjectId
from scripts import manage_db as mgr, custom_models as models


# A minimal async wrapper for mongomock collection
class AsyncMockCollection:
    def __init__(self, collection):
        self._collection = collection

    async def insert_one(self, *args, **kwargs):
        return self._collection.insert_one(*args, **kwargs)

    async def find_one(self, *args, **kwargs):
        return self._collection.find_one(*args, **kwargs)

    def find(self, *args, **kwargs):
        result = list(self._collection.find(*args, **kwargs))

        class Cursor:
            async def to_list(self, limit):
                return result[:limit]

        return Cursor()

    async def delete_one(self, *args, **kwargs):
        return self._collection.delete_one(*args, **kwargs)


@pytest.fixture
def mock_db(monkeypatch):
    client = mongomock.MongoClient()
    db = client["test_db"]
    collection = db["students"]
    monkeypatch.setattr(mgr, "student_collection", AsyncMockCollection(collection))
    return collection


@pytest.mark.asyncio
async def test_create_and_list_students(mock_db):
    student = models.StudentModel(
        name="Alice", email="alice@example.com", course="Math", gpa=3.8
    )
    created = await mgr.create_student(student)
    assert created["name"] == "Alice"

    listed = await mgr.list_students()
    assert listed.students[0].email == "alice@example.com"


@pytest.mark.asyncio
async def test_show_student_success(mock_db):
    student = {"name": "Bob", "email": "bob@example.com", "course": "CS", "gpa": 3.0}
    inserted_id = mock_db.insert_one(student).inserted_id

    found = await mgr.show_student(str(inserted_id))
    assert found["name"] == "Bob"


@pytest.mark.asyncio
async def test_show_student_not_found(mock_db):
    with pytest.raises(mgr.HTTPException) as excinfo:
        await mgr.show_student(str(ObjectId()))
    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_student_success(mock_db):
    student = {"name": "Del", "email": "del@example.com", "course": "Bio", "gpa": 3.2}
    inserted_id = mock_db.insert_one(student).inserted_id

    response = await mgr.delete_student(str(inserted_id))
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_student_not_found(mock_db):
    with pytest.raises(mgr.HTTPException) as excinfo:
        await mgr.delete_student(str(ObjectId()))
    assert excinfo.value.status_code == 404
