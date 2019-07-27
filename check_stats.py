import argparse
import logging
import os
import cv2
import pytesseract
import re
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd
import matplotlib.pyplot as plt
import pyautogui
import numpy

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


def get_users(image):
    # load the image as a PIL/Pillow image, apply OCR
    text = pytesseract.image_to_string(image) #, config="-c load_freq_dawg=3")
    users = []
    for line in text.splitlines():  # tokenize (1 user per line)
        logger.debug("Found line %s" % line)
        user = re.sub("^.*:", "", line).strip()     # drop team prefix (...:)
        user = user.encode('ascii', 'ignore').decode('ascii').strip()   # strip non-ascii chars (creates problems opening url)

        if user:  # skip empty users
            logger.info("Found user <%s>" % user)
            users.append(user)

    return users


def clean_image(image, preprocess):

    cv2.imshow("Image", image)
    cv2.waitKey(0)

    # convert to grayscale
    clean = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # preprocess the image
    if preprocess == "thresh":
        clean = cv2.threshold(clean, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # blur the image to remove noise
    elif preprocess == "blur":
        clean = cv2.medianBlur(clean, 3)

    # black on white gives better results with tesseract
    clean = cv2.bitwise_not(clean)

    # add a white border (to help tesseract)
    border = 10
    clean = cv2.copyMakeBorder(clean, border, border, border, border, cv2.BORDER_CONSTANT, None, [255,255,255])

    # show the output image
    cv2.imshow("Output", clean)
    cv2.waitKey(0)

    return clean


def get_stats(user, url):
    logger.debug("Opening %s" % url)

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read()
    raw = BeautifulSoup(html).get_text()

    # print(raw)

    # find the section in the page between "BedWars" and "SkyWars"
    regex = re.compile("%s.*%s" % ("BedWars", "SkyWars"), flags=re.DOTALL)
    results = regex.search(raw)

    if not results:
        return {}

    stats_text = results.group()
    logger.debug(stats_text)

    # convert to a list, but drop all the empty entries caused by blank lines
    stats_list = [x for x in stats_text.split("\n") if x]

    # drop the title and next title
    stats_list = stats_list[1:-1]

    # populate a dictionary based on the pairwise entries (entries appear in the reverse order)
    stats_dict = {}
    for i in range(0, len(stats_list) - 1, 2):
        stats_dict[stats_list[i + 1].strip()] = stats_list[i].strip()
    logger.debug(stats_dict)

    return stats_dict


def plot_table(df):
    fig = plt.figure()
    plt.subplot(121)
    plt.table(cellText=df.values, colLabels=df.columns, loc='center')
    plt.axis('off')
    plt.axis('tight')
    fig.tight_layout()
    plt.show()


if __name__ == '__main__':

    # read command-line args
    parser = argparse.ArgumentParser(
        description="check_stats")
    parser.add_argument("-iu", "--url", help="URL to retrieve statistics (will append user)")
    parser.add_argument("-i", "--input", help="screenshot of minecraft players")
    parser.add_argument("-p", "--preprocess", type=str, default="thresh",
                        help="preprocessing method that is applied to the image")
    parser.add_argument("-s", "--save", help="save the intermediate processed image", action="store_true",
                        default=False)
    args = parser.parse_args()
    print(args)

    # load the minecraft screenshot from existing file (if specified) or grab screen
    if args.input:
        raw = cv2.imread(args.input)
    else:
        #raw = ImageGrab.grab()
        raw = pyautogui.screenshot()
        raw.save("screenshot.png")
        raw = cv2.cvtColor(numpy.array(raw), cv2.COLOR_RGB2BGR)

    clean = clean_image(raw, args.preprocess)

    # write the new cleaned image to disk?
    if args.save:
        filename = "{}.png".format(os.getpid())
        cv2.imwrite(filename, clean)

    # extract the get_users
    users = get_users(clean)
    print("Users: ", users)

    # get the user_stats for each user (as a dict of dicts) and build a dataframe
    all_stats = {}
    for user in users:
        all_stats[user] = get_stats(user, args.url + user)

    logger.info(all_stats)

    # strip out the column names
    df_columns = ["Wins", "Kills", "Games", "Beds destroyed", "Deaths", "K/D"]
    df_data = {}
    for user, stats in all_stats.items():
        if stats.keys():
            logger.debug("Adding user %s: %s" % (user, stats))
            #df_columns = list(stats.keys())
            #logger.debug("Columns = %s" % df_columns)
            user_data = list(stats.values())
            user_data.append(round(int(stats["Kills"]) / int(stats["Deaths"]), 2))
            # df_columns.append("K/D")
            df_data[user] = user_data
        else:
            logger.debug("Adding unknown user %s" % user)
            df_data[user] = [None] * len(df_columns)

    logger.debug(df_data)
    df = pd.DataFrame.from_dict(df_data, orient="index", columns=df_columns).sort_values(df_columns[len(df_columns) - 1])
    print(df)

    #plot_table(df)

    cv2.waitKey(0)
