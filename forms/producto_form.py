# forms/producto_form.py
from flask_wtf import FlaskForm # pyright: ignore[reportMissingImports]
from wtforms import StringField, FloatField, IntegerField, SelectField, TextAreaField, SubmitField # pyright: ignore[reportMissingModuleSource]
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError # type: ignore

class ProductoForm(FlaskForm):
    """Formulario para crear/editar productos"""
    
    nombre = StringField('Nombre del producto', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(min=3, max=200, message='El nombre debe tener entre 3 y 200 caracteres')
    ])
    
    precio = FloatField('Precio', validators=[
        DataRequired(message='El precio es obligatorio'),
        NumberRange(min=0.01, message='El precio debe ser mayor a 0')
    ])
    
    cantidad = IntegerField('Cantidad', validators=[
        DataRequired(message='La cantidad es obligatoria'),
        NumberRange(min=0, message='La cantidad no puede ser negativa')
    ])
    
    categoria = SelectField('Categoría', choices=[
        ('computadoras', '💻 Computadoras'),
        ('perifericos', '🖱️ Periféricos'),
        ('audio', '🎧 Audio'),
        ('celulares', '📱 Celulares'),
        ('tablets', '📲 Tablets'),
        ('otros', '📦 Otros')
    ], validators=[DataRequired(message='Selecciona una categoría')])
    
    descripcion = TextAreaField('Descripción', validators=[
        Length(max=500, message='La descripción no puede exceder los 500 caracteres')
    ])
    
    submit = SubmitField('Guardar Producto')


class ProductoFiltroForm(FlaskForm):
    """Formulario para filtrar productos"""
    categoria = SelectField('Categoría', choices=[
        ('', 'Todas las categorías'),
        ('computadoras', '💻 Computadoras'),
        ('perifericos', '🖱️ Periféricos'),
        ('audio', '🎧 Audio'),
        ('celulares', '📱 Celulares'),
        ('tablets', '📲 Tablets'),
        ('otros', '📦 Otros')
    ], validators=[])
    
    stock_minimo = IntegerField('Stock mínimo', validators=[
        NumberRange(min=0, message='El stock mínimo debe ser mayor o igual a 0')
    ])
    
    buscar = StringField('Buscar', validators=[
        Length(max=100, message='Máximo 100 caracteres')
    ])