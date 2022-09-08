"""
schedulERGweb
============

AUTHOR @ladopixel
CREATED AT
    Friday 10 June 2022 08:00
LAST UPDATE
    Monday 8 September 2022
"""
import cryptocode
import cv2
import hashlib
from PIL import Image
import requests

from flask import Flask, render_template, request
from ergpy import helper_functions, appkit
from dotenv import dotenv_values
from Crypto.Cipher import AES
from crypt import methods
import numpy as np

from functions import to_utf8_string, resolve_ipfs
from formulario import Send_erg, Create_token, Image_ciphed, Create_token_ciphed, Wallet_form, Create_nft_ciphed, Create_deciph


app = Flask(__name__)

node_url: str = "http://159.65.11.55:9053/"
ergo = appkit.ErgoAppKit(node_url=node_url)

# You seed phrase
private = dotenv_values('.env')
wallet_mnemonic = private['PASSWORD']



# SEND ERG
def send_erg(receiver, cantidad):
    cantidad_float = float(cantidad)
    amount = [cantidad_float]
    receiver_Addresses = [receiver]
    print(f'enviando{str(amount)} ERG to {str(receiver_Addresses)}')
    try:
        print('Transaction OK ↓')
        return(helper_functions.simple_send(
                                    ergo=ergo,
                                    amount=amount,
                                    wallet_mnemonic=wallet_mnemonic,
                                    receiver_addresses=receiver_Addresses))
    except Exception as ex:
        print(f'ERROR Transaction! → {ex}')


# CREATE TOKEN
def create_token(token_name, token_description, token_amount, token_decimals):
    token_amount = int(token_amount)
    token_decimals = int(token_decimals)
    try:
        print('Transaction OK ↓')
        return(helper_functions.create_token(
                                    ergo=ergo,
                                    token_name=token_name,
                                    description=token_description,
                                    token_amount=token_amount,
                                    token_decimals=token_decimals,
                                    wallet_mnemonic=wallet_mnemonic))
    except Exception as ex:
        print(f'ERROR creating token! → {ex}')


# CREATE NFT IMG CIPHED
def create_nft_img_ciphed(
                        token_name,
                        token_description,
                        ruta_img_ciphed,
                        ruta_img_IPFS):
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
        idTx = helper_functions.create_nft(
                                    ergo=ergo,
                                    nft_name=token_name,
                                    description=token_description,
                                    image_link=image_link,
                                    image_hash=image_hash,
                                    wallet_mnemonic=wallet_mnemonic)
        return idTx
    except Exception as ex:
        idTx = f'ERROR create NFT! → {ex}'
        return idTx


# INDEX
@app.route('/')
def index():
    return render_template('menu.html')


# SEND ERG
@app.route('/send', methods=['GET', 'POST'])
def send():
    idTx = ''
    comment_form = Send_erg(request.form)
    wallet_address = comment_form.wallet_address.data
    amount = comment_form.amount.data
    if wallet_address is not None:
        idTx = send_erg(wallet_address, amount)

    return render_template(
                            'send-erg.html',
                            form=comment_form,
                            wallet_address=wallet_address,
                            amount=amount,
                            idTx=idTx)


# CREATE TOKEN
@app.route('/create-token', methods=['GET', 'POST'])
def create_token():
    idTx = ''
    create_token_form = Create_token(request.form)
    name = create_token_form.name.data
    description = create_token_form.description.data
    amount = create_token_form.amount.data
    decimals = create_token_form.decimals.data
    if name is None or name == '' or description is None or description == '' or amount is None or amount == '' or decimals is None or decimals == '':
        print('No se puede crear')
    else:
        idTx = create_token(name, description, amount, decimals)

    return render_template(
                            'create-token.html',
                            form=create_token_form,
                            name=name,
                            description=description,
                            amount=amount,
                            decimals=decimals,
                            idTx=idTx)


# CREATE TOKEN CIPHED
@app.route('/create-token-ciphed', methods=['GET', 'POST'])
def create_token_ciphed():
    create_token_ciphed_form = Create_token_ciphed(request.form)
    idTx = ''
    name_ciphed = ''
    description_ciphed = ''
    name = create_token_ciphed_form.name.data
    description = create_token_ciphed_form.description.data
    amount = create_token_ciphed_form.amount.data
    decimals = create_token_ciphed_form.decimals.data
    password = create_token_ciphed_form.password.data
    if name is None or name == '' or description is None or description == '' or password is None or password == '' or amount is None or amount == '' or decimals is None or decimals == '':
        print('No se puede crear')
    else:
        description_ciphed = cryptocode.encrypt(description, password)
        idTx = create_token(name, description_ciphed, amount, decimals)

    return render_template(
                            'create-token-ciphed.html',
                            form=create_token_ciphed_form,
                            name=name,
                            description=description,
                            amount=amount,
                            decimals=decimals,
                            name_ciphed=name_ciphed,
                            description_ciphed=description_ciphed,
                            idTx=idTx)


# IMAGE CIPHED
@app.route('/image-ciphed', methods=['GET', 'POST'])
def image_ciphed():
    img_ciphed_form = Image_ciphed(request.form)
    ruta_image_ciphed = ''
    password = img_ciphed_form.password.data
    ruta_image = img_ciphed_form.ruta_image.data
    mensaje_error = '...'
    if password is not None:
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
        except Exception as ex:
            mensaje_error = f'Error image ciphed → {ex}'

    return render_template(
                            'ciphed-image.html',
                            form=img_ciphed_form,
                            mensaje_error=mensaje_error,
                            ruta_image_ciphed=ruta_image_ciphed)


# CREATE NFT CIPHED
@app.route('/create-nft-ciphed', methods=['GET', 'POST'])
def create_nft_ciphed():
    create_nft_ciphed_form = Create_nft_ciphed(request.form)
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
        idTx = create_nft_img_ciphed(
                                        name,
                                        description,
                                        ruta_image_ciphed,
                                        ruta_ipfs)
    except Exception as ex:
        mensaje_error = 'Error creating ciphed NFT → {ex}'

    return render_template(
                            'create-nft-ciphed.html',
                            form=create_nft_ciphed_form,
                            name=name,
                            description=description,
                            ruta_image_ciphed=ruta_image_ciphed,
                            idTx=idTx,
                            mensaje_error=mensaje_error)


# WALLETS
@app.route('/wallets', methods=['GET', 'POST'])
def wallets():
    wallet_form = Wallet_form(request.form)
    wallet_address = wallet_form.wallet_address.data
    total_tokens = None
    total_ergs = None
    array_data_tokens = []
    if requests.get(f'https://api.ergoplatform.com/api/v1/addresses/{wallet_address}/balance/confirmed').status_code == 200:
        data_wallet = requests.get(f'https://api.ergoplatform.com/api/v1/addresses/{wallet_address}/balance/confirmed')
        data_wallet = data_wallet.json()
        total_tokens = len(data_wallet['tokens'])
        array_tokens = data_wallet['tokens']
        total_ergs = data_wallet['nanoErgs']/1000000000
        for single_token in array_tokens:
            array_data_tokens.append(single_token)
            print(single_token['tokenId'])
            print(single_token['name'])

    return render_template(
                            'wallets.html',
                            form=wallet_form,
                            wallet_address=wallet_address,
                            total_tokens=total_tokens,
                            total_ergs=total_ergs,
                            array_data_tokens=array_data_tokens)


# TOKEN
@app.route('/token/', methods=['GET', 'POST'])
@app.route('/token/<tokenId>', methods=['GET', 'POST'])
def token(tokenId):
    token_id = tokenId
    deciphed_form = Create_deciph(request.form)
    password = deciphed_form.password.data
    description_deciphed = ''
    message_error = ''
    url_token = ''
    url_token_ciphed = ''
    url_token_deciphed = ''
    data_token = requests.get(f'https://api.ergoplatform.com/api/v0/assets/{tokenId}/issuingBox')
    data_token = data_token.json()
    name_token = str(data_token[0]['assets'][0]['name'])
    description_token = to_utf8_string(data_token[0]['additionalRegisters']['R5'])[2:]

    if cryptocode.decrypt(description_token, password):
        description_deciphed = cryptocode.decrypt(description_token, password)
    else:
        message_error = 'error deciphed password'

    try:
        if data_token[0]['additionalRegisters']['R9']:
            url_token_ciphed = to_utf8_string(data_token[0]['additionalRegisters']['R9'])[2:]
    except Exception as ex:
        pass

    if cryptocode.decrypt(url_token_ciphed, password):
        url_token_deciphed = resolve_ipfs(cryptocode.decrypt(url_token_ciphed, password))
    else:
        message_error = 'error deciphed url'

    return render_template(
                            'token.html',
                            form=deciphed_form,
                            token_id=token_id,
                            password=password,
                            name_token=name_token,
                            description_token=description_token,
                            description_deciphed=description_deciphed,
                            url_token_ciphed=url_token_ciphed,
                            url_token_deciphed=url_token_deciphed,
                            message_error=message_error)


# NFT DECIPHED
@app.route('/nftciphed/', methods=['GET', 'POST'])
@app.route('/nftciphed/<tokenId>', methods=['GET', 'POST'])
def nft_ciphed(tokenId):
    token_id = tokenId
    password = None
    ruta_local = ''
    mensaje = ''
    deciphed_form = Create_deciph(request.form)
    data_token = requests.get(f'https://api.ergoplatform.com/api/v0/assets/{tokenId}/issuingBox')
    data_token = data_token.json()
    name_token = str(data_token[0]['assets'][0]['name'])
    description_token = str(to_utf8_string(data_token[0]['additionalRegisters']['R5'])[2:])
    url_token = resolve_ipfs(to_utf8_string(data_token[0]['additionalRegisters']['R9'])[2:])
    password = deciphed_form.password.data

    if password is not None or password == '':

        # get ciphed img
        req = requests.get(url_token)
        req.headers['User-Agent'] = 'Mozilla/5.0'
        response = req.content
        ruta_local = 'nueva_imagen.png'
        with open(ruta_local, 'wb') as f:
            f.write(response)

        key = str(password).encode('utf-8')
        iv = b'0000000000000000'
        enc_img = cv2.imread(ruta_local)
        dec_img_bytes = AES.new(key, AES.MODE_CBC, iv).decrypt(enc_img.tobytes())
        # The shape of the encrypted and decrypted image is the same (304, 451, 3)
        dec_img = np.frombuffer(dec_img_bytes, np.uint8).reshape(enc_img.shape)
        # Get the stored padding value
        pad = int(dec_img[-1, -1, 0])
        # Remove the padding rows, new shape is (300, 451, 3)
        dec_img = dec_img[0:-pad, :, :].copy()
        cv2.imwrite('./static/img/nueva_imagen.png', dec_img)
        ruta_local = 'ok'

    return render_template(
                            'nft-ciphed.html',
                            form=deciphed_form,
                            token_id=token_id,
                            password=password,
                            name_token=name_token,
                            description_token=description_token,
                            url_token=url_token,
                            ruta_local=ruta_local,
                            mensaje=mensaje)


# CAFE
@app.route('/cafe')
def cafe():
    return render_template('cafe.html')


# ADIOS :)
@app.route('/adios')
def adios():
    return 'Adios'


if __name__ == '__main__':
    app.run(debug=True, port=8000)
