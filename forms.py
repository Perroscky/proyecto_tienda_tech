# forms.py
from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, FloatField, IntegerField, SubmitField # type: ignore
from wtforms.validators import DataRequired, Length, NumberRange # type: ignore

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Producto', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres')
    ])
    precio = FloatField('Precio', validators=[
        DataRequired(message='El precio es obligatorio'),
        NumberRange(min=0.01, message='El precio debe ser mayor a 0')
    ])
    cantidad = IntegerField('Cantidad', validators=[
        DataRequired(message='La cantidad es obligatoria'),
        NumberRange(min=0, message='La cantidad no puede ser negativa')
    ])
    categoria = StringField('Categoría', validators=[
        DataRequired(message='La categoría es obligatoria')
    ])
    descripcion = StringField('Descripción')
    submit = SubmitField('Guardar Producto')