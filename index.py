"""
schedulERGweb
============

AUTHOR
    @ladopixel 
CREATED AT
    Friday 10 June 2022 08:00
LAST UPDATE
    Monday 27 June 2022 23:24
"""

from flask import Flask, render_template, request

from ergpy import helper_functions, appkit 

from crypt import methods
import cryptocode
import requests
import hashlib
from PIL import Image
import numpy as np
import cv2
from Crypto.Cipher import AES

import formulario
import formulario_create
import formulario_create_ciphed
import formulario_image_ciphed
import formulario_wallets
import formulario_deciph
import formulario_create_nft_ciphed

app = Flask(__name__)

node_url: str = "http://159.65.11.55:9053/"
ergo = appkit.ErgoAppKit(node_url=node_url)

#################### You seed phrase 
wallet_mnemonic = ''

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

# Resolver URLs IPFS
def resolveIpfs(url):
    ipfsPrefix = 'ipfs://'
    if url[0:7:1] != ipfsPrefix:
        return url
    else:
        print(url.replace(ipfsPrefix, 'https://cloudflare-ipfs.com/ipfs/'))
        return url.replace(ipfsPrefix, 'https://cloudflare-ipfs.com/ipfs/')

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

# CREATE NFT IMG CIPHED
def create_nft_img_ciphed(token_name, token_description, ruta_img_ciphed, ruta_img_IPFS):
    idTx = ''
    token_name = token_name
    token_description = token_description
    image_link = ruta_img_IPFS
    imagen = ruta_img_ciphed
    with open(imagen, 'rb') as f:    
            bytes = f.read()
            hash_local_image = hashlib.sha256(bytes).hexdigest()
            image_hash = appkit.sha256caster(hash_local_image)
    try:
        idTx = helper_functions.create_nft(ergo=ergo, nft_name=token_name, description=token_description, image_link=image_link, image_hash=image_hash, wallet_mnemonic=wallet_mnemonic)
        return idTx
    except:
        idTx = 'ERROR create NFT!'
        return idTx

# INDEX
@app.route('/')
def index():
    return render_template('menu.html')

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

# IMAGE CIPHED
@app.route('/image-ciphed', methods = ['GET', 'POST'])
def image_ciphed():
    img_ciphed_form = formulario_image_ciphed.CreateForm(request.form)
    ruta_image_ciphed = ''
    password = img_ciphed_form.password.data
    ruta_image = img_ciphed_form.ruta_image.data
    mensaje_error = '...'
    if password != None:
        try:
            key = str(password).encode('utf-8')
            iv = b'0000000000000000'
            img = cv2.imread(ruta_image)
            if img.size % 16 > 0:
                row = img.shape[0]
                pad = 16 - (row % 16)  
                img = np.pad(img, ((0, pad), (0, 0), (0, 0))) 
                img[-1, -1, 0] = pad  
            img_bytes = img.tobytes()
            enc_img_bytes = AES.new(key, AES.MODE_CBC, iv).encrypt(img_bytes)
            enc_img = np.frombuffer(enc_img_bytes, np.uint8).reshape(img.shape)
            cv2.imwrite('./static/img/image_ciphed.png', enc_img)
            ruta_image_ciphed = './static/img/image_ciphed.png'
            mensaje_error = 'Cipher ok!'
        except:
            mensaje_error = 'Error image cipher'
    
    return render_template('ciphed-image.html', form = img_ciphed_form, mensaje_error = mensaje_error, ruta_image_ciphed=ruta_image_ciphed)

# CREATE NFT CIPHED
@app.route('/create-nft-ciphed', methods = ['GET', 'POST'])
def create_nft_ciphed():
    create_nft_ciphed_form = formulario_create_nft_ciphed.CreateForm(request.form)
    idTx = ''
    name = ''
    description = ''
    ruta_image_ciphed = ''
    ruta_ipfs = ''
    name = create_nft_ciphed_form.name.data
    description = create_nft_ciphed_form.description.data
    ruta_image_ciphed = create_nft_ciphed_form.ruta_image.data
    ruta_ipfs = create_nft_ciphed_form.ruta_ipfs.data
    mensaje_error = ''
    try:
        idTx = create_nft_img_ciphed(name, description, ruta_image_ciphed, ruta_ipfs)
    except:
        mensaje_error = 'Error creating ciphed NFT'
        
    return render_template('create-nft-ciphed.html', form = create_nft_ciphed_form, name=name, description=description, ruta_image_ciphed=ruta_image_ciphed, idTx=idTx, mensaje_error=mensaje_error)

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
    url_token = ''
    url_token_deciphed = ''
    data_token = requests.get('https://api.ergoplatform.com/api/v0/assets/' + tokenId + '/issuingBox')
    data_token = data_token.json()
    name_token = str(data_token[0]['assets'][0]['name'])
    description_token = to_utf8_string(data_token[0]['additionalRegisters']['R5'])[2:]

    if cryptocode.decrypt(description_token, password):
        description_deciphed = cryptocode.decrypt(description_token, password)
    else:
        message_error = 'error deciphed password'

    if data_token[0]['additionalRegisters']['R9']:
        url_token_ciphed = to_utf8_string(data_token[0]['additionalRegisters']['R9'])[2:]

    if cryptocode.decrypt(url_token_ciphed, password):
        url_token_deciphed = resolveIpfs(cryptocode.decrypt(url_token_ciphed, password))
    else:
        message_error = 'error deciphed url'

    return render_template('token.html', form = deciphed_form, token_id = token_id, password = password, name_token = name_token, description_token = description_token, description_deciphed = description_deciphed, url_token_ciphed=url_token_ciphed, url_token_deciphed=url_token_deciphed, message_error = message_error)

# NFT DECIPHED
@app.route('/nftciphed/', methods = ['GET', 'POST'])
@app.route('/nftciphed/<tokenId>', methods = ['GET', 'POST'])
def nftciphed(tokenId):
    token_id = tokenId
    password = None
    ruta_local = ''
    mensaje = ''
    deciphed_form = formulario_deciph.CreateForm(request.form)
    data_token = requests.get('https://api.ergoplatform.com/api/v0/assets/' + tokenId + '/issuingBox')
    data_token = data_token.json()
    name_token = str(data_token[0]['assets'][0]['name'])
    description_token = str(to_utf8_string(data_token[0]['additionalRegisters']['R5'])[2:])
    url_token = resolveIpfs(to_utf8_string(data_token[0]['additionalRegisters']['R9'])[2:])
    password = deciphed_form.password.data

    if password != None or password == '':
        
        # get ciphed img
        req = requests.get(url_token)
        req.headers['User-Agent']= 'Mozilla/5.0'
        response = req.content
        ruta_local = 'nueva_imagen.png'
        with open(ruta_local, 'wb') as f:
            f.write(response)
        
        key = str(password).encode('utf-8')
        iv = b'0000000000000000'
        enc_img = cv2.imread(ruta_local)
        dec_img_bytes = AES.new(key, AES.MODE_CBC, iv).decrypt(enc_img.tobytes())
        dec_img = np.frombuffer(dec_img_bytes, np.uint8).reshape(enc_img.shape)  # The shape of the encrypted and decrypted image is the same (304, 451, 3)
        pad = int(dec_img[-1, -1, 0])  # Get the stored padding value
        dec_img = dec_img[0:-pad, :, :].copy()  # Remove the padding rows, new shape is (300, 451, 3)
        cv2.imwrite('./static/img/nueva_imagen.png', dec_img)
        ruta_local = 'ok'
        
    return render_template('nft-ciphed.html', form = deciphed_form, token_id = token_id, password = password,name_token = name_token, description_token=description_token, url_token=url_token, ruta_local=ruta_local, mensaje=mensaje)

# CAFE 
@app.route('/cafe')
def cafe():
    return render_template('cafe.html')

# ADIOS :)
@app.route('/adios')
def adios():
    return 'Adios'

if __name__ == '__main__':
    app.run(debug= True, port=8000)
