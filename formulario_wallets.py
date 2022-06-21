from tokenize import String
from wtforms import Form
from wtforms import StringField

class WalletForm(Form):
    wallet_address = StringField('wallet_address')