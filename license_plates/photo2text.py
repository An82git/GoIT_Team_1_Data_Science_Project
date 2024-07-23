import cv2
import easyocr
import matplotlib.pyplot as plt


def read_text(image_path):
    # Ініціалізація EasyOCR
    reader = easyocr.Reader(['uk'])

    # image_path = 'nom\BX7851HX.jpg'
    # image_path = 'nom\BC8011PT.jpg'

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

    # робимо бінаризацію зображення
    height, width, _ = image.shape
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)[1]

    # Відображення зображення за допомогою matplotlib
    # plt.imshow(cv2.cvtColor(binary, cv2.COLOR_BGR2RGB))
    # plt.axis('off')
    # plt.show()
    # cv2.imshow('Test', binary)
    # cv2.waitKey()

    # Знаходимо контури на зображенні
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Створюємо копію зображення для візуалізації
    # image_copy = image.copy()

    # Обходимо всі знайдені контури
    for cnt in contours:
        # Отримуємо координати прямокутника навколо контуру
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Фільтруємо області, які не мають типових розмірів номерних знаків
        aspect_ratio = w / float(h)
        if w > h*3 and 2 < aspect_ratio < 9 and w > 50 and w < 350 :
            # Вирізаємо область номерного знака
            roi = image[y:y+h, x:x+w]
            
            # Масштабуємо вирізану область
            roi_resized = cv2.resize(roi, (85, 20), interpolation=cv2.INTER_NEAREST)
            # roi_resized = cv2.resize(roi, (150, 40), interpolation=cv2.INTER_NEAREST)


            # Відображення зображення за допомогою matplotlib
            # cv2.imshow('Test', roi_resized)
            # cv2.waitKey()
            # plt.imshow(cv2.cvtColor(roi_resized, cv2.COLOR_BGR2RGB))
            # plt.axis('off')
            # plt.show()
            
            # Розпізнавання тексту
            if reader.readtext(roi_resized):
                result = reader.readtext(roi_resized)
        
                # Виведення результатів
                for res in result:
                    if len(res[1]) > 3:
                        text_without_spaces = res[1].replace(" ", "")
                        # print("Розпізнаний текст:", text_without_spaces.upper())
                        return text_without_spaces.upper()

                    
if __name__ == "__main__":
    read_text('nom\BX7851HX.jpg')





