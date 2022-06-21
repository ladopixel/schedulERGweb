from tokenize import String
from wtforms import Form
from wtforms import PasswordField

class CreateForm(Form):
    password = PasswordField('password')