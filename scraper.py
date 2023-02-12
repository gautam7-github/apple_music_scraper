import collections
import datetime
import json
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sqlalchemy import create_engine

import domo_pusher


def startDriver(URL):
    print("Driver Starting")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)
    # driver.maximize_window()
    time.sleep(3)
    driver.get(URL)
    return driver


def collectData(driver):
    print("Collection Started")
    allSongs = driver.find_elements_by_class_name("songs-list-row")
    driver.get_screenshot_as_file("screenshot.png")
    coll = collections.defaultdict(dict)
    for index, song in enumerate(allSongs):
        songRank = song.find_element_by_class_name("songs-list-row__rank")
        coll[index]['Rank'] = songRank.text
        songName = song.find_element_by_class_name("songs-list-row__song-name")
        coll[index]['Song'] = songName.text

        songArtists = []

        allArtists = song.find_element_by_class_name(
            "songs-list__col--secondary")
        allArtists = allArtists.find_elements_by_tag_name("a")
        for artist in allArtists:
            songArtists.append(artist.text)

        coll[index]['Artist(s)'] = ','.join(songArtists)

        songAlbum = song.find_element_by_class_name(
            "songs-list__col--tertiary")
        coll[index]['Album'] = songAlbum.text
    driver.close()
    return coll


def dumpData(coll):
    print("Dump Started")
    jsonData = json.dumps(coll)
    df = pd.read_json(jsonData)
    df = df.T
    df['GYD_TIMESTAMP'] = datetime.datetime.now()
    engine = create_engine("sqlite:///database/song.db", echo=False)
    df.to_sql(
        'songs', con=engine, index=False,
        index_label='Rank', if_exists='replace'
    )
    path = "./database/songs.csv"
    df.to_csv("./database/songs.csv", index=False,)
    return path


def startCrawler(URL):
    print("Starting Scraper")
    driver = startDriver(URL)
    data = collectData(driver)
    outputPath = dumpData(data)
    dsName = "APPLE_MUSIC_TOP_100_DOMO"
    domo_pusher.pushDataToDOMO(
        dsName=dsName, dsPath=outputPath, mode='replace')
