from celery import Celery
import os
import sys
from fastapi import UploadFile, File
# from process_pdf import process_pdf
from textract import transcribe
import os, shutil
from utils import draw_image, get_draw_instance, process_pdf, create_dir



from numpy.lib.recfunctions import recursive_fill_fields

sys.path.append(os.getcwd())

app = Celery('OCR', broker="amqp://rabbitmq:5672",
             backend="mongodb://mongodb:27017/task_results")


@app.task(bind=True)
def start_processing(person_id: int, file_obj: UploadFile = File(...)):
# def process
    pages = process_pdf(file_obj)

    savedPages=[]
    saveLoc='./res/{}/'.format(file_obj.filename.split(".")[0])

    create_dir(saveLoc)

    for idx, page in enumerate(pages):
        response=transcribe(page)
        image, draw = get_draw_instance(page)
        draw=draw_image(draw, image.size, person_id, response)
        image.save(saveLoc+'{}.png'.format(idx))
        savedPages.append(saveLoc+'{}.png'.format(idx))
    return savedPages