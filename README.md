[![Build Status](https://travis-ci.org/paulknewton/minecraft-stat-checker.svg?branch=master)](https://travis-ci.org/paulknewton/minecraft-stat-checker)
[![codecov](https://codecov.io/gh/paulknewton/minecraft-stat-checker/branch/master/graph/badge.svg)](https://codecov.io/gh/paulknewton/minecraft-stat-checker)

[![DeepSource](https://static.deepsource.io/deepsource-badge-light.svg)](https://deepsource.io/gh/paulknewton/minecraft-stat-checker/?ref=repository-badge)

# minecraft-stat-checker
Tools to extract Minecraft player names from screenshots and retrieve player statistics. Used to assess the level of your opponents before entering the game. Uses optical character recognition via Google Tesseract to extract usernames from images. Statistics retrieved from online Minecraft servers. Data is summarised using pandas dataframes and Seaborn heatmaps.

## What is it...?

Minecraft has a lot of statistics: wins, games, kills, deaths...

These statistics make a difference and help players understand who they are playing against. They can even be used to understand IF you want to play against someone. This tool allows you to get a summary of statistics for the players in a round by using a screenshot from a Minecraft game.

Let's walk through the scenario:

1. Get ready to join a Minecraft round

    Minecraft displays the players that are entering a round. This is shown at the top of the screen as list if players/teams:

    ![Screenshot](docs/screenshot.png)

1. Launch the tool

    The tool is launched (usually via a shortcut key). It prompts the user to take a screenshot of the area listing the usernames.

1. Build the stats

    The tool extracts usernames from the image using OCR (via Google Tesseract) and looks up statistics of each user (via online web services). These are displayed as a pop-up window:

    ![Statistics](docs/stats.png)

1. Make the decision. Play or pass?

    Based on the statistics of the assembled players you can decide if it makes sense to jump into the round...or move on to fight another day.

## Installing
Clone the repo and install required packages via pip:
```
pip install -r requirements.txt
```

## Using the tool
The main program is mcstats:
```
python mcstats.py
```

It supports different command line parameters:
```
python mcstats.py -h

usage: mcstats.py [-h] [--url URL] [--image IMAGE] [--filter FILTER]

check_stats

optional arguments:
  -h, --help       show this help message and exit
  --url URL        URL to retrieve statistics (will append user)
  --image IMAGE    screenshot of minecraft players
  --filter FILTER  preprocessing method that is applied to the raw image
                   during OCR
```

By default, the tool takes the input from the clipboard, unless given a file via the `--image` parameter.
A default statistics service will retrieve figures for each user, but can be overridden by the `--url`parameter.
Different filtering algorithms can be used to tune the OCR character recognition (thresh or blur). Default: blur.
