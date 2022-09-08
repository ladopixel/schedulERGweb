from tokenize import String
from wtforms import Form, StringField, PasswordField


class Send_erg(Form):
    wallet_address = StringField('wallet_address')
    amount = StringField('amount')


class Create_token(Form):
    name = StringField('name')
    description = StringField('description')
    amount = StringField('amount')
    decimals = StringField('decimals')


class Image_ciphed(Form):
    ruta_image = StringField('ruta_image')
    password = PasswordField('password')


class Create_token_ciphed(Form):
    name = StringField('name')
    description = StringField('description')
    amount = StringField('amount')
    decimals = StringField('decimals')
    password = PasswordField('password')


class Create_nft_ciphed(Form):
    name = StringField('name')
    description = StringField('description')
    ruta_image = StringField('ruta_image')
    ruta_ipfs = StringField('ruta_ipfs')
    hash_image = StringField('hash_image')
    password = PasswordField('password')


class Wallet_form(Form):
    wallet_address = StringField('wallet_address')


class Create_deciph(Form):
    password = PasswordField('password')