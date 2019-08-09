"""
Module for extracting text from images
"""
import re
import cv2
import pytesseract
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

RAW_IMAGE_FILENAME = "screenshots/clipboard.png"
CLEAN_IMAGE_FILENAME = "screenshots/clean.png"


class MinecraftScreenReader:
    """Reader to extract username from a Minecraft screenshot"""

    def __init__(self, image, image_filter="blur"):
        """
        Constructor

        @param image: a CV2 image to process
        @param image_filter: optional filter to apply (default blur)
        """
        self.raw = image
        self.clean = None
        self.filter = image_filter

        if self.raw is not None:
            cv2.imwrite(RAW_IMAGE_FILENAME, self.raw)

    def get_users(self):
        """
        Extract the users from the image via OCR.

        @returns: a dictionary of user strings
        """

        # no need to continue if image is empty
        if self.raw is None:
            return []

        # lazy cleaning of the image
        if not self.clean:
            self.clean = self._clean_image()

        # load the raw as a PIL/Pillow raw, apply OCR
        text = pytesseract.image_to_string(self.clean)

        # iterate through the results, cleaning whitespace
        users = []
        for line in text.splitlines():  # tokenize (1 user per line)
            logger.debug("Found line %s", line)
            user = self._strip_user_from_line(line)

            if user:  # skip empty users
                logger.info("Found user <%s>", user)
                users.append(user)

        return users

    def _strip_user_from_line(self, line):
        # drop team prefix (...:)
        user = re.sub("^.*:", "", line).strip()

        # strip non-ascii chars (creates problems opening url)
        user = user.encode('ascii', 'ignore').decode(
            'ascii').strip()

        # TODO remove trailing v as this is used by Minecraft as a marker
        user = re.sub(" *v$", "", user)

        return user

    def _clean_image(self):
        """
        Process an image prior to OCR.

        @returns: the processed image
        """

        # convert to grayscale
        clean = cv2.cvtColor(self.raw, cv2.COLOR_BGR2GRAY)

        # pre-process the raw image
        if self.filter == "thresh":
            clean = cv2.threshold(clean, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # blur the raw to remove noise
        elif self.filter == "blur":
            clean = cv2.medianBlur(clean, 3)

        # black on white gives better results with tesseract
        clean = cv2.bitwise_not(clean)

        # add a white border (to help tesseract)
        border = 10
        clean = cv2.copyMakeBorder(clean, border, border, border, border, cv2.BORDER_CONSTANT, None, [255, 255, 255])

        # save (useful for debugging)
        cv2.imwrite(CLEAN_IMAGE_FILENAME, clean)

        return clean
