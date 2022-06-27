from tokenize import String
from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms import FileField

class CreateForm(Form):
    name = StringField('name')
    description = StringField('description')
    ruta_image = StringField('ruta_image')
    ruta_ipfs = StringField('ruta_ipfs')
    hash_image = StringField('hash_image')
    password = PasswordField('password')