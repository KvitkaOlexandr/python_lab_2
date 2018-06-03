from flask import Flask, render_template, request
from pymongo import MongoClient
from db import Mongo_URL
import json
import subprocess

app = Flask(__name__)
client = MongoClient(Mongo_URL)
lim = 30


@app.route('/')
def index():
    page = request.args.get('page')
    if page is None:
        page = 0
    data = client.lab_2.data.find().skip(int(page) * lim).limit(lim)
    pages = client.lab_2.data.count() // lim
    return render_template('index.html', data=[d for d in data], page=int(page), pages=pages)


@app.route('/<topic>/<author>')
def topic_author(topic, author):
    data = client.lab_2.data
    rec = data.find({'topic': topic, 'author': author})
    author_messages_count = data.count({'topic': topic, 'author': author})
    topic_messages_count = data.count({'topic': topic})
    print(topic_messages_count)
    return render_template('authors.html', data=[d for d in rec], author_messages_count=author_messages_count,
                           topic_messages_count=topic_messages_count)


@app.route('/add')
def add():
    #spider_name = "coin_spider.py"
    #subprocess.check_output(['scrapy', 'runspider', spider_name, "-o", "out.json"])
    with open("out.json") as items_file:
        res = json.loads(items_file.read())
        for r in res:
            client.lab_2.data.insert(r)
    client.close()
    return '-'


if __name__ == '__main__':
    app.run()
