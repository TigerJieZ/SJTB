import sys
sys.path.append('/home/ubuntu/Python_Workspace/SJTB/')
from tools.box.ocr import main

def testSimpleOCR():
    main.simple_ocr('')

if __name__ == '__main__':
    testSimpleOCR()