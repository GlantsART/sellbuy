from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, FloatField
from wtforms.validators import DataRequired


class OfferForm(FlaskForm):
    name_offer = StringField('Название', validators=[DataRequired()])
    discription = TextAreaField("Описание")
    price = FloatField('Цена', validators=[DataRequired()])
    topic = StringField('Категория', validators=[DataRequired()])
    place = StringField('Город/Населенный пункт', validators=[DataRequired()])
    submit = SubmitField('Применить')