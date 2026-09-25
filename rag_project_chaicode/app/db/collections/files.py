from pydantic import Field
from typing import TypedDict
from pymongo.asynchronous.collection import AsyncCollection
from ..db import database

class FileSchema(TypedDict):
    name : str = Field(..., description="Name of the file")
    status: str = Field(..., description="Status of the file")
    

COLLECTON_NAME ="files"
file_collection :AsyncCollection = database[COLLECTON_NAME]
