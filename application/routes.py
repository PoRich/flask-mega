from flask import render_template
from application import app


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    posts =[
        {
        'author': {'username': 'John'},
        'body': 'Beautiful day in Portland!'
        },
        {
        'author': {'username': 'Susan'},
        'body': 'Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)
