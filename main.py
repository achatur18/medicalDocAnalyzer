from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
# from process_pdf import process_pdf
from textract import transcribe
import os, shutil
from utils import draw_image, get_draw_instance, process_pdf, create_dir, save_pdf, extract_filename
from tasks import start_processing

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post('/process')
def process(person_id: int, file_obj: UploadFile = File(...)):
    file_loc = save_pdf(file_obj)
    print("pdf saved at : ", file_loc)
    pages = process_pdf(file_loc)

    savedPages=[]
    saveLoc='./res/{}/'.format(extract_filename(file_loc))

    create_dir(saveLoc)

    for idx, page in enumerate(pages):
        response=transcribe(page)
        image, draw = get_draw_instance(page)
        draw=draw_image(draw, image.size, person_id, response)
        image.save(saveLoc+'{}.png'.format(idx))
        savedPages.append(saveLoc+'{}.png'.format(idx))
    return savedPages


@app.post('/batch_process')
async def process_pdf_async(person_id: int, file_obj: UploadFile = File(...)):
    try:
        return {"result": start_processing.delay()}
    except Exception as e:
        return {"status": 'FAILURE', 'error': e}
