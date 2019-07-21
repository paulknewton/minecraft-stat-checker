import argparse
import logging
import os
import cv2
import pytesseract
import re

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_users(image):
    # load the image as a PIL/Pillow image, apply OCR
    text = pytesseract.image_to_string(image)
    users = []
    for line in text.splitlines():
        logger.debug("Found line %s" % line)
        user = re.sub("^.*:", "", line).strip()
        logger.info("Found user <%s>" % user)

        if user:  # skip empty users
            users.append(user)

    return users


def clean_image(image, preprocess):
    # convert to grayscale
    clean = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # preprocess the image
    if preprocess == "thresh":
        clean = cv2.threshold(clean, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # blur the image to remove noise
    elif preprocess == "blur":
        clean = cv2.medianBlur(clean, 3)

    return clean


if __name__ == '__main__':

    # read command-line args
    parser = argparse.ArgumentParser(
        description="check_stats")
    parser.add_argument("input", help="screenshot of minecraft players")
    parser.add_argument("-p", "--preprocess", type=str, default="thresh",
                        help="preprocessing method that is applied to the image")
    parser.add_argument("-s", "--save", help="save the intermediate processed image", action="store_true",
                        default=False)
    args = parser.parse_args()
    print(args)

    # load the minecraft screenshot
    raw = cv2.imread(args.input)

    clean = clean_image(raw, args.preprocess)

    # write the new grayscale image to disk
    if args.save:
        filename = "{}.png".format(os.getpid())
        cv2.imwrite(filename, clean)

    # show the output image
    # cv2.imshow("Image", image)
    # cv2.imshow("Output", grey)
    # cv2.waitKey(0)

    users = get_users(clean)
    print(users)
