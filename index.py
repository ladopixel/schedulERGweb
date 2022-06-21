from crypt import methods
from flask import Flask
from flask import render_template
from flask import request

from ergpy import helper_functions, appkit 

import formulario
import formulario_create
import formulario_create_ciphed
import formulario_wallets
import formulario_deciph

import cryptocode
import requests

app = Flask(__name__)

node_url: str = "http://159.65.11.55:9053/"
ergo = appkit.ErgoAppKit(node_url=node_url)

#################### You seed phrase 
wallet_mnemonic = ""

# Convert the description UTF-8 to String
def to_utf8_string(hex):
    valor_utf8 = '' 
    aux = ''
    contador = 0
    for i in hex:
        contador = contador + 1
        if contador < 3:
            aux = aux + i
        if contador == 2:
            valor_utf8 = valor_utf8 + str(chr(int(aux, 16)))
            contador = 0
            aux = ''
    return valor_utf8

# INDEX
@app.route('/')
def index():
    return render_template('menu.html')

# SEND ERG
def sendERG(receiver, cantidad):
    cantidad_float = float(cantidad)
    amount = [cantidad_float]
    receiver_Addresses = [receiver]
    print('enviando ' + str(amount) + ' ERG to ' + str(receiver_Addresses))
    try:
        print('Transaction OK ↓')
        return(helper_functions.simple_send(ergo=ergo, amount=amount, wallet_mnemonic=wallet_mnemonic, receiver_addresses=receiver_Addresses))
    except:
        print('ERROR Transaction!')

# CREATE TOKEN
def createToken(token_name, token_description, token_amount, token_decimals):
    token_amount = int(token_amount)
    token_decimals = int(token_decimals)
    try:
        print('Transaction OK ↓')
        return(helper_functions.create_token(ergo=ergo, token_name=token_name, description=token_description, token_amount=token_amount, token_decimals=token_decimals, wallet_mnemonic=wallet_mnemonic))            
    except:
        print('ERROR creating token!')

# SEND ERG
@app.route('/send', methods = ['GET', 'POST']) 
def send():
    idTx = ''
    comment_form = formulario.CommentForm(request.form)
    wallet_address = comment_form.wallet_address.data
    amount = comment_form.amount.data
    if wallet_address != None:
        idTx = sendERG(wallet_address, amount)

    return render_template('send-erg.html', form = comment_form, wallet_address = wallet_address, amount = amount, idTx = idTx)



# CREATE TOKEN
@app.route('/create-token', methods = ['GET', 'POST']) 
def create_token():
    idTx = ''
    create_token_form = formulario_create.CreateForm(request.form)
    name = create_token_form.name.data
    description = create_token_form.description.data
    amount = create_token_form.amount.data
    decimals = create_token_form.decimals.data
    if name == None or name == '' or description == None or description == '' or amount == None or amount == '' or decimals == None or decimals == '':
        print('No se puede crear')
    else:
        idTx = createToken(name, description, amount, decimals)

    return render_template('create-token.html', form = create_token_form, name = name, description = description, amount = amount, decimals = decimals, idTx = idTx)


# CREATE TOKEN CIPHED
@app.route('/create-token-ciphed', methods = ['GET', 'POST'])
def create_token_ciphed():
    create_token_ciphed_form = formulario_create_ciphed.CreateForm(request.form)
    idTx = ''
    name_ciphed = ''
    description_ciphed = ''
    name = create_token_ciphed_form.name.data
    description = create_token_ciphed_form.description.data
    amount = create_token_ciphed_form.amount.data
    decimals = create_token_ciphed_form.decimals.data
    password = create_token_ciphed_form.password.data
    if name == None or name == '' or description == None or description == '' or password == None or password == '' or amount == None or amount == '' or decimals == None or decimals == '':
        print('No se puede crear')
    else:
        description_ciphed = cryptocode.encrypt(description, password)
        idTx = createToken(name, description_ciphed, amount, decimals)

    return render_template('create-token-ciphed.html', form = create_token_ciphed_form, name = name, description = description, amount = amount, decimals = decimals, name_ciphed = name_ciphed, description_ciphed = description_ciphed, idTx = idTx)

# WALLETS
@app.route('/wallets', methods = ['GET', 'POST']) 
def wallets():
    wallet_form = formulario_wallets.WalletForm(request.form)
    wallet_address = wallet_form.wallet_address.data
    total_tokens = None
    total_ergs = None
    array_data_tokens = []
    if requests.get('https://api.ergoplatform.com/api/v1/addresses/' + str(wallet_address) + '/balance/confirmed').status_code == 200:
        data_wallet = requests.get('https://api.ergoplatform.com/api/v1/addresses/' + str(wallet_address) + '/balance/confirmed')
        data_wallet = data_wallet.json()
        total_tokens = len(data_wallet['tokens'])
        array_tokens = data_wallet['tokens']
        total_ergs = data_wallet['nanoErgs']/1000000000
        for single_token in array_tokens:
            array_data_tokens.append(single_token)
            print(single_token['tokenId'])
            print(single_token['name'])

    return render_template('wallets.html', form = wallet_form, wallet_address = wallet_address, total_tokens = total_tokens, total_ergs = total_ergs, array_data_tokens = array_data_tokens)

# TOKEN
@app.route('/token/', methods = ['GET', 'POST'])
@app.route('/token/<tokenId>', methods = ['GET', 'POST'])
def token(tokenId):
    token_id = tokenId
    deciphed_form = formulario_deciph.CreateForm(request.form)
    password = deciphed_form.password.data
    description_deciphed = ''
    message_error = ''
    data_token = requests.get('https://api.ergoplatform.com/api/v0/assets/' + tokenId + '/issuingBox')
    data_token = data_token.json()
    name_token = str(data_token[0]['assets'][0]['name'])
    description_token = to_utf8_string(data_token[0]['additionalRegisters']['R5'])[2:]
    if cryptocode.decrypt(description_token, password):
        description_deciphed = cryptocode.decrypt(description_token, password)
    else:
        message_error = 'error password'

    return render_template('token.html', form = deciphed_form, token_id = token_id, password = password, name_token = name_token, description_token = description_token, description_deciphed = description_deciphed, message_error = message_error)

# ADIOS :)
@app.route('/adios')
def adios():
    return 'Adios'

if __name__ == '__main__':
    app.run(debug= True, port=8000)
