import re
import cv2
import pytesseract
import logging

logger = logging.getLogger(__name__)


class MinecraftScreenReader():

    def __init__(self, image, filter="blur", show=False):
        self.raw = image
        self.clean = None
        self.filter = filter
        self.show = show

    def get_users(self):

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
