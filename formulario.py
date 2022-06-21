from tokenize import String
from wtforms import Form
from wtforms import StringField

class CommentForm(Form):
    wallet_address = StringField('wallet_address')
    amount = StringField('amount')