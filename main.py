from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request, Body, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scripts import custom_models as models, manage_db as mgr
import requests

############################ START OF CONFIG ############################

description = """
The Warehouse API helps you do... well, a bunch of random stuff!
For starters, feel free to check out the endpoints we provide:

## /students
Allows you to perform basic CRUD operations on a database - you may **search/create/update/delete** student records.
<hr>

## /weather
Get the weather for a particular region, courtesy of https://wttr.in
<hr>

## /apod
Gets the Astronomy Picture of the Day, courtesy of [NASA](https://api.nasa.gov/).
<hr>

## /xkcd
Get an XKCD comic.
<hr>

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

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0"
}

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
async def scalar_html(request: Request):
    return templates.TemplateResponse(request, "scalar.html")

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


@app.get(
    "/weather/{region}",
    response_description="Get the weather for a particular region",
    response_model=models.WeatherModel,
    response_model_by_alias=True,
)
async def get_weather(region: str):
    """
    Get the weather for a particular region, courtesy of https://wttr.in

    The region could be of one of the following types:

    |Type                   |Description
    |-----------------------|----------------
    |paris                  |city name
    |Москва                 |Unicode name of any location in any language
    |muc                    |airport code (3 letters)
    |@stackoverflow.com     |domain name
    |94107                  |area codes
    |-78.46,106.79          |GPS coordinates
    """

    resp = requests.get(f"https://wttr.in/{region}?format=j1", headers=headers).json()["current_condition"][0]
    data = {
        "temperature_c": resp["temp_C"],
        "feels_like_c": resp["FeelsLikeC"],
        "humidity": resp["humidity"],
        "description": resp["weatherDesc"][0]["value"],
        "precip_mm": resp["precipMM"],
        "visibility_km": resp["visibility"],
        "uv_index": resp["uvIndex"],
    }
    return data


@app.get(
    "/apod",
    response_description="Get Astronomy Picture of the Day",
    response_model=List[models.ApodResponseModel],
    response_model_by_alias=True,
)
async def get_apod(
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    count: Optional[int] = None,
    thumbs: Optional[bool] = False,
    api_key: str = "DEMO_KEY",
):
    """
    Gets the Astronomy Picture of the Day, courtesy of [NASA](https://api.nasa.gov/). 

    - `date`: The date of the APOD image to retrieve `(YYYY-MM-DD)`.
    - `start_date`: The start date of a range `(YYYY-MM-DD)`.
    - `end_date`: The end date of a range `(YYYY-MM-DD)`.
    - `count`: If specified, returns a number of random APODs. **Cannot be used with `date` or a date range**.
    - `thumbs`: If True, returns the thumbnail for video-type APODs.
    - `api_key`: Your NASA API key. Defaults to `'DEMO_KEY'`.
    """
    # Validate mutually exclusive conditions
    if date and (start_date or end_date or count):
        raise HTTPException(status_code=400, detail="`date` cannot be used with `start_date`, `end_date`, or `count`")
    if count and (date or start_date or end_date):
        raise HTTPException(status_code=400, detail="`count` cannot be used with `date` or a date range")

    params = {
        "date": date,
        "start_date": start_date,
        "end_date": end_date,
        "count": count,
        "thumbs": str(thumbs).lower(),
        "api_key": api_key,
    }

    response = requests.get("https://api.nasa.gov/planetary/apod", params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    data = response.json()
    if not isinstance(data, list):
        return [data]

    return data


@app.get(
    "/xkcd",
    response_description="Get XKCD comic info by ID or latest",
    response_model=models.XKCDComicModel,
    response_model_by_alias=True,
)
async def get_xkcd(id: Optional[int] = None):
    """
    Get an XKCD comic.

    - `id`: The comic ID to fetch. If omitted, returns the latest comic.
    """
    url = f"https://xkcd.com/{id}/info.0.json" if id else "https://xkcd.com/info.0.json"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail="Connectivity Issue :/")

    return response.json()
