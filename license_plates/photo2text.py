import cv2
import easyocr
import re
import matplotlib.pyplot as plt
# from ultralytics import YOLO
# import roboflow
# import torch
# import tensorflow as tf


reader = easyocr.Reader(['uk'], gpu=False)


def read_text(image_path):

    # Завантаження зображення
    image = cv2.imread(image_path)

    # Перевірка, чи зображення завантажилось успішно
    if image is None:
        print("Failed to load image.")
        exit(1)

    # обрізаємо зайвий верх 
    crop_percent = 0.3  # 30% зображення
    # Визначити кількість пікселів для обрізання
    crop_pixels = int(crop_percent * image.shape[0])
    # Обрізати верхню частину зображення
    image = image[crop_pixels:, :]

    # робимо бінаризацію зображення і фільтра
    # image = cv2.blur(image, (2, 2))
    # gaus = cv2.GaussianBlur(image, (3, 3), 0)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)[1]V, 31, 2)

    # Відображення зображення за допомогою matplotlib
    # plt.imshow(cv2.cvtColor(binary, cv2.COLOR_BGR2RGB))
    # plt.axis('off')
    # plt.show()

    if __name__ == "__main__":
        cv2.imshow('Test', binary)
        cv2.waitKey()

    # Знаходимо контури на зображенні
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Обходимо всі знайдені контури
    for cnt in contours:
        # Отримуємо координати прямокутника навколо контуру
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Фільтруємо області, які не мають типових розмірів номерних знаків
        aspect_ratio = w / float(h)
        if  2 < aspect_ratio < 5 and w > 90 and w < 260 :
            # Вирізаємо область номерного знака
            roi = image[y:y+h, x:x+w]
            # Масштабуємо вирізану область
            # roi_resized = cv2.resize(roi, (125, 45), interpolation=cv2.INTER_NEAREST)
            roi_resized = cv2.resize(roi, (450, 100), interpolation=cv2.INTER_NEAREST)

            if __name__ == "__main__":
                cv2.imshow('Test', roi_resized)
                cv2.waitKey()
            # plt.imshow(cv2.cvtColor(roi_resized, cv2.COLOR_BGR2RGB))
            # plt.axis('off')
            # plt.show()
            
            # Розпізнавання тексту
            if reader.readtext(roi_resized):
                result = reader.readtext(roi_resized)
                # Виведення результатів
                for res in result:
                    if len(res[1]) > 4:
                        text_without_spaces =  re.sub(r'[^a-zA-Zа-яА-ЯёЁіїґІЇҐ0-9-]', '', res[1])  
                        print("Розпізнаний текст:", text_without_spaces.upper())
                        if len(text_without_spaces) > 4:
                            # pass
                            return text_without_spaces.upper()

                    
if __name__ == "__main__":
    # read_text('noms\AA0005CO.jpg')
    read_text('nom\BI7658HK.jpg')
    read_text('nom\BI6948BH.jpg')
    # read_text('nom\BC7684OB.jpg')





