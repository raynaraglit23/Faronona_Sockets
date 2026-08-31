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
python3 servidor.py
```

### Terminal 2 - jogador 1

```bash
python3 cliente.py
```

### Terminal 3 - jogador 2

```bash
python3 cliente.py
```

Para testar em computadores diferentes, execute o servidor em uma máquina e, nos clientes, informe o IP do servidor:

```bash
python cliente.py 192.168.0.10
```

A porta padrão é `9090`.

## Observação

Caso não tenha instalado 

```bash
brew install python
```

```bash
brew install python-tk@3.14
```
