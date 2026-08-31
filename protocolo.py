# -*- coding: utf-8 -*-
import json

def enviar(sock, dados):
    mensagem = json.dumps(dados, ensure_ascii=False) + "\n"
    sock.sendall(mensagem.encode("utf-8"))

def receber(linha):
    return json.loads(linha)
