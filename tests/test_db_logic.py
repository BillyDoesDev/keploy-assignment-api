import mongomock
import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock
from scripts import manage_db as mgr


class AsyncMockCollection:
    def __init__(self, collection):
        self._collection = collection

    async def insert_one(self, *args, **kwargs):
        return self._collection.insert_one(*args, **kwargs)

    async def find_one(self, *args, **kwargs):
        return self._collection.find_one(*args, **kwargs)

    async def find_one_and_update(self, *args, **kwargs):
        return self._collection.find_one_and_update(*args, **kwargs)

    async def delete_one(self, *args, **kwargs):
        return self._collection.delete_one(*args, **kwargs)

    def find(self, *args, **kwargs):
        # simulate Motor’s `find().to_list(...)` usage
        result = list(self._collection.find(*args, **kwargs))
        class Cursor:
            async def to_list(self, limit):
                return result[:limit]
        return Cursor()


@pytest.fixture
def mock_db(monkeypatch):
    mock_client = mongomock.MongoClient()
    collection = mock_client.db["students"]
    async_mock = AsyncMockCollection(collection)
    monkeypatch.setattr(mgr, "student_collection", async_mock)
    return collection
