from ocr import MinecraftScreenReader
import cv2


def test_ocr():
    img = cv2.imread("screenshots/test4_crop.png")
    ocr = MinecraftScreenReader(img)

    users = ocr.get_users()
    assert users == ['_byF3l1lx_', 'Sternlicht', 'dramatc', 'StegobertFanyboy', 'UnwichtigsDing', 'lolmcOO1',
                    'PrestigePrincess',
                    'ClientKnocki', 'iFrostSupreme', 'Marvin__Lp', 'NQRMANY', 'Grammatik']
