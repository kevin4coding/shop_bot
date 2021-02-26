import time
from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
from twilio.rest import Client
from playsound import playsound

import secrets  # from secrets.py in this folder

app = Flask(__name__)

def get_page_html(url):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"}
    page = requests.get(url, headers=headers)
    return page.content


def check_item_in_stock(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')
    out_of_stock_divs = soup.findAll("img", {"class": "oos-overlay hide"})
    return len(out_of_stock_divs) != 0

def setup_twilio_client():
    account_sid = secrets.TWILIO_ACCOUNT_SID
    auth_token = secrets.TWILIO_AUTH_TOKEN
    return Client(account_sid, auth_token)

def send_notification(item):
    twilio_client = setup_twilio_client()
    twilio_client.messages.create(
        body=f"Your item {item} is available for purchase.",
        from_=secrets.TWILIO_FROM_NUMBER,
        to=secrets.MY_PHONE_NUMBER
    )
    while True:
        playsound('alarm.mp3')

def check_inventory():
    urls = ["https://www.costco.com/sk-ii-facial-treatment-essence-with-pump,-11.0-fl-oz.product.100287232.html", "https://www.costco.com/la-mer-creme-de-la-mer,-2.0-oz.product.100372155.html"]
    item = 0
    for url in urls:
        item=item+1
        page_html = get_page_html(url)
        if check_item_in_stock(page_html):
            send_notification(item)
        else:
            print(f"Item {item} Out of stock still")

@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    while True:
        check_inventory()
        time.sleep(30)  # Wait a minute and try again
    app.run(debug=True)