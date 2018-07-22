from PIL import Image
import pytesseract

def simple_ocr(image):
    '''
    简单的OCR识别
    :param image: 需要识别的图片
    :return: 识别的结果文本
    '''
    text=pytesseract.image_to_string(Image.open('/home/ubuntu/Python_Workspace/SJTB/img/ocr_simple2.png'),lang='chi_sim')
    print(text)
    return text