import re
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class MinecraftStats:

    def __init__(self, url="https://www.gommehd.net/player/index?playerName="):
        self.url = url  # url used to retrieve statistics

    def get_stats(self, users):

        if type(users) is not list: users = [users]  # process 1 or more users

        # get the user_stats for each user (as a dict of dicts) and build a dataframe
        all_stats = {}
        for user in users:
            all_stats[user] = self._get_stats_for_user(user)

        return all_stats
        # return self.convert_to_df(all_stats)

    def _read_stats_as_text(self, url):
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        text = BeautifulSoup(html).get_text()
        #with open("out.txt", "w") as text_file:
        #   text_file.write(text)

        return text

    def _get_stats_for_user(self, user):
        user_url = self.url + user
        logger.debug("Opening %s" % user_url)

        raw = self._read_stats_as_text(user_url)
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

    def get_stats_df(self, users):

        all_stats = self.get_stats(users)

        # strip out the column names
        df_columns = ["Wins", "Kills", "Games", "Beds destroyed", "Deaths", "K/D"]
        df_data = {}
        for user, stats in all_stats.items():
            if stats.keys():
                logger.debug("Adding user %s: %s" % (user, stats))
                # df_columns = list(stats.keys())
                # logger.debug("Columns = %s" % df_columns)
                user_data = list(stats.values())
                user_data.append(round(int(stats["Kills"]) / int(stats["Deaths"]), 2))
                # df_columns.append("K/D")
                df_data[user] = user_data
            else:
                logger.debug("Adding unknown user %s" % user)
                df_data[user] = [None] * len(df_columns)

        logger.debug(df_data)
        return pd.DataFrame.from_dict(df_data, orient="index", columns=df_columns).sort_values(
            df_columns[len(df_columns) - 1])

    @staticmethod
    def plot_table(df):
        import seaborn as sns
        import matplotlib.pyplot as plt

        plt.figure(facecolor='w', edgecolor='k')
        sns.heatmap(df.head(), annot=True, cmap='viridis', cbar=False)
        plt.show()
