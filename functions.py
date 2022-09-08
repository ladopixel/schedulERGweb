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
def resolve_ipfs(url):
    ipfs_prefix = 'ipfs://'
    if url[0:7:1] != ipfs_prefix:
        return url
    else:
        print(url.replace(ipfs_prefix, 'https://cloudflare-ipfs.com/ipfs/'))
        return url.replace(ipfs_prefix, 'https://cloudflare-ipfs.com/ipfs/')
