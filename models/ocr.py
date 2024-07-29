import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
from ultralytics import YOLO
import numpy as np
import gdown
import os
import time

def crop_plate(img_path):
    model_path = './models/Detection/runs/detect/train/weights/best.pt' 
    model = YOLO(model_path)
    image = Image.open(img_path)
    results = model(img_path)
    
    for res in results:
        for box in res.boxes:
            confidence = box.conf[0].item()  # Get confidence score
            if confidence >= 0.7:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get bounding box coordinates
                cropped_image = image.crop((x1, y1, x2, y2))  # Crop the region
                cropped_array = np.array(cropped_image)  # Convert to numpy array
                return cropped_array
    return None 


def download_model_from_google_drive(file_id, destination_path):
    url = f'https://drive.google.com/uc?id={file_id}'
    temp_file_path = destination_path + ".part"
    gdown.download(url, temp_file_path, quiet=False)
    
    model_file = os.path.join(destination_path, "model.safetensors")

    # rename to model.safetensors
    os.rename(temp_file_path, model_file)


def ocr(img_path):

    model_path = "./models/OCR/results/trocr-finetuned"

    try:
        processor = TrOCRProcessor.from_pretrained(model_path)
        model = VisionEncoderDecoderModel.from_pretrained(model_path)
    except OSError:
        ocr_model_id = '1F3V_m1CaJuDi6EL9UOZthKq0uPaMzegb'
        ocr_model_path = './models/OCR/results/trocr-finetuned'

        download_model_from_google_drive(ocr_model_id, ocr_model_path)
        time.sleep(10)
        processor = TrOCRProcessor.from_pretrained(model_path)
        model = VisionEncoderDecoderModel.from_pretrained(model_path)

    cropped_image_array = crop_plate(img_path)
    
    if cropped_image_array is None:
        return "No license plate detected"

    # cropped numpy array to PIL image
    cropped_image = Image.fromarray(cropped_image_array)

    # preprocessing
    pixel_values = processor(images=cropped_image, return_tensors="pt").pixel_values

    # text geneation
    with torch.no_grad():
        generated_ids = model.generate(pixel_values)

    # decoding
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return generated_text

# usage test
# img_path = "./models/test_img/BC3565TH.jpg" 
# print(ocr(img_path))
