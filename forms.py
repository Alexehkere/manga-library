from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, FileField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

class ComicForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])  # Сделаем автора обязательным
    artist = StringField('Художник', validators=[DataRequired()])  # Сделаем художника обязательным
    publisher = StringField('Издательство', validators=[DataRequired()])  # Сделаем издательство обязательным
    volume = IntegerField('Том', validators=[Optional()])
    year_published = IntegerField('Год издания', validators=[Optional()])
    genre = StringField('Жанр', validators=[DataRequired()])  # Сделаем жанр обязательным
    short_description = TextAreaField('Краткое описание', validators=[DataRequired()])  # Сделаем описание обязательным
    cover_image = FileField('Обложка', validators=[DataRequired()])  # Сделаем обложку обязательной
    status = SelectField('Статус', choices=[('In Stock', 'В наличии'), ('Loaned Out', 'Выдано')], validators=[DataRequired()])  # Сделаем статус обязательным
    submit = SubmitField('Добавить комикс/мангу')
