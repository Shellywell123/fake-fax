#!/bin/bash
cat splash.md
echo Faxing...
cat splash.md | lp -o cpi=10 -o lpi=10 -o DocCutType=0NoCutDoc
date | lp -d STAR
python3 read_gmail_inbox.py | lp -o cpi=3 -o lpi=3
echo Faxed.
