import threading
import time

import schedule
from flask import Flask, render_template

import scraper

app = Flask(__name__)


@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html")


def runScraper():
    print("Triggered Scraper")
    URL = "https://music.apple.com/kw/playlist/top-100-india/pl.c0e98d2423e54c39b3df955c24df3cc5"
    schedule.every(15).seconds.do(scraper.startCrawler, URL=URL)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    flaskThread = threading.Thread(target=app.run)
    scraperThread = threading.Thread(target=runScraper)
    flaskThread.start()
    scraperThread.start()
