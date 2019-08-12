"""
OCR unit tests that can run without tesseract
"""
import cv2
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
    """
    Test user extraction logic with trailing whitespace
    """
    ocr = MinecraftScreenReader(None)
    assert ocr._extract_users_from_line("    user    ") == ["user"]


def test_user_with_teamname():
    """
    Test user extraction logic where user contains prefix of the team name
    """
    ocr = MinecraftScreenReader(None)
    assert ocr._extract_users_from_line("team:user") == ["user"]
    assert ocr._extract_users_from_line("team: user") == ["user"]
    assert ocr._extract_users_from_line("team :user") == ["user"]
    assert ocr._extract_users_from_line("team : user") == ["user"]


def test_user_with_trailing_y():
    """
    Test user extraction logic where user has a trailing 'Y' (caused by a tick on the screen)
    """
    assert MinecraftScreenReader._extract_users_from_line("usery") == ["usery", "user"]


def test_user_with_trailing_v():
    """
    Test user extraction logic where user has a trailing '<space>v' (caused by a tick on the screen)
    """
    assert MinecraftScreenReader._extract_users_from_line("user v") == ["user"]
    assert MinecraftScreenReader._extract_users_from_line("user  v") == ["user"]
    assert MinecraftScreenReader._extract_users_from_line("user   v") == ["user"]
