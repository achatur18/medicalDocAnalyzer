from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
# from process_pdf import process_pdf
from textract import transcribe
import os, shutil
from utils import draw_image, get_draw_instance, process_pdf, create_dir, save_pdf, extract_filename
from tasks import start_processing, process_file

from celery.result import AsyncResult
import pymongo

client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
# Database Name
db = client["task_results"]
# Collection Name
coll = db["celery_taskmeta"]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post('/process')
async def process(file_obj: UploadFile = File(...)):
    person_id=int(extract_filename(file_obj.filename).split("_")[-1])
    file_loc = save_pdf(file_obj)
    print("pdf saved at : ", file_loc)
    return process_file(person_id, file_loc)


@app.post('/batch_process')
async def process_pdf_async(file_obj: UploadFile = File(...)):
    person_id=int(extract_filename(file_obj.filename).split("_")[-1])
    file_loc = save_pdf(file_obj)
    print("pdf saved at : ", file_loc)
    result=start_processing.delay(person_id, file_loc)
    return {"status": result.state, 'id': result.id, 'error': ''}


@app.post('/check_progress/{task_id}')
async def check_async_progress(task_id: str):
    try:
        result = AsyncResult(task_id)
        if result.ready():
            data = coll.find({'_id': task_id})[0]
            return {'status': 'SUCEESS', 'data': data['result']}
        else:
            return {"status": result.state, "error": ''}
    except Exception as e:
        data = coll.find({'_id': task_id})[0]
        if data:
            return {'status': 'SUCEESS', 'data': data['result']}
        return {'status': 'Task ID invalid', 'error': e}
