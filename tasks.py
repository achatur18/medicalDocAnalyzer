from celery import Celery
import os
import sys
from fastapi import UploadFile, File
# from process_pdf import process_pdf
from textract import transcribe
import os, shutil
from utils import draw_image, get_draw_instance, process_pdf, create_dir, save_pdf, extract_filename



from numpy.lib.recfunctions import recursive_fill_fields

sys.path.append(os.getcwd())

app = Celery('OCR', broker="amqp://127.0.0.1:5672",
             backend="mongodb://127.0.0.1:27017/task_results")


def process_file(person_id: int, file_loc: str):
    pages = process_pdf(file_loc)

    savedPages=[]
    saveLoc='http://18.130.155.16:7001/res/{}/'.format(extract_filename(file_loc))

    create_dir(saveLoc)

    for idx, page in enumerate(pages):
        response=transcribe(page)
        image, draw = get_draw_instance(page)
        draw=draw_image(draw, image.size, person_id, response)
        image.save(saveLoc+'{}.png'.format(idx))
        savedPages.append(saveLoc+'{}.png'.format(idx))
    return savedPages

@app.task(bind=True)
def start_processing(self, person_id: int, file_obj: str):
    return process_file(person_id, file_obj)