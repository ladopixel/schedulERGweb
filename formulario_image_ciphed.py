from tokenize import String
from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField

class CreateForm(Form):
    ruta_image = StringField('ruta_image')
    password = PasswordField('password')