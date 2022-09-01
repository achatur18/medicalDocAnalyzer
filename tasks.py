from typing import List, Union
import uuid
from celery import Celery
import os
import sys
from fastapi import UploadFile, File
# from process_pdf import process_pdf
from textract import transcribe
import os, shutil
from utils import draw_image, get_draw_instance, process_pdf, create_dir, save_pdf, extract_filename
import json



from numpy.lib.recfunctions import recursive_fill_fields

sys.path.append(os.getcwd())

app = Celery('OCR', broker="amqp://127.0.0.1:5672",
             backend="mongodb://127.0.0.1:27017/task_results")

cache={}


def process_file(person_id: int, file_loc: str, search_list=None):
    pages = process_pdf(file_loc)

    savedPages=[]
    saveLoc='./res/{}/'.format(extract_filename(file_loc))

    create_dir(saveLoc)

    for idx, page in enumerate(pages):
        key = extract_filename(file_loc)+"_{}".format(idx)
        if key in cache.keys():
            response = cache[key]
        else:
            response=transcribe(page)
            cache[key]=response
        image, draw = get_draw_instance(page)
        draw, bbs_exists=draw_image(draw, image.size, person_id, response, search_list)
        if bbs_exists:
            ids=uuid.uuid4().hex
            image.save(saveLoc+'{}.png'.format(ids))
            savedPages.append('http://18.130.155.16:7001/'+saveLoc[2:]+'{}.png'.format(ids))
    return savedPages

@app.task(bind=True)
def start_processing(self, person_id: int, file_loc: str, search_list: Union[List, None]=None):
    return process_file(person_id, file_loc, search_list)