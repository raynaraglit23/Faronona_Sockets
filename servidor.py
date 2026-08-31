# -*- coding: utf-8 -*-
import socket
import threading
from jogo import Jogo, JOGADOR_1, JOGADOR_2
from protocolo import enviar, receber

HOST = "0.0.0.0"
PORTA = 9090

class Servidor:
    def __init__(self):
        self.jogo = Jogo()
        self.clientes = {}
        self.lock = threading.Lock()

    def transmitir(self, mensagem):
        desconectados = []
        for jogador, sock in list(self.clientes.items()):
            try:
                enviar(sock, mensagem)
            except Exception:
                desconectados.append(jogador)
        for jogador in desconectados:
            self.clientes.pop(jogador, None)

    def transmitir_estado(self, aviso=""):
        self.transmitir({
            "tipo": "estado",
            "estado": self.jogo.estado(),
            "aviso": aviso
        })

    def tratar(self, sock, jogador):
        try:
            arquivo = sock.makefile("r", encoding="utf-8")
            for linha in arquivo:
                if not linha.strip():
                    continue

                msg = receber(linha)

                with self.lock:
                    tipo = msg.get("tipo")

                    if tipo == "movimento":
                        origem = tuple(msg.get("origem", []))
                        destino = tuple(msg.get("destino", []))

                        ok, texto, estado = self.jogo.mover(
                            jogador, origem, destino
                        )

                        enviar(sock, {
                            "tipo": "resultado",
                            "ok": ok,
                            "mensagem": texto
                        })

                        self.transmitir_estado(texto)

                    elif tipo == "chat":
                        texto = str(msg.get("mensagem", "")).strip()
                        if texto:
                            self.transmitir({
                                "tipo": "chat",
                                "jogador": jogador,
                                "mensagem": texto
                            })

                    elif tipo == "desistencia":
                        ok, texto, estado = self.jogo.desistir(jogador)

                        self.transmitir({
                            "tipo": "resultado",
                            "ok": ok,
                            "mensagem": texto
                        })
                        self.transmitir_estado(texto)

                    elif tipo == "estado":
                        enviar(sock, {
                            "tipo": "estado",
                            "estado": self.jogo.estado(),
                            "aviso": ""
                        })

        except Exception as e:
            print(f"Jogador {jogador} desconectou: {e}")
        finally:
            with self.lock:
                self.clientes.pop(jogador, None)
            try:
                sock.close()
            except Exception:
                pass

    def iniciar(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORTA))
        servidor.listen(2)

        print("=" * 50)
        print("        SERVIDOR FANORONA")
        print("=" * 50)
        print(f"Aguardando jogadores na porta {PORTA}...")

        while len(self.clientes) < 2:
            sock, endereco = servidor.accept()

            with self.lock:
                jogador = JOGADOR_1 if JOGADOR_1 not in self.clientes else JOGADOR_2
                self.clientes[jogador] = sock

            print(f"Jogador {jogador} conectado: {endereco}")

            enviar(sock, {
                "tipo": "conexao",
                "jogador": jogador,
                "mensagem": f"Você é o Jogador {jogador}."
            })

            enviar(sock, {
                "tipo": "estado",
                "estado": self.jogo.estado(),
                "aviso": "Jogador 1 começa."
            })

            thread = threading.Thread(
                target=self.tratar,
                args=(sock, jogador),
                daemon=True
            )
            thread.start()

        self.transmitir_estado("Os dois jogadores estão conectados. Bom jogo!")

        print("Dois jogadores conectados. Partida iniciada.")

        try:
            while True:
                if self.jogo.finalizado:
                    break
                threading.Event().wait(0.5)
        except KeyboardInterrupt:
            print("\nServidor encerrado.")
        finally:
            servidor.close()

if __name__ == "__main__":
    Servidor().iniciar()
