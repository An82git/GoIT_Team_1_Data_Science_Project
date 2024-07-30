import os


img_folder = './ocr_dataset/img'

for img in os.listdir(img_folder):
    with open('./ocr_dataset/labels.csv', 'a') as file:
        file.write(f'{img},{img[:-4]}\n')