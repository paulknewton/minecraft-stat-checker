"""
Module to create statistics for users
"""
import logging
import re
from urllib import request
import cv2
import pandas as pd
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SORRY_IMAGE_FILENAME = "sorry.png"


class MinecraftStats:
    """
    Service for retrieving Minecraft statistics for users.
    """

    def __init__(self, url="https://www.gommehd.net/player/index?playerName="):
        """
        Constructor

        @param url: the url to be used to download statistics for a user
        """
        self.url = url

    def get_stats(self, users):
        """
        Get the statistics for (1 or more) users.

        @param: user a single user string, or a list of user strings
        @return: a dictionary of statistics. 1 entry per user of the form
        'User': {'Wins': '391', 'Kills': '1259', 'Games': '1069', 'Beds destroyed': '725', 'Deaths': '712'}
        """
        if type(users) is not list:
            users = [users]  # process 1 or more users

        # get the user_stats for each user (as a dict of dicts) and build a dataframe
        all_stats = {}
        for user in users:
            all_stats[user] = self._get_stats_for_user(user)

        return all_stats
        # return self.convert_to_df(all_stats)

    def _read_stats_as_text(self, user_url):
        """
        Get statistics for a user from the service and convert them to text

        @returns: the free text containing statistics (and potentially a lot else besides)
        """
        if user_url.lower().startswith('http'):
            req = request.Request(user_url, headers={'User-Agent': 'Mozilla/5.0'})
        else:
            raise ValueError from None

        with request.urlopen(req) as resp:
            text = BeautifulSoup(resp).get_text()
            # with open("out.txt", "w") as text_file:
            #   text_file.write(text)

            return text

    def _get_stats_for_user(self, user):
        """
        Get the statistics for a given user. Raw statistics text is extracted via the _read_stats_as_text method.
        Actual statistics are extracted using regular expressions.

        @param user: the user @returns: a dictionary of statistics of the form 'User': {'Wins': '391',
        'Kills': '1259', 'Games': '1069', 'Beds destroyed': '725', 'Deaths': '712'}
        """
        user_url = self.url + user
        logger.info("Retrieving stats for user <%s>", user)
        logger.debug("Opening %s", user_url)

        raw = self._read_stats_as_text(user_url)
        logger.debug(raw)

        # find the section in the page between "BedWars" and "SkyWars"
        regex = re.compile("%s.*%s" % ("BedWars", "SkyWars"), flags=re.DOTALL)
        results = regex.search(raw)

        if not results:
            logger.debug("Did not find results")
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

    def get_stats_df(self, users):
        """        
        Get the statistics for (1 or more) users as a pandas dataframe.

        @param: user a single user string, or a list of user strings
        @return: a dataframe of statistics with columns 'Wins', 'Kills', 'Games', 'Beds destroyed', 'Deaths', 'K/D'
        """
        all_stats = self.get_stats(users)

        # strip out the column names
        df_columns = ["Wins", "Kills", "Games", "Beds destroyed", "Deaths", "K/D"]
        df_data = {}
        for user, stats in all_stats.items():
            if stats.keys():
                logger.debug("Adding user %s: %s", user, stats)
                # df_columns = list(stats.keys())
                # logger.debug("Columns = %s" % df_columns)
                user_data = list(stats.values())

                # calculate the kill ratio
                kills = int(stats["Kills"])
                deaths = int(stats["Deaths"])
                if deaths == 0:
                    kd = 0
                else:
                    kd = round(kills / deaths, 2)

                user_data.append(kd)
                # df_columns.append("K/D")
                df_data[user] = user_data
            else:
                logger.debug("Adding unknown user %s", user)
                df_data[user] = [None] * len(df_columns)

        logger.debug(df_data)
        return pd.DataFrame.from_dict(df_data, orient="index", columns=df_columns).sort_values(
            df_columns[len(df_columns) - 1])

    @staticmethod
    def plot_table(df):
        """
        Static method to display a statistics dataframe (returned by the get_stats_df method. Table shown as a grid
        using the seaborn heatmap feature

        @param df: the dataframe to display
        """

        # seaborn heatmap cannot handle empty data
        if df.empty or df.isnull().to_numpy().all():
            cv2.imshow("Sorry", cv2.imread(SORRY_IMAGE_FILENAME))
            cv2.waitKey(0)
            return

        import seaborn as sns
        sns.set(style="darkgrid")
        import matplotlib.pyplot as plt
        # from matplotlib.colors import ListedColormap

        df = df.apply(pd.to_numeric)
        plt.figure(facecolor='w', edgecolor='k')
        # sns.heatmap(df, annot=True, cmap=ListedColormap(['white']), cbar=False, fmt='g')
        sns.heatmap(df, annot=True, cmap="Blues", cbar=False, fmt='g', linewidths=3)
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig("stats.png", bbox_inches='tight')
        plt.show()
