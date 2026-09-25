from fastapi import FastAPI, UploadFile, File
from uuid import uuid4

from .db.collections.files import file_collection, FileSchema
from .utils.file import save_to_disk
from.queue.q import q
from .queue.workers import process_file
app = FastAPI()


@app.get("/") 
def hello():
    return {"status": "healthy!"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    db_file = await file_collection.insert_one(
        {
            "name": file.filename,
            "status": "saving",
        }
    )

    file_path = f"./uploads/{str(db_file.inserted_id)}/{file.filename}"

    await save_to_disk(
        file=await file.read(),
        path=file_path,
    )

    # Push to queue
    job = q.enqueue(process_file,str(db_file.inserted_id),file_path)

    # MongoDB save
    await file_collection.update_one(
        {"_id": db_file.inserted_id},
        {
            "$set": {
                "status": "queued",
            }
        },
    )

    return {"file_id": str(db_file.inserted_id)}
