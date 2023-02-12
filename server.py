import threading
import time

import schedule
from flask import Flask, render_template, request

import scraper

app = Flask(__name__)


@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/playlist", methods=['POST'])
def playlist():
    if request.method == "POST":
        print(request.form['URL'])
        scraper.startCrawler(request.form['URL'])
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
