"""Movie Ratings"""

# from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Rating, Movie, connect_to_db, db
import requests
import secrets


app = Flask(__name__)
connect_to_db(app)
# app.jinja_env.undefined = StrictUndefined


# @app.route('/')
# def index():
#     """Homepage."""

#     return render_template('homepage.html')

# @app.route('/test')
# def get():

#     r = requests.get("http://www.omdbapi.com/?i=tt0107290&apikey=ff058cb3")
#     movie_desc = r.json()
#     return jsonify(movies=movie_desc)
API_KEY = 'ff058cb3'

@app.route('/')
def index():
    """Homepage."""

    return render_template('homepage_search.html')

@app.route('/login_homepage')
def login_page():
    """Login page"""
    return render_template('homepage.html')





@app.route('/search')
def get():
    searchword = request.args.get('s', '')
    r = requests.get('http://www.omdbapi.com/?s={}&apikey={}'.format(searchword, API_KEY))
    movie_desc = r.json()
    return jsonify(movies=movie_desc)







@app.route('/test')
def get_test():
    """Homepage."""

    return render_template('homepage_search_by_id.html')


@app.route('/search_by_id')
def search_test():
    searchid = request.args.get('s_id', '')
    r = requests.get('http://www.omdbapi.com/?i={}&apikey={}'.format(searchid, API_KEY))
    movie_desc = r.json()
    # movie = Movie(id=id,
    #               title=title,
    #               year=year,
    #               genre=genre,
    #               imdb_rating=imdb_rating,
    #               image_url=image_url)
    # db.session.add(movie)
    # db.session.commit()
    return jsonify(movies=movie_desc)


@app.route('/api/registration', methods=['POST'])
def registration():

    data = { #crearing data, will be accessed with data[email]
        'email': request.json['email'],
        'password': request.json['password'],
        'first_name': request.json['first_name'],
        'last_name': request.json['last_name'],
    }
    token = secrets.token_hex()#generating tokens
    user = User(email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                token=token
                )
    db.session.add(user)
    db.session.commit()
    return jsonify(data), 201


if __name__ == '__main__':
    # debug=True gives us error messages in the browser and also "reloads"
    # our web app if we change the code.
    app.run(debug=True, host="0.0.0.0")
