import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from psycopg2 import extras
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

# Imports
from models import Comic, Rating, Note
from forms import ComicForm
from db import get_db_connection  # Import get_db_connection

# Configuration
DEBUG = True
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'super secret key')

UPLOAD_FOLDER = 'static/covers'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# App Initialization
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
app.secret_key = SECRET_KEY

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# User class
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = str(id)  # Ensure ID is a string
        self.username = username
        self.email = email

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM \"Сайт библиотека\".users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            return User(user['id'], user['username'], user['email'])
        else:
            return None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()


# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Routes
@app.route('/')
def welcome():
    return render_template('library.html')


@app.route('/index')
def home():
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'title')  # Default to sorting by title
    status = request.args.get('status', '')  # Default status is empty
    comics = Comic.get_all(search_query=search_query, sort_by=sort_by, status=status)
    return render_template('home.html', comics=comics, search_query=search_query, sort_by=sort_by, status=status)


@app.route('/add_comic', methods=['GET', 'POST'])
@login_required
def add_comic():
    form = ComicForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            title = form.title.data
            author = form.author.data
            artist = form.artist.data
            publisher = form.publisher.data
            volume = form.volume.data
            year_published = form.year_published.data
            genre = form.genre.data
            short_description = form.short_description.data
            status = form.status.data

            cover_image = form.cover_image.data
            if cover_image and allowed_file(cover_image.filename):
                filename = secure_filename(cover_image.filename)
                cover_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('Необходимо загрузить обложку.', 'error')
                return render_template('add_comic.html', form=form)

            Comic.create(title, author, artist, publisher, volume, year_published, genre, short_description, filename, status)
            return redirect(url_for('home'))
        else:
            # Если форма не прошла валидацию, выводим сообщения об ошибках
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Ошибка в поле {getattr(form, field).label.text}: {error}", 'error')
            return render_template('add_comic.html', form=form)

    return render_template('add_comic.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        conn = get_db_connection()
        if conn is None:
            return render_template('register.html', error='Database connection failed')

        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM \"Сайт библиотека\".users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                return render_template('register.html', error='Username already exists')

            hashed_password = generate_password_hash(password, method='sha256')

            cursor.execute(
                "INSERT INTO \"Сайт библиотека\".users (username, password, email) VALUES (%s, %s, %s)",
                (username, hashed_password, email)
            )

            conn.commit()
            return redirect(url_for('login'))
        except psycopg2.Error as e:
            return render_template('register.html', error=f"Database error: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        if conn is None:
            return render_template('login.html', error='Database connection failed')

        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM \"Сайт библиотека\".users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                user_obj = User(user['id'], user['username'], user['email'])
                login_user(user_obj)
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error='Invalid username or password')
        except psycopg2.Error as e:
            return render_template('login.html', error=f"Database error: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM \"Сайт библиотека\".users WHERE id = %s", (current_user.id,))
        user = cursor.fetchone()
        return render_template('profile.html', user=user)
    except psycopg2.Error as e:
        return f"Database error: {e}", 500
    finally:
        if conn:
            cursor.close()
            conn.close()


@app.route('/comic/<int:comic_id>')
def comic_detail(comic_id):
    comic = Comic.get_by_id(comic_id)
    if not comic:
        return "Comic not found", 404

    average_rating = Rating.get_average_rating(comic_id)

    note = None
    if current_user.is_authenticated:
        note = Note.get_by_user_and_comic(current_user.id, comic_id)

    return render_template('comic_detail.html', comic=comic, average_rating=average_rating, note=note)


@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('query', '')
    comics = Comic.search(search_query)
    return render_template('home.html', comics=comics, search_query=search_query)


@app.route('/add_rating/<int:comic_id>', methods=['POST'])
@login_required
def add_rating(comic_id):
    rating = int(request.form['rating'])
    Rating.create(current_user.id, comic_id, rating)
    return redirect(url_for('comic_detail', comic_id=comic_id))


@app.route('/add_note/<int:comic_id>', methods=['POST'])
@login_required
def add_note(comic_id):
    note_text = request.form['note']
    Note.create(current_user.id, comic_id, note_text)
    return redirect(url_for('comic_detail', comic_id=comic_id))


@app.route('/user_notes')
@login_required
def user_notes():
    notes = Note.get_all_by_user(current_user.id)
    ratings = Rating.get_all_by_user(current_user.id)
    return render_template('user_notes.html', notes=notes, ratings=ratings)

if __name__ == '__main__':
    app.run(debug=DEBUG)
