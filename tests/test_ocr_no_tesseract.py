"""
OCR unit tests that can run without tesseract
"""
import cv2
import numpy as np
from ocr import MinecraftScreenReader


def test_empty_image():
    """
    Test OCR with a missing image.
    """
    img = cv2.imread("tests/THIS_DOES_NOT_EXIT.png")
    ocr = MinecraftScreenReader(img)

    users = ocr.get_users()
    assert not users


def test_user_with_whitespace():
    ocr = MinecraftScreenReader(None)
    assert ocr._strip_user_from_line("    user    ") == "user"

def test_user_with_teamname():
    ocr = MinecraftScreenReader(None)
    assert ocr._strip_user_from_line("team:user") == "user"
    assert ocr._strip_user_from_line("team: user") == "user"
    assert ocr._strip_user_from_line("team :user") == "user"
    assert ocr._strip_user_from_line("team : user") == "user"

def test_user_with_trailing_v():
    ocr = MinecraftScreenReader(None)

    assert ocr._strip_user_from_line("user v") == "user"