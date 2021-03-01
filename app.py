from __future__ import print_function
import time
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bs4 import BeautifulSoup
import requests
from twilio.rest import Client
from playsound import playsound

import sys
import secrets  # from secrets.py in this folder

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://kliu:bPmqBLLduk9aKopa@cluster0.5bddj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
mongo = PyMongo(app)

mylist = mongo.db.lists

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

def convert_string_to_url(ls):
    link_list = dict()
    for each_url in ls:
        link_string = '<div class="col-sm-3"><a href = "'
        link_string = link_string + each_url['url']
        link_string = link_string + '">'
        link_string = link_string + "URL: Track Here" + '</a></d>\n'
        link_list[each_url['_id']] = link_string
    return link_list    
    # outref = open(mytemp.htm, 'w')
    # outref.writelines(link_list)
    # outref.close()

@app.route('/')
def check_inventory():
    items = mylist.find()
    urls = convert_string_to_url(mylist.find({}, {"url": 1}))
    # print(urls, file=sys.stderr)
    # for item in items:
    #     page_html = get_page_html(item)
    #     if check_item_in_stock(page_html):
    #         send_notification(item)
    #         item.update_one({"stock": False}, {"stock": True})
    return render_template('index.html', myitems=items, tracklist=urls)

@app.route('/add', methods=['POST'])
def display():
    item_name = request.form.get("item_name")
    new_item = request.form.get("items")
    mylist.insert_one({'name': item_name, 'url' : new_item, 'stock': False, 'follow': True})
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    # while True:
    #     check_inventory()
    #     time.sleep(30)  # Wait a minute and try again
    app.run(debug=True)