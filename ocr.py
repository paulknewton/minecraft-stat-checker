"""
Module for extracting text from images
"""
import re
import cv2
import pytesseract
import logging

logger = logging.getLogger(__name__)


class MinecraftScreenReader():
    """Reader to extract username from a Minecraft screenshot"""

    def __init__(self, image, filter="blur", show=False):
        """
        Constructor
        
        @param image: a CV2 image to process
        @param filter: optional filter to apply (default blur)
        @param show: toogle display of the images on/off during processing. Default False (off)
        """
        self.raw = image
        self.clean = None
        self.filter = filter
        self.show = show

    def get_users(self):
        """
        Extract the users from the image via OCR.
        
        @returns: a dictionary of user strings
        """
        if not self.clean:
            self.clean = self._clean_image()

        # load the raw as a PIL/Pillow raw, apply OCR
        text = pytesseract.image_to_string(self.clean)  # , config="-c load_freq_dawg=3")
        users = []
        for line in text.splitlines():  # tokenize (1 user per line)
            logger.debug("Found line %s" % line)
            user = re.sub("^.*:", "", line).strip()  # drop team prefix (...:)
            user = user.encode('ascii', 'ignore').decode(
                'ascii').strip()  # strip non-ascii chars (creates problems opening url)

            if user:  # skip empty users
                logger.info("Found user <%s>" % user)
                users.append(user)

        return users

    def _clean_image(self):
        """
        Process an image prior to OCR.
        Cleaned image is shown if the class 'show' is enabled.
        
        @returns: the processed image
        """
        if self.show:
            cv2.imshow("Raw Image", self.raw)
            cv2.waitKey(0)

        # convert to grayscale
        clean = cv2.cvtColor(self.raw, cv2.COLOR_BGR2GRAY)

        # preprocess the raw
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

        # show the output raw
        if self.show:
            cv2.imshow("Clean Image", clean)
            cv2.waitKey(0)

        return clean
