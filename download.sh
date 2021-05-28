#!/bin/sh
git submodule init && git submodule update
wget -np -r accept-regex 'https://dumps.wikimedia.org/enwiki/20210220/enwiki-20210220-pages-articles[0-9].*' https://dumps.wikimedia.org/enwiki/20210220/
./gather_wordfreq.py dumps.wikimedia.org/enwiki/20190320/*.bz2 > wordfreq.txt

