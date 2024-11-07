# Apple price parser
## _Maksimov A.V._

Apple price parser is a tool for parsing prices in Apple hardware stores.

## Features

- Uses BeautifulSoup4
- Works with Google Sheets
- Regular execution scripts configured


## Tech

Parser uses a number of open source projects to work properly:

- [gspread] - Working with Google Sheets
- [Advanced Python Scheduler] - Runs parser at certain time
- [BeautifulSoup4] - Scrapping web pages.

to Markdown converter
- [jQuery] - duh

And of course Apple price parser itself is open source with a [public repository][repo]
 on GitHub.

## Installation

Parser requires [Python](https://www.python.org/downloads/) 3.11.2+ to run.

Clone repo:
```powershell
git clone https://github.com/DuhastMish/apple-price-parser.git
```

Make authentification to Google Sheets API using [this instructuction](https://docs.gspread.org/en/latest/oauth2.html)
And put your credentials.json into root dir.

Dont forget to change your TABLE_KEY in `sheet\main.py`

Runs app using `main.py`

*NOTE!*
In file `utils\scheduler.py` file you can configure the time when to parse prices.

## License

MIT

**Free Software, Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [repo]: <https://github.com/DuhastMish/apple-price-parser>
   [gspread]: <https://docs.gspread.org/en/v6.1.3/>
   [Advanced Python Scheduler]: <https://apscheduler.readthedocs.io/en/3.x/index.html>
   [BeautifulSoup4]: <https://www.crummy.com/software/BeautifulSoup/>
