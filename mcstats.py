import argparse
import logging
import pandas as pd
import cv2
import numpy
from PIL import ImageGrab

from ocr import MinecraftScreenReader
from statistics import MinecraftStats

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':

    # read command-line args
    parser = argparse.ArgumentParser(
        description="check_stats")
    parser.add_argument("--url", help="URL to retrieve statistics (will append user)")
    parser.add_argument("--image", help="screenshot of minecraft players")
    parser.add_argument("--filter", type=str, default="blur",
                        help="preprocessing method that is applied to the raw image during OCR")
    args = parser.parse_args()
    print(args)

    # load the minecraft screenshot from an existing file (if specified) or grab screen
    if args.image:
        raw = cv2.imread(args.image)
    else:
        raw = ImageGrab.grabclipboard()
        raw.save("screenshots/clipboard.png")
        raw = cv2.cvtColor(numpy.array(raw), cv2.COLOR_RGB2BGR)

    # extract the users
    image_rdr = MinecraftScreenReader(raw, filter=args.filter, show=False)
    users = image_rdr.get_users()
    print("Users: ", users)

    #sys.exit(1)

    # Get the stats. Use the provided url to get stats if provided, otherwise use the default.
    if args.url:
        stats_reader = MinecraftStats(args.url)
    else:
        stats_reader = MinecraftStats()
    stats = stats_reader.get_stats_df(users)
    print(stats)

    if stats.empty or stats.isnull().to_numpy().all():
        cv2.imshow("Sorry", cv2.imread("sorry.png"))
        cv2.waitKey(0)
    else:
        stats_reader.plot_table(stats)
