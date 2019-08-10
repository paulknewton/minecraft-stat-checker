"""
OCR unit tests that require tesseract to be installed
"""
from ocr import MinecraftScreenReader
import cv2
import numpy as np


def test_ocr():
    """
    Test character recognition of a test image.
    """
    img = cv2.imread("tests/test.png")
    ocr = MinecraftScreenReader(img)

    users = ocr.get_users()
    assert users == ['_byF3l1lx_', 'Sternlicht', 'dramatc', 'StegobertFanyboy', 'UnwichtigsDing', 'lolmcOO1',
                     'PrestigePrincess',
                     'ClientKnocki', 'iFrostSupreme', 'Marvin__Lp', 'NQRMANY', 'NQRMAN', 'Grammatik']


def test_blank_image():
    """
    Test OCR with a blank image
    """
    blank_image = np.zeros((300, 300, 3), np.uint8)
    ocr = MinecraftScreenReader(blank_image)

    users = ocr.get_users()
    assert not users
