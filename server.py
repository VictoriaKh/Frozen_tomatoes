from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_restful import reqparse, abort, Api, Resource
from model import User, Rating, Movie, connect_to_db, db
import requests
from flask_marshmallow import Marshmallow
import secrets


app = Flask(__name__)
api = Api(app)
connect_to_db(app)
ma = Marshmallow(app)
API_KEY = 'ff058cb3'


class UserSchema(ma.Schema):
    class Meta:
        fields = ('email', 'first_name', 'last_name', 'id')


class MovieSchema(ma.Schema):
    class Meta:
        fields = ('title', 'year')


user_schema = UserSchema()
users_schema = UserSchema(many=True)
movies_schema = MovieSchema(many=True)


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


class UserAction(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        return user_schema.jsonify(user)

    def delete(self, user_id):
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        return user_schema.jsonify(user)

    def put(self, user_id):
        user = User.query.get(user_id)
        user.first_name = request.json['first_name']
        user.last_name = request.json['last_name']
        user.email = request.json['email']
        user.password = request.json['password']

        db.session.commit()
        return user_schema.jsonify(user)


class Users(Resource):
    def get(self):
        all_users = User.query.all()
        result = users_schema.dump(all_users)
        return jsonify(result.data)

    def post(self):
        token = secrets.token_hex()
        user = User(email=request.json['email'],
                    password=request.json['password'],
                    first_name=request.json['first_name'],
                    last_name=request.json['last_name'],
                    token=token
                    )
        db.session.add(user)
        db.session.commit()
        return user_schema.jsonify(user)


class UserMovieList(Resource):
    def get(self, user_id):
        all_movies = Movie.query.filter(Movie._users.any(id=user_id)).all()
        result = movies_schema.dump(all_movies)
        return jsonify(result.data)

    def post(self, user_id):
        movie_id = request.json['movie_id']
        user = User.query.get(user_id)
        movie = Movie.query.get(movie_id)
        user.movies.append(movie)
        db.session.add(user)
        db.session.commit()
        return user_schema.jsonify(user)


api.add_resource(UserAction, '/api/users/<user_id>')
api.add_resource(Users, '/api/users')
api.add_resource(UserMovieList, '/api/users/<user_id>/movielist')


if __name__ == '__main__':
    # debug=True gives us error messages in the browser and also "reloads"
    # our web app if we change the code.
    app.run(debug=True, host="0.0.0.0")
