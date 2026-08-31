# -*- coding: utf-8 -*-
import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from protocolo import enviar, receber

PORTA = 9090

class ClienteFanorona:
    def __init__(self, root, host):
        self.root = root
        self.host = host
        self.sock = None
        self.jogador = None
        self.estado = None
        self.selecionada = None
        self.bloqueado = False

        self.root.title("Fanorona - Cliente")
        self.root.geometry("1050x700")
        self.root.minsize(900, 600)

        self.montar_interface()

        try:
            self.conectar()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar ao servidor.\n\n{e}")
            self.root.destroy()

    def montar_interface(self):
        topo = tk.Frame(self.root, padx=15, pady=12)
        topo.pack(fill="x")

        self.titulo = tk.Label(
            topo, text="FANORONA",
            font=("Helvetica", 24, "bold")
        )
        self.titulo.pack(side="left")

        self.status = tk.Label(
            topo, text="Conectando...",
            font=("Helvetica", 13, "bold")
        )
        self.status.pack(side="right")

        principal = tk.Frame(self.root, padx=15, pady=5)
        principal.pack(fill="both", expand=True)

        esquerda = tk.Frame(principal)
        esquerda.pack(side="left", fill="both", expand=True)

        direita = tk.Frame(principal, width=300)
        direita.pack(side="right", fill="y")
        direita.pack_propagate(False)

        self.canvas = tk.Canvas(
            esquerda, bg="#ead7b7",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.clicar_tabuleiro)

        tk.Label(
            direita, text="CHAT",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(0, 8))

        self.chat = tk.Text(
            direita, state="disabled",
            wrap="word", height=20
        )
        self.chat.pack(fill="both", expand=True)

        entrada = tk.Frame(direita, pady=8)
        entrada.pack(fill="x")

        self.entrada_chat = tk.Entry(entrada)
        self.entrada_chat.pack(side="left", fill="x", expand=True)
        self.entrada_chat.bind("<Return>", lambda e: self.enviar_chat())

        tk.Button(
            entrada, text="Enviar",
            command=self.enviar_chat
        ).pack(side="right", padx=(5, 0))

        self.info = tk.Label(
            direita, text="",
            justify="left", anchor="w",
            font=("Helvetica", 11)
        )
        self.info.pack(fill="x", pady=8)

        self.btn_desistir = tk.Button(
            direita, text="DESISTIR",
            command=self.desistir,
            height=2
        )
        self.btn_desistir.pack(fill="x", pady=(5, 0))

        rodape = tk.Label(
            self.root,
            text="Clique em uma peça e depois no destino.",
            pady=7
        )
        rodape.pack(fill="x")

    def conectar(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, PORTA))

        self.thread = threading.Thread(
            target=self.receber_mensagens,
            daemon=True
        )
        self.thread.start()

        enviar(self.sock, {"tipo": "estado"})

    def receber_mensagens(self):
        arquivo = self.sock.makefile("r", encoding="utf-8")
        try:
            for linha in arquivo:
                if not linha.strip():
                    continue
                mensagem = receber(linha)
                self.root.after(0, self.processar_mensagem, mensagem)
        except Exception as e:
            self.root.after(
                0,
                lambda: self.adicionar_chat(f"Sistema: conexão encerrada ({e})")
            )

    def processar_mensagem(self, msg):
        tipo = msg.get("tipo")

        if tipo == "conexao":
            self.jogador = msg["jogador"]
            self.root.title(f"Fanorona - Jogador {self.jogador}")
            self.adicionar_chat("Sistema: " + msg.get("mensagem", ""))

        elif tipo == "estado":
            self.estado = msg["estado"]
            self.bloqueado = self.estado["finalizado"]
            self.atualizar_interface()

            aviso = msg.get("aviso", "")
            if aviso:
                self.adicionar_chat("Sistema: " + aviso)

            if self.estado["finalizado"]:
                vencedor = self.estado["vencedor"]
                texto = (
                    "Você venceu!" if vencedor == self.jogador
                    else f"Jogador {vencedor} venceu!"
                )
                messagebox.showinfo("Fim de jogo", texto)

        elif tipo == "chat":
            self.adicionar_chat(
                f"Jogador {msg['jogador']}: {msg['mensagem']}"
            )

        elif tipo == "resultado":
            if not msg.get("ok"):
                self.adicionar_chat("Sistema: " + msg["mensagem"])

    def atualizar_interface(self):
        self.desenhar_tabuleiro()

        if not self.estado:
            return

        turno = self.estado["turno"]
        if self.estado["finalizado"]:
            self.status.config(text="PARTIDA ENCERRADA")
        elif turno == self.jogador:
            self.status.config(text="SUA VEZ")
        else:
            self.status.config(text=f"VEZ DO JOGADOR {turno}")

        self.info.config(
            text=(
                f"Você: Jogador {self.jogador}\n"
                f"Peças - J1: {self.estado['pecas1']} | "
                f"J2: {self.estado['pecas2']}\n"
                f"Turno: Jogador {turno}"
            )
        )

    def desenhar_tabuleiro(self):
        self.canvas.delete("all")
        if not self.estado:
            return

        tab = self.estado["tabuleiro"]
        linhas = len(tab)
        colunas = len(tab[0])

        w = max(self.canvas.winfo_width(), 500)
        h = max(self.canvas.winfo_height(), 400)

        margem_x = 45
        margem_y = 45

        espacox = (w - 2 * margem_x) / (colunas - 1)
        espacoy = (h - 2 * margem_y) / (linhas - 1)

        def ponto(l, c):
            return margem_x + c * espacox, margem_y + l * espacoy

        # Linhas horizontais.
        for l in range(linhas):
            for c in range(colunas - 1):
                x1, y1 = ponto(l, c)
                x2, y2 = ponto(l, c + 1)
                self.canvas.create_line(x1, y1, x2, y2, width=2)

        # Verticais.
        for c in range(colunas):
            for l in range(linhas - 1):
                x1, y1 = ponto(l, c)
                x2, y2 = ponto(l + 1, c)
                self.canvas.create_line(x1, y1, x2, y2, width=2)

        # Diagonais.
        for l in range(linhas - 1):
            for c in range(colunas - 1):
                x1, y1 = ponto(l, c)
                x2, y2 = ponto(l + 1, c + 1)
                self.canvas.create_line(x1, y1, x2, y2, width=1)

                x1, y1 = ponto(l, c + 1)
                x2, y2 = ponto(l + 1, c)
                self.canvas.create_line(x1, y1, x2, y2, width=1)

        # Pontos e peças.
        raio = 14
        for l in range(linhas):
            for c in range(colunas):
                x, y = ponto(l, c)

                if self.selecionada == (l, c):
                    self.canvas.create_oval(
                        x - 21, y - 21, x + 21, y + 21,
                        outline="#d4a72c", width=4
                    )

                self.canvas.create_oval(
                    x - 5, y - 5, x + 5, y + 5,
                    fill="#3f3f3f", outline=""
                )

                peca = tab[l][c]
                if peca != 0:
                    # Jogador 1: claro; Jogador 2: escuro.
                    preenchimento = "#f7f1df" if peca == 1 else "#333333"
                    contorno = "#333333" if peca == 1 else "#111111"

                    self.canvas.create_oval(
                        x - raio, y - raio,
                        x + raio, y + raio,
                        fill=preenchimento,
                        outline=contorno,
                        width=2
                    )

    def clicar_tabuleiro(self, event):
        if not self.estado or self.estado["finalizado"]:
            return

        if self.estado["turno"] != self.jogador:
            return

        linhas = len(self.estado["tabuleiro"])
        colunas = len(self.estado["tabuleiro"][0])

        w = max(self.canvas.winfo_width(), 500)
        h = max(self.canvas.winfo_height(), 400)
        margem_x = 45
        margem_y = 45
        espacox = (w - 2 * margem_x) / (colunas - 1)
        espacoy = (h - 2 * margem_y) / (linhas - 1)

        c = round((event.x - margem_x) / espacox)
        l = round((event.y - margem_y) / espacoy)

        if not (0 <= l < linhas and 0 <= c < colunas):
            return

        if abs(event.x - (margem_x + c * espacox)) > 25:
            return
        if abs(event.y - (margem_y + l * espacoy)) > 25:
            return

        if self.selecionada is None:
            if self.estado["tabuleiro"][l][c] == self.jogador:
                self.selecionada = (l, c)
                self.desenhar_tabuleiro()
        else:
            origem = self.selecionada
            destino = (l, c)

            if origem == destino:
                self.selecionada = None
                self.desenhar_tabuleiro()
                return

            enviar(self.sock, {
                "tipo": "movimento",
                "origem": list(origem),
                "destino": list(destino)
            })

            self.selecionada = None
            self.desenhar_tabuleiro()

    def enviar_chat(self):
        texto = self.entrada_chat.get().strip()
        if not texto:
            return

        enviar(self.sock, {
            "tipo": "chat",
            "mensagem": texto
        })
        self.entrada_chat.delete(0, "end")

    def adicionar_chat(self, texto):
        self.chat.config(state="normal")
        self.chat.insert("end", texto + "\n")
        self.chat.see("end")
        self.chat.config(state="disabled")

    def desistir(self):
        if not self.estado or self.estado["finalizado"]:
            return

        confirmar = messagebox.askyesno(
            "Desistir",
            "Tem certeza que deseja desistir?"
        )
        if confirmar:
            enviar(self.sock, {"tipo": "desistencia"})


def main():
    import sys

    if len(sys.argv) >= 2:
        host = sys.argv[1]
    else:
        host = "127.0.0.1"

    root = tk.Tk()
    ClienteFanorona(root, host)
    root.mainloop()


if __name__ == "__main__":
    main()
