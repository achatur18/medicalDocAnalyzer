
from PIL import Image as PImage, ImageDraw
from diseases import diseases
import os, shutil
from pdf2image import convert_from_path

# diseases=['anemia', 'alcohol', 'clinical', 'assistance', 'asians', 'jaundice', 'diebetes']
insured_diseases = {1: ['jaundice'], 2:['diabetes']}


def find_disease(text, diseases):
    if text in diseases:
        return True
    return False

def draw_image(draw, w_h, person_id, response=None, search_list=None):
    Keywords_flag=False
    bbs_exists=False
    if search_list==None:
        search_list=diseases
    else:
        Keywords_flag=True


    w, h=w_h
    for block in response['Blocks']:
        if "Text" in block.keys():
            bbx=block['Geometry']['BoundingBox']
            
            if find_disease(block['Text'].lower(), search_list):
                if Keywords_flag:
                    # print("Found-"+block['Text'].lower())
                    draw.rectangle(xy=[bbx['Left']*w, (bbx['Top']+bbx['Height'])*h, (bbx['Left']+bbx['Width'])*w, bbx['Top']*h], outline=(255, 255, 0), width=4)
                    bbs_exists=True
                elif find_disease(block['Text'].lower(), insured_diseases[int(person_id)]):
                    # print("Found-"+block['Text'].lower())
                    draw.rectangle(xy=[bbx['Left']*w, (bbx['Top']+bbx['Height'])*h, (bbx['Left']+bbx['Width'])*w, bbx['Top']*h], outline=(0, 255, 0), width=4)
                    bbs_exists=True
                else:
                    # print("NotFound-"+block['Text'].lower())
                    draw.rectangle(xy=[bbx['Left']*w, (bbx['Top']+bbx['Height'])*h, (bbx['Left']+bbx['Width'])*w, bbx['Top']*h], outline=(255, 0, 0), width=4)
                    bbs_exists=True
                

    return draw, bbs_exists


def get_draw_instance(documentName):
    image = PImage.open(documentName)
    rgb_im = image.convert('RGB')
    draw = ImageDraw.Draw(rgb_im)
    return rgb_im, draw

def create_dir(filename):
    if os.path.exists(filename):
        shutil.rmtree(filename)
    os.mkdir(filename)

def save_pdf(file_obj):
    filename='./temp/'
    create_dir(filename)

    location_file=filename+"{}.pdf".format(extract_filename(file_obj.filename))
    with open(location_file, 'wb') as file:
            file.write(file_obj.file.read())
    return location_file

def extract_filename(file_path):
    return file_path.split("/")[-1].split(".")[0]

def process_pdf(filename):
    images = convert_from_path(filename)
    save_path='./temp/{}/'.format(extract_filename(filename))
    create_dir(save_path)
    image_path=[]
    for idx, img in enumerate(images):
        img.save(os.path.join(save_path, '{}.jpg'.format(idx)), 'JPEG')
        image_path.append(os.path.join(save_path, '{}.jpg'.format(idx)))
    return image_path