# Import necessary modules
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup as bs
import pandas as pd

# Create a Flask application
application = Flask(__name__)
app = application


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/api/videos', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():

    # Initialize a headless browser using Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run the browser in headless mode
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    if request.method == 'POST':
        try:
            
            # Load the YouTube channel URL
            searchString = request.form['content'].replace(" ", "-")
            Channel_URL = " https://www.youtube.com/@" + searchString + "/videos"
            print("Channel URL :-", Channel_URL)
            driver.get(Channel_URL)
            time.sleep(0)  # Let the page load

            # Scroll down to load more videos (adjust the number of scrolls as needed)
            scrolls = 3
            for _ in range(scrolls):
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(0)

            # Get the page source after scrolling
            Channel_Page = driver.page_source

            # Close the browser
            driver.quit()

            # Now you can use BeautifulSoup to parse the loaded content
            Channel_HTML = bs(Channel_Page, 'html.parser')

            # BigBox for Video URL & Video Thumbnail
            BigBox_UT = Channel_HTML.findAll("ytd-thumbnail", {"class": "style-scope ytd-rich-grid-media"})

            # Video Title
            BigBox_Title = Channel_HTML.findAll("a", {
                "class": "yt-simple-endpoint focus-on-expand style-scope ytd-rich-grid-media"})
            
            Videos_Title = []
            for T in BigBox_Title:
                title = T.text
                Videos_Title.append(title)

            # BigBox for Video URL & Video Thumbnail
            BigBox_UT = Channel_HTML.findAll("ytd-thumbnail", {"class": "style-scope ytd-rich-grid-media"})

            # Video URL
            Videos_URL = []
            for U in BigBox_UT:
                url = "https://www.youtube.com" + U.a['href']
                Videos_URL.append(url)

            # Video Thumbnail
            Thumbnail_URL = []
            for Th in BigBox_UT[0:10]:
                thumbnail = Th.img['src']
                Thumbnail_URL.append(thumbnail)

            Videos_Thumbnail = []
            for i in Thumbnail_URL:
                parsed_url = urlparse(i)
                cleaned_url = urlunparse(parsed_url._replace(query=""))
                Videos_Thumbnail.append(cleaned_url)

            # BigBox for Video View_Count & Video Uploaded

            # Video Count
            BigBox_View_Count = Channel_HTML.findAll("span", {"class": "inline-metadata-item style-scope ytd-video-meta-block"})
            Videos_Viewcount = []
            for Vid_Count in BigBox_View_Count[0::2]:
                View_Count = Vid_Count.text
                Videos_Viewcount.append(View_Count)

            # Video Uploaded
            BigBox_Upload = Channel_HTML.findAll("span", {"class": "inline-metadata-item style-scope ytd-video-meta-block"})
            Videos_Uploaded = []
            for Vid_Upload in BigBox_Upload[1::2]:
                Uploaded = Vid_Upload.text
                Videos_Uploaded.append(Uploaded)
            
            # Replace the print statements with the response data
            # Create an empty list to store video data dictionaries
            Videos_Data = []

            # Loop through the videos and collect data in dictionaries
            for title, thumbnail, url, viewcount, uploaded in zip(Videos_Title, Videos_Thumbnail, Videos_URL, Videos_Viewcount, Videos_Uploaded):
                video_data = {
                    "Videos_Title": title,
                    "Videos_Thumbnail": thumbnail,
                    "Videos_URL": url,
                    "Videos_Viewcount": viewcount,
                    "Videos_Uploaded": uploaded
                }
                Videos_Data.append(video_data)

            # Create a DataFrame from the list of video data dictionaries
            df = pd.DataFrame(Videos_Data)

            # Save the DataFrame to a CSV file
            filename = searchString + ".csv"
            df.to_csv(filename, index=False)


            return render_template('result.html', reviews=Videos_Data)

        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'


if __name__ == "__main__":
    app.run()