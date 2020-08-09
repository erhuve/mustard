import flask
import json
import pandas as pd
from compareColleges import compare
from flask import request, render_template

app = flask.Flask(__name__, template_folder='templates')
DRIVER_PATH = '/Users/pastel/Downloads/chromedriverReal'
with open('links.json') as json_file:
    links= json.load(json_file)

@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        colleges = links.keys()
        return(flask.render_template('main.html', colleges1=colleges, colleges2=colleges))

    if flask.request.method ==  'POST':
        colleges = links.keys()
        college1 = request.form['colleges1']
        college2 = request.form['colleges2']
        df = compare(college1, college2, DRIVER_PATH, True)
        # df = df.T
        return flask.render_template('main.html', tables=[df.to_html(classes='data', header="true")], colleges1=colleges, colleges2=colleges)



if __name__ == '__main__':
    app.run()