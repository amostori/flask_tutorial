# pip install -U Flask-SQLAlchemy
# pip install Flask-Bootstrap
# pip install Flask-WTF
# pip install email_validator
# pip install wtforms[email]
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.secret_key = 'random_string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)

MOVIE_DATABASE_API = "a4e27a606804ec0bd4baae3da4c33fd2"
MOVIE_DATABASE_URL = "https://api.themoviedb.org/3/search/movie"
DETAILS_MOVIE_URL = "https://api.themoviedb.org/3/movie/"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


# creating table
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(500), nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'


db.create_all()


# new_movie = Movie(
#     title="Godfather 2",
#     year=1988,
#     description=" Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=10,
#     ranking=1,
#     review="My favourite character was the Godfather's son.",
#     img_url="https://freight.cargo.site/w/1280/q/94/i/18678c7a58e6aa9e17b6736303fdeab034f4b811b780df7ca08346adc67a197a/godfather_regular.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()


@app.route('/')
def home():
    # This line creates a list of all the movies sorted by rating
    all_movies = Movie.query.order_by(Movie.rating).all()

    # This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template('index.html', all_movies=all_movies)


class RateMovieForm(FlaskForm):
    new_rating = FloatField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    new_review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Done")


@app.route('/edit', methods=["GET", "POST"])
def edit():
    rate_movie_form = RateMovieForm()
    movie_id = request.args.get('movie_id')
    movie_to_update = Movie.query.get(movie_id)
    if request.method == "POST":
        if rate_movie_form.validate_on_submit():
            movie_to_update.rating = rate_movie_form.new_rating.data
            movie_to_update.review = rate_movie_form.new_review.data
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('edit.html', form=rate_movie_form, movie=movie_to_update)


@app.route('/delete')
def delete():
    movie_id = request.args.get('movie_id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


class AddTitleForm(FlaskForm):
    title = StringField("Movie title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route('/add', methods=["POST", "GET"])
def add():
    add_title_form = AddTitleForm()

    if add_title_form.validate_on_submit():
        add_params = {
            "api_key": MOVIE_DATABASE_API,
            "query": add_title_form.title.data
        }
        response = requests.get(url=MOVIE_DATABASE_URL, params=add_params)
        data = response.json()['results']
        return render_template('select.html', options=data)
    return render_template('add.html', form=add_title_form)


@app.route('/select')
def select():
    render_template('select.html')


@app.route('/find')
def find():
    movie_api_id = request.args.get("id")
    find_params = {
        "api_key": MOVIE_DATABASE_API,
    }
    path = f"{DETAILS_MOVIE_URL}/{movie_api_id}"
    response = requests.get(url=path, params=find_params)
    data = response.json()
    new_movie = Movie(
        id=data['id'],
        title=data["title"],
        # The data in release_date includes month and day, we will want to get rid of.
        year=data["release_date"].split("-")[0],
        img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
        description=data["overview"],
        rating=7.3,
        ranking=10,
        review="My favourite character was the caller."
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', movie_id=new_movie.id))


# searching movie in movie database


if __name__ == "__main__":
    app.run(debug=True)
