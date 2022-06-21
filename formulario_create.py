from tokenize import String
from wtforms import Form
from wtforms import StringField

class CreateForm(Form):
    name = StringField('name')
    description = StringField('description')
    amount = StringField('amount')
    decimals = StringField('decimals')