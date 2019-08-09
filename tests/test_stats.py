from statistics import MinecraftStats
import pytest
import mock
import pandas


@pytest.fixture
def grammatik():
    """
    Fixture data for unit tests
    """
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

    # sample stats text data (from a file)
    with open("tests/grammatik_invalid_stats.txt", "r") as text_file:
        dummy_invalid_stats_text = text_file.read()

    # dataframe if stats cannot be retrieved

    return [
        grammatik_dict,
        grammatik_df,
        dummy_stats_text,
        dummy_invalid_stats_text
    ]


@mock.patch("statistics.MinecraftStats._read_stats_as_text")
def test_single_lookup(mock_read_stats_as_text, grammatik):
    """
    Test lookup of stats for a single user (with dummy statistics service)
    :param mock_read_stats_as_text: mock stats reading function
    :param grammatik: fixture data
    """
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
    """
    Test lookup of stats for multiple users (with dummy statistics service)
    :param mock_read_stats_as_text: mock stats reading function
    :param grammatik: fixture data
    """
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
    assert len(stats) == len(users)
    for user in users:
        assert stats[user] == grammatik[0]["Grammatik"]

    # check stats as df
    stats_df = stats_reader.get_stats_df(users)
    assert stats_df.equals(multi_df)


@mock.patch("statistics.MinecraftStats._read_stats_as_text")
def test_zero_deaths(mock_read_stats_as_text):
    """
    Test lookup for a user with zero deaths (avoid divide by zero)
    :param mock_read_stats_as_text: mock stats reading function
    :param grammatik: fixture data
    """
    # test data
    grammatik_dict = {
        'Grammatik0': {'Wins': '391', 'Kills': '1259', 'Games': '1069', 'Beds destroyed': '725', 'Deaths': '0'}}

    # in dataframe form
    df_columns = list(grammatik_dict["Grammatik0"].keys())
    df_columns.append("K/D")
    df_data = list(grammatik_dict["Grammatik0"].values())
    df_data.append(0)
    grammatik_df = pandas.DataFrame.from_dict({"Grammatik0": df_data}, orient="index", columns=df_columns)

    # sample stats text data (from a file)
    with open("tests/grammatik_zero_deaths_stats.txt", "r") as text_file:
        dummy_stats_text = text_file.read()

    # configure mock class to return hard-coded stats text
    stats_reader = MinecraftStats()
    mock_read_stats_as_text.return_value = dummy_stats_text

    stats = stats_reader.get_stats("Grammatik0")
    assert stats == grammatik_dict

    stats_df = stats_reader.get_stats_df("Grammatik0")
    assert stats_df.equals(grammatik_df)


def test_invalid_url(grammatik):
    """
    Test lookup with a non-http protocol in the URL
    :param grammatik: fixture data
    :return:
    """
    user = next(iter(grammatik[0]))

    with pytest.raises(ValueError):
        stats_reader = MinecraftStats("file://this_protocol_not_supported")
        stats_reader.get_stats(user)


@mock.patch("statistics.MinecraftStats._read_stats_as_text")
def test_invalid_stats(mock_read_stats_as_text, grammatik):
    """
    Test lookup of stats where the returned text does not include the required tokens to extract the figures
    :param mock_read_stats_as_text: mock stats reading function
    :param grammatik: fixture data
    """
    user = next(iter(grammatik[0]))

    stats_reader = MinecraftStats()

    # configure mock class to return hard-coded (invalid) stats text
    mock_read_stats_as_text.return_value = grammatik[3]

    stats = stats_reader.get_stats(user)
    assert stats == {'Grammatik': {}}  # no stats

    df_columns = list(grammatik[0][user].keys())
    df_columns.append("K/D")
    df_invalid_data = [None] * len(df_columns)
    grammatik_invalid_df = pandas.DataFrame.from_dict({"Grammatik": df_invalid_data}, orient="index",
                                                      columns=df_columns)
    print(grammatik_invalid_df)

    stats_df = stats_reader.get_stats_df(user)
    assert stats_df.equals(grammatik_invalid_df)
