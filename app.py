import flask
import json
import pandas as pd
from compareCollegesFirebase import getDataForCollege, calculate, coldRecommend, getAllCollegeDicts, getUniqueMajors
from flask import request, render_template

app = flask.Flask(__name__, template_folder='templates')
DRIVER_PATH = '/Users/pastel/Downloads/chromedriverReal'
with open('links.json') as json_file:
    links= json.load(json_file)

@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        colleges = links.keys()
        fieldlist = getUniqueMajors()
        return(flask.render_template('main.html', colleges1=colleges, colleges2=colleges, fieldlist=fieldlist))

    if flask.request.method ==  'POST':
        colleges = links.keys()
        fieldlist = getUniqueMajors()
        college1 = request.form['colleges1']
        college2 = request.form['colleges2']

        field = request.form['field']
        salary = request.form['salary']
        cost = request.form['cost']
        diversity = False
        if request.form['diverse'] == 'diverse':
            diversity = True

        public = []
        if request.form.get('public'):
            public.append('Public')
        if request.form.get('private'):
            public.append('Private')
        if request.form.get('forprofit'):
            public.append('For-Profit')

        size = []
        if request.form.get('small'):
            size.append('Small')
        if request.form.get('medium'):
            size.append('Medium')
        if request.form.get('large'):
            size.append('Large')

        urbanicity = []
        if request.form.get('city'):
            urbanicity.append('City')
        if request.form.get('suburban'):
            urbanicity.append('Suburban')
        if request.form.get('town'):
            urbanicity.append('Town')
        if request.form.get('rural'):
            urbanicity.append('Rural')

        if request.form.get('cold'):
            recs = coldRecommend(getAllCollegeDicts(), 5, field, salary, cost, diversity, size, urbanicity, public)
            res = 'Our recommendations for you: '
            for rec in recs:
                res += '---' + rec + '--- '
            if len(recs) < 1:
                res = 'We couldn\'t find a match for you. :('
            return(flask.render_template('main.html', colleges1=colleges, colleges2=colleges, result=res, fieldlist=fieldlist))


        c1_dict = getDataForCollege(college1)
        c2_dict = getDataForCollege(college2)
        df = pd.DataFrame([c1_dict, c2_dict]).T
        college_list = [c1_dict, c2_dict]

        scores = calculate(college_list, field, salary, cost, diversity, size, urbanicity, public)
        scores_sum = [0,0]
        if type(scores[0][0]) is not str:
            for score in scores[0]:
                scores_sum[0] += score
            if not diversity:
                scores_sum[0] -= scores[0][3]
            
        if type(scores[1][0]) is not str:
            for score in scores[1]:
                scores_sum[1] += score
            if not diversity:
                scores_sum[1] -= scores[1][3]
        
        winner_index = 0
        if scores_sum[1] > scores_sum[0]:
            winner_index = 1
        
        recommendation = 'Our recommendation: ' + college_list[winner_index]['name']
        if not diversity:
            recommendation += ' (Diversity score was calculated but not included in the total)'

        score_df = pd.DataFrame([['Total score', scores_sum[0], scores_sum[1]],
                    ['Field of study score',scores[0][0],scores[1][0]],
                    ['Salary score',scores[0][1],scores[1][1]],
                    ['Cost score',scores[0][2],scores[1][2]],
                    ['Diversity score',scores[0][3],scores[1][3]],
                    ['Size score',scores[0][4],scores[1][4]],
                    ['Urbanicity score',scores[0][5],scores[1][5]],
                    ['Public/Private score',scores[0][6],scores[1][6]]],
                    columns = ['Criteria', college1, college2])
        # df = df.T
        return flask.render_template('main.html', tables=[df.to_html(classes='data', header="true")], colleges1=colleges, colleges2=colleges, results=[score_df.to_html(classes='data', header="true")], result=recommendation, fieldlist=fieldlist)



if __name__ == '__main__':
    app.run()