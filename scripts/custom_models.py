from typing import List, Optional
from typing_extensions import Annotated

from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from bson import ObjectId
from datetime import datetime

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]


class StudentModel(BaseModel):
    """
    Container for a single student record.
    """

    # The primary key for the StudentModel, stored as a `str` on the instance.
    # This will be aliased to `_id` when sent to MongoDB,
    # but provided as `id` in the API requests and responses.
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    email: EmailStr = Field(...)
    course: str = Field(...)
    gpa: float = Field(..., le=4.0)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": 3.0,
            }
        },
    )


class UpdateStudentModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    course: Optional[str] = None
    gpa: Optional[float] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": 3.0,
            }
        },
    )


class StudentCollection(BaseModel):
    """
    A container holding a list of `StudentModel` instances.

    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    students: List[StudentModel]


class WeatherModel(BaseModel):
    temperature_c: float = None
    feels_like_c: float = None
    humidity: float = None
    description: str = None
    precip_mm: float = None
    visibility_km: float = None
    uv_index: float

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "temperature_c": 15,
                "feels_like_c": 18,
                "humidity": 97,
                "description": "Light drizzle",
                "precip_mm": 0.4,
                "visibility_km": 2,
                "uv_index": 0,
            }
        },
    )


class ApodResponseModel(BaseModel):
    date: Optional[str]
    explanation: Optional[str]
    media_type: Optional[str]
    service_version: Optional[str]
    title: Optional[str]
    url: Optional[str]
    hdurl: Optional[str] = None
    thumbnail_url: Optional[str] = None
    copyright: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "copyright": "Ramesh",
                "date": "2024-06-21",
                "explanation": "Astronomy Picture of the Day explanation text...",
                "media_type": "image",
                "service_version": "v1",
                "title": "A Stunning Galaxy",
                "url": "https://apod.nasa.gov/apod/image/2406/example.jpg",
                "hdurl": "https://apod.nasa.gov/apod/image/2406/example_hd.jpg",
                "thumbnail_url": "https://apod.nasa.gov/apod/image/2406/thumb.jpg",
            }
        }
    }


class XKCDComicModel(BaseModel):
    month: str
    num: int
    link: str
    year: str
    news: str
    safe_title: str
    transcript: str
    alt: str
    img: str
    title: str
    day: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "month": "7",
                "num": 614,
                "link": "",
                "year": "2009",
                "news": "",
                "safe_title": "Woodpecker",
                "transcript": "[[Transcript text here...]]",
                "alt": "If you don't have an extension cord I can get that too.  Because we're friends!  Right?",
                "img": "https://imgs.xkcd.com/comics/woodpecker.png",
                "title": "Woodpecker",
                "day": "24"
            }
        }
    }
