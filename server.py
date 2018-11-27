from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_restful import reqparse, abort, Api, Resource
from model import User, Rating, Movie, connect_to_db, db
import requests
from flask_marshmallow import Marshmallow
import secrets
import os


app = Flask(__name__)
app.secret_key = 'SECRET123'

api = Api(app)
connect_to_db(app)
ma = Marshmallow(app)


API_KEY = os.getenv('API_KEY')


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
    return redirect('/login')


@app.route('/search', methods=['POST', 'GET'])
def get():
    search_word = request.args.get('s', '')
    movie_id = request.form.get('movie_id', None)
    r = requests.get('http://www.omdbapi.com/?s={}&i={}&apikey={}'.format(search_word, movie_id, API_KEY))
    if search_word:
        return render_template('search_results.html', movies=r.json())
    else:
        return jsonify(r.json())


@app.route('/api/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if password == user.password:
        session['email'] = email
        flash('Logged in  as {0}'.format(email))
        return redirect('/')
    else:
        flash('Wrong password')
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


def custom_response(res, status_code):
    return Response(mimetype='application/json', response=json.dumps(res), status=status_code)



if __name__ == '__main__':
    # debug=True gives us error messages in the browser and also "reloads"
    # our web app if we change the code.
    app.run(debug=True, host="0.0.0.0")
