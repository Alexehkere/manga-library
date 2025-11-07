import psycopg2
from psycopg2 import extras
from db import get_db_connection  # Import get_db_connection from db.py

class Comic:
    def __init__(self, id, title, author, artist, publisher, volume, year_published, genre, short_description, cover_image, status):
        self.id = id
        self.title = title
        self.author = author
        self.artist = artist
        self.publisher = publisher
        self.volume = volume
        self.year_published = year_published
        self.genre = genre
        self.short_description = short_description
        self.cover_image = cover_image
        self.status = status

    @staticmethod
    def get_all(search_query='', sort_by='title', status=''):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        try:
            # Удаляем лишние пробелы в начале и конце поискового запроса
            search_query = search_query.strip()

            query = """
                SELECT id, title, author, artist, publisher, volume, year_published, genre, short_description, cover_image, status
                FROM "Сайт библиотека".comics
                WHERE (title ILIKE %s OR author ILIKE %s OR genre ILIKE %s)
            """
            # Добавим поиск по вхождению в жанр
            params = ['%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%']

            if status:
                query += " AND status = %s"
                params.append(status)

            if sort_by == 'year':
                query += " ORDER BY year_published DESC"
            elif sort_by == 'author':
                query += " ORDER BY author"
            else:
                query += " ORDER BY title"  # Default sort by title
            cursor.execute(query, params)
            comics = []
            for row in cursor.fetchall():
                comic = Comic(
                    id=row['id'],
                    title=row['title'],
                    author=row['author'],
                    artist=row['artist'],
                    publisher=row['publisher'],
                    volume=row['volume'],
                    year_published=row['year_published'],
                    genre=row['genre'],
                    short_description=row['short_description'],
                    cover_image=row['cover_image'],
                    status=row['status']
                )
                comics.append(comic)
            return comics
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()

    @staticmethod
    def create(title, author, artist, publisher, volume, year_published, genre, short_description, cover_image, status):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO \"Сайт библиотека\".comics (title, author, artist, publisher, volume, year_published, genre, short_description, cover_image, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (title, author, artist, publisher, volume, year_published, genre, short_description, cover_image, status)
            )
            conn.commit()
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
        finally:
            if conn:
                cursor.close()
                conn.close()

    @staticmethod
    def get_by_id(comic_id):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        try:
            cursor.execute("SELECT * FROM \"Сайт библиотека\".comics WHERE id = %s", (comic_id,))
            comic = cursor.fetchone()
            if comic:
                return Comic(**comic)
            else:
                return None
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()

class Rating:
    def __init__(self, id, user_id, comic_id, rating):
        self.id = id
        self.user_id = user_id
        self.comic_id = comic_id
        self.rating = rating

    @staticmethod
    def create(user_id, comic_id, rating):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO \"Сайт библиотека\".ratings (user_id, comic_id, rating) VALUES (%s, %s, %s)",
                (user_id, comic_id, rating)
            )
            conn.commit()
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
        finally:
            if conn:
                cursor.close()
                conn.close()

    @staticmethod
    def get_average_rating(comic_id):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        try:
            cursor.execute(
                "SELECT AVG(rating) AS average_rating FROM \"Сайт библиотека\".ratings WHERE comic_id = %s",
                (comic_id,)
            )
            result = cursor.fetchone()
            if result and result['average_rating'] is not None:
                return round(result['average_rating'], 2)
            else:
                return None
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()

    @staticmethod
    def get_all_by_user(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        try:
            cursor.execute(
                "SELECT r.*, c.title as comic_title FROM \"Сайт библиотека\".ratings r JOIN \"Сайт библиотека\".comics c ON r.comic_id = c.id WHERE r.user_id = %s",
                (user_id,)
            )
            ratings = []
            for row in cursor.fetchall():
                rating = Rating(id=row['id'], user_id=row['user_id'], comic_id=row['comic_id'], rating=row['rating'])
                rating.comic_title = row['comic_title']  # Add comic title to the rating object
                ratings.append(rating)
            return ratings
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()

class Note:
    def __init__(self, id, user_id, comic_id, note, comic=None):
        self.id = id
        self.user_id = user_id
        self.comic_id = comic_id
        self.note = note
        self.comic = comic  # Add comic object to the note

    @staticmethod
    def create(user_id, comic_id, note):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO \"Сайт библиотека\".notes (user_id, comic_id, note) VALUES (%s, %s, %s)",
                (user_id, comic_id, note)
            )
            conn.commit()
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
        finally:
            if conn:
                cursor.close()
                conn.close()

    @staticmethod
    def get_by_user_and_comic(user_id, comic_id):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        try:
            cursor.execute(
                "SELECT * FROM \"Сайт библиотека\".notes WHERE user_id = %s AND comic_id = %s",
                (user_id, comic_id)
            )
            note = cursor.fetchone()
            if note:
                return Note(**note)
            else:
                return None
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()

    @staticmethod
    def get_all_by_user(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        try:
            cursor.execute(
                "SELECT n.*, c.* FROM \"Сайт библиотека\".notes n JOIN \"Сайт библиотека\".comics c ON n.comic_id = c.id WHERE n.user_id = %s",
                (user_id,)
            )
            notes = []
            for row in cursor.fetchall():
                comic = Comic(id=row['id'], title=row['title'], author=row['author'], artist=row['artist'], publisher=row['publisher'], volume=row['volume'], year_published=row['year_published'], genre=row['genre'], short_description=row['short_description'], cover_image=row['cover_image'], status=row['status'])
                note = Note(id=row['id'], user_id=row['user_id'], comic_id=row['comic_id'], note=row['note'], comic=comic)
                notes.append(note)
            return notes
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()
