import os
from bson import ObjectId

from fastapi import Body, HTTPException, status, Response

from pymongo import AsyncMongoClient
from pymongo import ReturnDocument

try:
    import scripts.custom_models as models
except ImportError:
    from scripts import custom_models as models

from dotenv import load_dotenv
load_dotenv()

client = AsyncMongoClient(os.getenv("MONGODB_URL"))
db = client.college
student_collection = db.get_collection("students")


async def create_student(student: models.StudentModel = Body(...)):
    new_student = await student_collection.insert_one(
        student.model_dump(by_alias=True, exclude=["id"])
    )
    created_student = await student_collection.find_one(
        {"_id": new_student.inserted_id}
    )
    return created_student

async def list_students():
    return models.StudentCollection(students=await student_collection.find().to_list(1000))


async def show_student(id: str):
    if (
        student := await student_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")



async def update_student(id: str, student: models.UpdateStudentModel = Body(...)):
    student = {
        k: v for k, v in student.model_dump(by_alias=True).items() if v is not None
    }

    if len(student) >= 1:
        update_result = await student_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": student},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Student {id} not found")

    # The update is empty, but we should still return the matching document:
    if (existing_student := await student_collection.find_one({"_id": id})) is not None:
        return existing_student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")



async def delete_student(id: str):
    delete_result = await student_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")