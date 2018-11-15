from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

movies_to_users = db.Table('movies_to_users',
                                 db.Column('movie_id', db.String(20), db.ForeignKey('movies.id')),
                                 db.Column('user_id', db.Integer, db.ForeignKey('users.id')))


class User(db.Model):
    """User of movies website."""

    __tablename__ = "users"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    token = db.Column(db.String(64), nullable=False)
    movies = db.relationship('Movie', backref='movies', lazy='dynamic', secondary=movies_to_users)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<User user_id={self.id} email={self.email}>"


class Movie(db.Model):
    """Movie on movies website."""

    __tablename__ = "movies"

    id = db.Column(db.String(20), autoincrement=False, primary_key=True)
    title = db.Column(db.String(100))
    year = db.Column(db.String(100))
    genre = db.Column(db.String(200))
    imdb_rating = db.Column(db.String(100))
    image_url = db.Column(db.String(200))

    _users = db.relationship('User', secondary=movies_to_users,
                             backref=db.backref('movies_to_users_backref', lazy='dynamic'))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Movie movie_id={self.id} title={self.title}>"


class Rating(db.Model):
    """Rating of a movie by a user."""

    __tablename__ = "ratings"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.String(20), db.ForeignKey('movies.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.Column(db.String(500))
    score = db.Column(db.Integer)

    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("ratings", order_by=id))

    # Define relationship to movie
    movie = db.relationship("Movie",
                            backref=db.backref("ratings", order_by=id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Rating rating_id={self.rating_id}
                    movie_id={self.movie_id}
                    user_id={self.user_id}
                    score={self.score}>"""


##############################################################################

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")
# Helper functions

# def connect_to_db(app):
#     """Connect the database to our Flask app."""

#     # Configure to use our PostgreSQL database
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


# if __name__ == "__main__":
#     # As a convenience, if we run this module interactively, it will leave
#     # you in a state of being able to work with the database directly.

#     from server import app
#     connect_to_db(app)
#     print("Connected to DB.")
