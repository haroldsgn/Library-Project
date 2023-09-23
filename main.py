from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlite3

db = SQLAlchemy()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"

db.init_app(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)


@app.route('/', methods=['GET', 'POST'])
def home():

    book_id = request.args.get('id')
    if book_id:
        book_to_delete = db.get_or_404(Book, book_id)
        db.session.delete(book_to_delete)
        db.session.commit()
    else:

        try:
            result = db.session.execute(db.select(Book).order_by(Book.title))
            all_books = result.scalars().all()
        except Exception as e:
            print("Error:", e)
            all_books = []

        return render_template('index.html', books=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add_book():

    if request.method == 'POST':

        data = request.form
        book = data['book'].title()
        author = data['author'].title()
        rating = float(data['rating'])

        new_book = Book(
            title=book,
            author=author,
            rating=rating
        )

        with app.app_context():
            db.create_all()
            db.session.add(new_book)
            db.session.commit()

        return redirect(url_for('home'))

    return render_template('add.html')


@app.route("/edit", methods=['GET', 'POST'])
def edit_rating():
    book_id = request.args.get('id')
    book_to_update = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    title = book_to_update.title
    current_rating = book_to_update.rating

    if request.method == 'POST':
        new_rating = request.form['rating']
        book_to_update.rating = new_rating

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', title=title, current_rating=current_rating, id=book_id)


if __name__ == "__main__":
    app.run(debug=True)
