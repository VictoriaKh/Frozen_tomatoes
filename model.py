from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

movies_to_users = db.Table('movies_to_users', db.Column('movie_id', db.String(20), db.ForeignKey('movies.id')),
                           db.Column('user_id', db.Integer, db.ForeignKey('users.id')))


class User(db.Model):
    """User of movies website."""

    __tablename__ = "users"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    token = db.Column(db.String(64), nullable=True)
    movies = db.relationship('Movie', backref='movies', lazy='dynamic', secondary=movies_to_users)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<User user_id={self.id} email={self.email} movies {self.movies}>"


class Movie(db.Model):
    """Movie on movies website."""

    __tablename__ = "movies"

    id = db.Column(db.String(20), autoincrement=False, primary_key=True)
    title = db.Column(db.String(100))
    year = db.Column(db.String(100))
    genre = db.Column(db.String(200))
    imdb_rating = db.Column(db.String(100))
    image_url = db.Column(db.String(200), nullable=True)
    ratings = db.Column(db.String(200), default='{}')
    rating = db.Column(db.Float, nullable=True)
    _users = db.relationship('User', secondary=movies_to_users,
                             backref=db.backref('movies_to_users_backref', lazy='dynamic'))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Movie movie_id={self.id} title={self.title} rating={self.rating}>"


class Comment(db.Model):
    """Rating of a movie by a user."""

    __tablename__ = "comments"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.String(20), db.ForeignKey('movies.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.String(200))
    user = db.relationship("User",
                           backref=db.backref("comments", order_by=id))
    movie = db.relationship("Movie",
                            backref=db.backref("comments", order_by=id))


##############################################################################
def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

# def connect_to_db(app):
#     POSTGRES = {
#         'user': 'postgres',
#         'db': 'ratings',
#         'host': 'localhost',
#         'port': '5432',
#     }
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s@%(host)s:%(port)s/%(db)s' % POSTGRES
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     db.app = app
#     db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")
