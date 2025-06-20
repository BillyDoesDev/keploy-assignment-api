from fastapi import FastAPI, Request, Body, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scripts import db_models as models, manage_db as mgr

from dotenv import load_dotenv
load_dotenv()

############################ START OF CONFIG ############################

description = """
The Warehouse API helps you do... well, a bunch of random stuff!

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

app = FastAPI(
    title="The Warehouse",
    description=description,
    summary="The warehouse of the internet",
    version="0.0.1",
    license_info={
        "name": "Apache 2.0",
        "identifier": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

############################ INITIAL ROUTES ############################

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("assets/favicon.ico")

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "yep, here it goes again [Server's online!]"}

@app.get("/scalar", include_in_schema=False)
async def scalar_html(request:Request):
    return templates.TemplateResponse(request, "index.html")

############################ END OF CONFIG ############################


@app.post(
    "/students/",
    response_description="Add new student",
    response_model=models.StudentModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_student(student: models.StudentModel = Body(...)):
    """
    Insert a new student record.

    A unique `id` will be created and provided in the response.
    """
    return await mgr.create_student(student=student)


@app.get(
    "/students/",
    response_description="List all students",
    response_model=models.StudentCollection,
    response_model_by_alias=False,
)
async def list_students():
    """
    List all of the student data in the database.

    The response is unpaginated and limited to `1000` results.
    """
    return await mgr.list_students()


@app.get(
    "/students/{id}",
    response_description="Get a single student",
    response_model=models.StudentModel,
    response_model_by_alias=False,
)
async def show_student(id: str):
    """
    Get the record for a specific student, looked up by `id`.
    """
    return await mgr.show_student(id=id)


@app.put(
    "/students/{id}",
    response_description="Update a student",
    response_model=models.StudentModel,
    response_model_by_alias=False,
)
async def update_student(id: str, student: models.UpdateStudentModel = Body(...)):
    """
    Update individual fields of an existing student record.

    Only the provided fields will be updated.
    Any missing or `null` fields will be ignored.
    """
    return await mgr.update_student(id=id, student=student)


@app.delete("/students/{id}", response_description="Delete a student")
async def delete_student(id: str):
    """
    Remove a single student record from the database.
    """
    await mgr.delete_student(id=id)