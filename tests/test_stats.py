from statistics import MinecraftStats
import pytest
import mock
import pandas


@pytest.fixture
def grammatik():
    # test data
    grammatik_dict = {
        'Grammatik': {'Wins': '391', 'Kills': '1259', 'Games': '1069', 'Beds destroyed': '725', 'Deaths': '712'}}

    # in dataframe form
    df_columns = list(grammatik_dict["Grammatik"].keys())
    df_columns.append("K/D")
    df_data = list(grammatik_dict["Grammatik"].values())
    df_data.append(round(int(grammatik_dict["Grammatik"]["Kills"]) / int(grammatik_dict["Grammatik"]["Deaths"]), 2))
    grammatik_df = pandas.DataFrame.from_dict({"Grammatik": df_data}, orient="index", columns=df_columns)

    # sample stats text data (from a file)
    with open("tests/grammatik_stats.txt", "r") as text_file:
        dummy_stats_text = text_file.read()

    return [
        grammatik_dict,
        grammatik_df,
        dummy_stats_text
    ]


@mock.patch("statistics.MinecraftStats._read_stats_as_text")
def test_single_lookup(mock_read_stats_as_text, grammatik):
    user = next(iter(grammatik[0]))

    stats_reader = MinecraftStats()

    # configure mock class to return hard-coded stats text
    mock_read_stats_as_text.return_value = grammatik[2]

    stats = stats_reader.get_stats(user)
    assert stats == grammatik[0]

    stats_df = stats_reader.get_stats_df(user)
    assert stats_df.equals(grammatik[1])


@mock.patch("statistics.MinecraftStats._read_stats_as_text")
def test_multi_lookup(mock_read_stats_as_text, grammatik):
    user = next(iter(grammatik[0]))

    stats_reader = MinecraftStats()

    # configure mock class to return hard-coded stats text
    mock_read_stats_as_text.return_value = grammatik[2]

    # build a list of users
    num_users = 5
    users = [""] * num_users
    user = next(iter(grammatik[0]))
    for i in range(0, len(users)):
        users[i] = user + "_" + str(i)

    # build multi-row dataframe
    df = grammatik[1].reset_index()
    multi_df = df.copy()
    multi_df["index"] = users[0]
    for i in range(1, len(users)):
        df["index"] = users[i]
        multi_df = multi_df.append(df)
    multi_df.set_index("index", inplace=True)

    # check stats
    stats = stats_reader.get_stats(users)
    for user in users:
        assert stats[user] == grammatik[0]["Grammatik"]

    # check stats as df
    stats_df = stats_reader.get_stats_df(users)
    assert stats_df.equals(multi_df)

    #stats_reader.plot_table(stats_df)
