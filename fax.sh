#!/bin/bash
cat splash.md
echo Faxing...
cat splash.md | lp -o cpi=10 -o lpi=10 -o DocCutType=0NoCutDoc
python3 read_gmail_inbox.py | lp -o cpi=6 -o lpi=6 -o
echo Faxed.
