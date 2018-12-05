from flask import Flask, render_template, request, flash, redirect, session, jsonify, Response
from flask_restful import Api, Resource
from model import User, Movie, Comment, connect_to_db, db
import requests
from flask_marshmallow import Marshmallow
import os
import ast
import json


app = Flask(__name__)
app.secret_key = 'SECRET123'
SELF_URL = 'http://localhost:5000'

api = Api(app)
connect_to_db(app)
ma = Marshmallow(app)


API_KEY = os.getenv('API_KEY')


class UserSchema(ma.Schema):
    class Meta:
        fields = ('email', 'first_name', 'last_name', 'id')


class MovieSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'year', 'genre', 'imdb_rating', 'image_url', 'rating', 'ratings')


class CommentSchema(ma.Schema):
    class Meta:
        fields = ('text', 'user_id')


user_schema = UserSchema()
users_schema = UserSchema(many=True)
movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()
comments_schema = CommentSchema(many=True)
comment_schema = CommentSchema()


@app.route('/')
def index_page():
    """Homepage"""
    if session.get('email'):
        return render_template('index.html')
    return redirect('/login')


@app.route('/registration')
def registration_page():
    """Login page"""
    if session.get('email'):
        return redirect('/')
    return render_template('registration.html')


@app.route('/login')
def login_page():
    if session.get('email'):
        return redirect('/')
    return render_template('login.html')


@app.route('/logout')
def logout_page():
    session.pop('email', None)
    session.pop('user_id', None)
    return redirect('/login')


@app.route('/search', methods=['POST', 'GET'])
def search_movies():
    if not session.get('email'):
        return redirect('/login')
    search_word = request.args.get('s', '')
    movie_id = request.form.get('movie_id', None)
    r = requests.get('http://www.omdbapi.com/?s={}&i={}&apikey={}'.format(search_word, movie_id, API_KEY))
    if search_word:
        return render_template('search_results.html', movies=r.json())
    else:
        movie = add_movie_if_not_there_or_get(movie_id)
        if movie:
            return redirect('/moviedetails?movie_id={}'.format(movie_id))
    # return jsonify(r.json())


@app.route('/moviedetails', methods=['GET'])
def get_moviedetails():
    if not session.get('email'):
        return redirect('/login')
    movie_id = request.args.get('movie_id', '')
    user_id = session.get('user_id')
    r1 = requests.get('{}/api/movies/{}?with_comments=true&with_imdb=true'.format(SELF_URL, movie_id))
    comments = r1.json()['comments']
    my_rate = {'1': '', '2': '', '3': '', '4': '', '5': ''}
    _movie = Movie.query.get(movie_id)
    if _movie.ratings:
        _movie_ratings = json.loads(_movie.ratings)
        if str(user_id) in _movie_ratings:
            my_rate[str(_movie_ratings[str(user_id)])] = 'checked'
    return render_template('movie_details.html', movie=r1.json(), comments=comments, my_rate=my_rate)


@app.route('/movielist', methods=['GET'])
def get_movielist():
    if not session.get('email'):
        return redirect('/login')
    r = requests.get('{}/api/users/{}/movielist'.format(SELF_URL, session.get('user_id')))
    return render_template('movie_list.html', movies=r.json())


@app.route('/comment', methods=['POST'])
def add_comment():
    if not session.get('email'):
        return redirect('/login')
    user_id = session.get('user_id')
    text = request.form['text']
    movie_id = request.form['movie_id']
    data = {'user_id': user_id, 'text': text}
    data = json.dumps(data)
    headers = {'Content-Type': 'application/json'}
    requests.post('{}/api/movies/{}/comments'.format(SELF_URL, movie_id),
                  data=data,
                  headers=headers)
    return redirect('/moviedetails?movie_id={0}'.format(movie_id))


@app.route('/rate', methods=['POST'])
def add_rating():
    if not session.get('email'):
        return redirect('/login')
    user_id = session.get('user_id')
    rating = int(request.form['rating'])
    movie_id = request.form['movie_id']
    data = {'rating': rating}
    data = json.dumps(data)
    headers = {'Content-Type': 'application/json'}
    requests.post('{}/api/users/{}/movielist/{}/rating'.format(SELF_URL, user_id, movie_id),
                  data=data,
                  headers=headers)
    return redirect('/moviedetails?movie_id={}'.format(movie_id))


@app.route('/api/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user:
        if password == user.password:
            session['email'] = email
            session['user_id'] = user.id
            flash('Logged in  as {0}'.format(email))
            return redirect('/')
        else:
            flash('Wrong password')
            return redirect('/login')
    else:
        flash('Wrong email')
        return redirect('/login')


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
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        first_name = request.json.get('first_name', None)
        last_name = request.json.get('last_name', None)
        if email and password and first_name and last_name:
            user_in_db = User.query.filter_by(email=email).first()
            if user_in_db:
                message = {'error': 'User already exist, please supply another email address'}
                return custom_response(message, 400)
            user = User(email=email,
                        password=request.json['password'],
                        first_name=request.json['first_name'],
                        last_name=request.json['last_name']
                        )
            db.session.add(user)
            db.session.commit()
            res = user_schema.jsonify(user)
            return res
        message = {'error': 'Somethings is missing'}
        return custom_response(message, 400)


class UserMovieList(Resource):
    def get(self, user_id):
        all_movies = Movie.query.filter(Movie._users.any(id=user_id)).all()
        result = movies_schema.dump(all_movies)
        return jsonify(result.data)

    def post(self, user_id):
        content_type = request.headers['Content-Type']
        if content_type == 'application/json':
            movie_id = request.json.get('movie_id')
        elif content_type == 'application/x-www-form-urlencoded':
            movie_id = request.form.get('movie_id')
        else:
            message = {'error': 'Specify Content-Type'}
            return custom_response(message, 400)
        user = User.query.get(user_id)
        for movie in user.movies:
            if movie.id == movie_id:
                message = {'error': 'Movie is already in the list'}
                return custom_response(message, 409)
        movie = add_movie_if_not_there_or_get(movie_id)
        user.movies.append(movie)
        db.session.add(user)
        db.session.commit()
        return redirect('/movielist')


class UserMovieRating(Resource):
    def post(self, movie_id, user_id):
        content_type = request.headers['Content-Type']
        if content_type == 'application/json':
            rating = request.json.get('rating')
        elif content_type == 'application/x-www-form-urlencoded':
            rating = int(request.form.get('rating'))
        else:
            message = {'error': 'Specify Content-Type'}
            return custom_response(message, 400)
        user = User.query.get(user_id)
        _movie = Movie.query.get(movie_id)
        for movie in user.movies:
            if movie.id == movie_id:
                _movie_ratings = json.loads(_movie.ratings)
                if user_id in _movie_ratings and _movie_ratings[user_id] != rating:
                    _movie_ratings[user_id] = rating
                    _movie_rating = recalc_rating(_movie_ratings)
                    movie.rating = _movie_rating
                    movie.ratings = json.dumps(_movie_ratings)
                    db.session.add(_movie)
                    db.session.commit()
                    return True
                elif not _movie_ratings:
                    _movie_ratings = dict()
                    _movie_ratings[user_id] = rating
                    _movie_rating = recalc_rating(_movie_ratings)
                    movie.rating = _movie_rating
                    movie.ratings = json.dumps(_movie_ratings)
                    db.session.add(_movie)
                    db.session.commit()
                    return True

        message = {'error': 'No such movie found in your list'}
        return custom_response(message, 404)


class Comments(Resource):
    def get(self, movie_id):
        all_comments = Comment.query.filter_by(movie_id=movie_id).all()
        result = comments_schema.dump(all_comments)
        return jsonify(result.data)

    def post(self, movie_id):
        content_type = request.headers['Content-Type']
        if content_type == 'application/json':
            user_id = request.json.get('user_id')
            text = request.json.get('text')
        elif content_type == 'application/x-www-form-urlencoded':
            user_id = request.form['user_id']
            text = request.form['text']
        else:
            message = {'error': 'Specify Content-Type'}
            return custom_response(message, 400)
        comment = Comment(user_id=user_id,
                          movie_id=movie_id,
                          text=text)
        db.session.add(comment)
        db.session.commit()
        return comment_schema.jsonify(comment)


class MovieAction(Resource):
    def get(self, movie_id):
        movie = add_movie_if_not_there_or_get(movie_id)
        result_movie = movie_schema.dump(movie).data
        with_comments = request.args.get('with_comments')
        with_imdb = request.args.get('with_imdb')
        if with_comments:
            comments = Comment.query.filter_by(movie_id=movie_id).all()
            for comment in comments:
                user = User.query.get(comment.user_id)
                user_dict = {'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name}
                comment.user_id = user_dict
            result_movie['comments'] = comments_schema.dump(comments).data
        if with_imdb:
            r = requests.get('http://www.omdbapi.com/?i={}&apikey={}'.format(movie_id, API_KEY))
            result_movie.update(r.json())
        return jsonify(result_movie)


class Ratings(Resource):
    def get(self, movie_id):
        movie = Movie.query.get(movie_id)
        result_movie = movie_schema.dump(movie).data
        with_comments = request.args.get('with_comments')
        if with_comments:
            comments = Comment.query.filter_by(movie_id=movie_id).all()
            result_movie['comments'] = comments_schema.dump(comments).data
        return jsonify(result_movie)


api.add_resource(UserAction, '/api/users/<user_id>')
api.add_resource(Users, '/api/users')
api.add_resource(UserMovieList, '/api/users/<user_id>/movielist')
api.add_resource(UserMovieRating, '/api/users/<user_id>/movielist/<movie_id>/rating')
api.add_resource(Comments, '/api/movies/<movie_id>/comments')
api.add_resource(Ratings, '/api/movies/<movie_id>/rating')
api.add_resource(MovieAction, '/api/movies/<movie_id>')


def custom_response(res, status_code):
    return Response(mimetype='application/json', response=json.dumps(res), status=status_code)


def recalc_rating(d):
    rating = 0
    for i in d:
        rating += d[i]
    return rating / len(d)


def add_movie_if_not_there_or_get(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        r = requests.get('http://www.omdbapi.com/?i={}&apikey={}'.format(movie_id, API_KEY))
        if r.status_code == 200:
            title = r.json().get('Title')
            year = r.json().get('Year')
            genre = r.json().get('Genre')
            imdb_rating = r.json().get('imdbRating')
            image_url = r.json().get('Poster')
            movie = Movie(id=movie_id, title=title, year=year, genre=genre, imdb_rating=imdb_rating,
                          image_url=image_url, rating=0)
            db.session.add(movie)
            db.session.commit()
    return movie


if __name__ == '__main__':
    # debug=True gives us error messages in the browser and also "reloads"
    # our web app if we change the code.
    app.run(debug=True, host='0.0.0.0', threaded=True)
