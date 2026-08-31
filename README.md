# Fanorona - Projeto de Sockets

Projeto da disciplina de Programação Paralela e Distribuída.

## Tecnologias

- Python 3
- TCP Socket
- threading
- Tkinter
- JSON

## Arquivos

- `servidor.py` - servidor da partida.
- `cliente.py` - interface gráfica do jogador.
- `jogo.py` - regras e estado do Fanorona.
- `protocolo.py` - envio e recebimento das mensagens JSON.

## Como executar

Abra três terminais.

### Terminal 1 - servidor

```bash
python servidor.py
```

### Terminal 2 - jogador 1

```bash
python cliente.py
```

### Terminal 3 - jogador 2

```bash
python cliente.py
```

Para testar em computadores diferentes, execute o servidor em uma máquina e, nos clientes, informe o IP do servidor:

```bash
python cliente.py 192.168.0.10
```

A porta padrão é `9090`.

## Observação

Esta primeira versão já possui a arquitetura cliente/servidor, dois jogadores,
controle de turno, movimentação, capturas, sequência de capturas, chat,
desistência e indicação de vencedor.

A representação das diagonais e a configuração inicial do tabuleiro podem ser
ajustadas conforme a variante de Fanorona adotada pelo professor.
