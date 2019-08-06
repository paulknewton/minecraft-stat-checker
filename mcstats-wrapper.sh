#! /bin/sh

PATH=/usr/local/sbin:/usr/local/bin:$PATH

# load virtualenv
echo "Loading python virtualenv..."
. ./activate

# reads from the clipboard
python3 mcstats.py --filter blur --url "https://www.gommehd.net/player/index?playerName="
read key
exit 0

