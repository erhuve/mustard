import flask
import json
import scraper
from flask import request, render_template

app = flask.Flask(__name__, template_folder='templates')
DRIVER_PATH = '/Users/pastel/Downloads/chromedriverReal'

@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        return(flask.render_template('main.html'))

    if flask.request.method ==  'POST':
        college1 = request.form['college1']
        college2 = request.form['college2']
        college1 = scraper.read_data(college1, DRIVER_PATH)
        college2 = scraper.read_data(college2, DRIVER_PATH)
        data = [college1, college2]
        return flask.render_template('main.html', result=data)



if __name__ == '__main__':
    app.run()