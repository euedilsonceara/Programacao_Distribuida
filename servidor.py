# CÓDIGO DESENVOLVIDO DURANTE A DISCIPLINA DE PROGRAMAÇÃO PARALELA E DISTRIBUÍDA (PPD)
# UNIVERSIDADE: INSTITUTO FEDERAL DE EDUCAÇÃO, CIÊNCIA E TECNOLOGIA DO CEARÁ (IFCE) - CAMPUS FORTALEZA
# CURSO: ENGENHARIA DA COMPUTAÇÃO
# DATA: 20/11/2024
# DENSENVOLVEDOR: JOSÉ EDILSON CEARÁ GOMES FILHO

# INSTRUÇÕES
# 1. EXECUTE PRIMEIRAMENTE O ARQUIVO servidor.py
# 2. EM SEGUIDA EXECUTE O ARQUIVO jogador1.py EM UM TERMINAL DEDICADO
# 3. FINALIZE EXECUTANDO O ARQUIVO jogador2.py EM UM OUTRO TERMINAL
# 4. PRONTO! AGORA JOGUE E DESFRUTE DO JOGO OTHELLO (REVERSI), SEMPRE ACOMPANHANDO AS MENSAGENS NA TELA!

##################################################################################################################

# Importação das bibliotecas
import socket
import threading
import time

# Configurações do servidor
HOST = '127.0.0.1'
PORT = 5000

# Inicializando o tabuleiro 8x8 para o jogo Othello
tabuleiro = [
    ["❌", "❌", "❌", "❌", "❌", "❌", "❌", "❌"],
    ["❌", "❌", "❌", "❌", "❌", "❌", "❌", "❌"],
    ["❌", "❌", "❌", "❌", "❌", "❌", "❌", "❌"],
    ["❌", "❌", "❌", "⚪", "⚫", "❌", "❌", "❌"],  # Peças iniciais
    ["❌", "❌", "❌", "⚫", "⚪", "❌", "❌", "❌"],  # Peças iniciais
    ["❌", "❌", "❌", "❌", "❌", "❌", "❌", "❌"],
    ["❌", "❌", "❌", "❌", "❌", "❌", "❌", "❌"],
    ["❌", "❌", "❌", "❌", "❌", "❌", "❌", "❌"]
]


# Função para enviar a mensagem a todos os jogadores
def enviar_mensagem_para_todos(mensagem):
    for cliente in clientes:
        cliente.send(mensagem.encode('utf-8'))


# Função para tratar a desistência de um jogador
def tratar_desistencia(cliente):
    # Envia a mensagem de desistência para o jogador que desistiu
    cliente.send("\nVocê perdeu por desistência ❌".encode('utf-8'))
    
    # Envia mensagem de vitória para o oponente
    for oponente in clientes:
        if oponente != cliente:
            oponente.send("\nSeu oponente desistiu. Você é o grande vencedor 🏆".encode('utf-8'))
    
    # Espera 5 segundos antes de encerrar as conexões
    time.sleep(5)
    
    # Fecha as conexões com ambos os jogadores e limpa a lista
    for jogador in clientes:
        jogador.close()
    clientes.clear()


# Função para passar o turno
def passar_turno(jogador_atual):
    if jogador_atual == '⚫':
        return '⚪' 
    elif jogador_atual == '⚪':
        return '⚫'
    

# Função para verificar se uma jogada é válida
def jogada_valida(jogador, linha, coluna):
    
    # Verifica se a posição está vazia
    if tabuleiro[linha][coluna] != "❌":
        return False

    # Direções horizontais, verticais e diagonais
    direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]  
    for direcao in direcoes:
        x, y = linha + direcao[0], coluna + direcao[1]
        peças_vira = []

        while 0 <= x < 8 and 0 <= y < 8 and tabuleiro[x][y] != "❌":
            if tabuleiro[x][y] == jogador:  # Encontrou uma peça do jogador
                if peças_vira:
                    return True  # Jogada válida
                break
            peças_vira.append((x, y))
            x += direcao[0]
            y += direcao[1]

    return False


def aplicar_jogada(jogador, linha, coluna):
    tabuleiro[linha][coluna] = jogador

    # Virar as peças do oponente
    direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for direcao in direcoes:
        x, y = linha + direcao[0], coluna + direcao[1]
        peças_vira = []

        while 0 <= x < 8 and 0 <= y < 8 and tabuleiro[x][y] != "❌":
            if tabuleiro[x][y] == jogador:  # Encontrou uma peça do jogador
                if peças_vira:
                    for px, py in peças_vira:
                        tabuleiro[px][py] = jogador  # Vira as peças
                break
            peças_vira.append((x, y))
            x += direcao[0]
            y += direcao[1]


# Função para verificar se o jogo terminou
def jogo_terminado():
    # Verifica se todos os espaços estão ocupados ou se nenhum jogador pode fazer uma jogada
    for i in range(8):
        for j in range(8):
            if tabuleiro[i][j] == "❌":
                return False
    return True


# Função para contar as peças de cada jogador
def contar_pecas():
    pretas = sum(linha.count('⚫') for linha in tabuleiro)
    brancas = sum(linha.count('⚪') for linha in tabuleiro)
    return pretas, brancas

# Função para mostrar a contagem das peças
def conta(cliente):
    pecas_pretas, pecas_brancas = contar_pecas()
    cliente.send(f"{pecas_pretas} peças pretas ⚫".encode('utf-8'))
    cliente.send(f"{pecas_brancas} peças brancas ⚪\n".encode('utf-8'))


# Função para determinar o vencedor
def verificar_vencedor():
    pretas, brancas = contar_pecas()
    if pretas > brancas:
        return '⚫'  # Jogador com as peças pretas vence
    elif brancas > pretas:
        return '⚪'  # Jogador com as peças brancas vence
    else:
        return 'EMPATE'  # Empate

# Função para enviar o tabuleiro atualizado aos jogadores
def enviar_tabuleiro_para_todos():
    tabuleiro_visualizado = "\n".join(["".join(linha) for linha in tabuleiro])
    for cliente in clientes:
        cliente.send(f"\nTabuleiro Atualizado:\n{tabuleiro_visualizado}\n".encode('utf-8'))

# Função para dar início ao jogo e oferecer instruções
def jogo_iniciado():
    for cliente in clientes:
        cliente.send("INSTRUÇÕES:\n".encode('utf-8'))
        cliente.send("1. O jogador com as peças pretas ⚫ inicia!\n".encode('utf-8'))
        cliente.send("2. Utilize os campos linha e coluna para definir o local da peça.\n".encode('utf-8'))
        cliente.send("3. Utilize entradas de 0 a 7 para linha e de 0 a 7 para as colunas.\n".encode('utf-8'))
        cliente.send("4. Digite uma mensagem e envie ao oponente caso queira interagir.\n\n".encode('utf-8'))
        cliente.send("JOGO INICIADO 🕹️\n".encode('utf-8'))

# Lista para armazenar as conexões dos jogadores e identificadores
clientes = []

# Identificadores para os jogadores
ids_jogadores = ['1', '2']  

# Variavel de controle do numero da jogada
jogada = 1

# Função para lidar com as conexões dos jogadores
def gerenciar_cliente(cliente, identificador):
    if identificador == '1':
        jogador_atual = '⚫'
    elif identificador == '2': 
        jogador_atual = '⚪'
    else:
        jogador_atual = 'Sem Id'

    print(f'Jogador(a) {identificador} conectado(a) ao servidor! ✅')
    
    # Envia uma mensagem personalizada para o jogador que acabou de se conectar
    cliente.send(f"Conexão estabelecida com o servidor! ✅\n".encode('utf-8'))
    cliente.send(f"Bem-vindo(a) ao Jogo Othello (Reversi)!\n".encode('utf-8'))
    if identificador == '1':
        cliente.send(f"Você é o(a) Jogador(a) {identificador}! Suas peças são as pretas ⚫!\n\n".encode('utf-8'))
        cliente.send(f"Aguardando a conexão do oponente...!\n".encode('utf-8'))
    else:
        cliente.send(f"Você é o(a) Jogador(a) {identificador}! Suas peças são as brancas ⚪!\n\n".encode('utf-8'))
        jogo_iniciado()
        enviar_tabuleiro_para_todos()
        cliente.send(f"\nAguarde sua vez de jogar!\n".encode('utf-8'))

    # Recebe e retransmite mensagens para todos os jogadores   
    while True:
        try:
            mensagem = cliente.recv(1024).decode('utf-8')

            # Verifica se o cliente desistiu do jogo
            if mensagem == 'DESISTIR':
                tratar_desistencia(cliente)
                break

            if mensagem == 'CONTAR':
                conta(cliente)

            if mensagem == 'SAIR':
                pass

            elif mensagem.startswith("JOGADA"):
                _, linha, coluna = mensagem.split()
                linha, coluna = int(linha), int(coluna)

                global jogada

                if contar_pecas() == (2, 2) and jogador_atual == '⚪':
                    cliente.send("Ainda não é sua vez! Aguarde seu oponente jogar!.\n".encode('utf-8'))

                elif ((identificador == '1' and jogador_atual == '⚫') or (identificador == '2' and jogador_atual == '⚪')):
                    
                    if jogada_valida(jogador_atual, linha, coluna):
                        aplicar_jogada(jogador_atual, linha, coluna)
                        jogada += 1
                        enviar_mensagem_para_todos(f"Jogador {jogador_atual} fez a jogada em {linha}, {coluna}")
                        # Alterna o turno após a jogada
                        jogador_atual = passar_turno(jogador_atual)  # Alterna o jogador
                        enviar_mensagem_para_todos(f"É a vez do jogador {jogador_atual} agora.\n") 
                        enviar_tabuleiro_para_todos()
                        
                        if jogo_terminado():
                            vencedor = verificar_vencedor()
                            if vencedor == 'EMPATE':
                                enviar_mensagem_para_todos("\nO jogo terminou em empate!")
                            else:
                                enviar_mensagem_para_todos(f"\nJogador {vencedor} venceu!")
                            break 

                    else:
                        cliente.send("Jogada inválida! Tente novamente.\n".encode('utf-8'))


                else:                    
                    #if (identificador == '1' and jogador_atual == '⚪' or identificador == '2' and jogador_atual == '⚫'):

                    pretas = contar_pecas()[0]
                    brancas = contar_pecas()[1]
                    soma = pretas + brancas

                    if (soma < 6):
                        cliente.send("Ainda não é sua vez! Aguarde seu oponente jogar!.\n".encode('utf-8'))
                        
                    elif ((jogada % 2) != 0 and identificador == '2') or ((jogada % 2) == 0 and identificador == '1'):
                        cliente.send("Ainda não é sua vez! Aguarde seu oponente jogar!.\n".encode('utf-8'))
                    
                    else:
                        jogador_atual = passar_turno(jogador_atual)

                        if jogada_valida(jogador_atual, linha, coluna):
                            aplicar_jogada(jogador_atual, linha, coluna)
                            jogada += 1
                            enviar_mensagem_para_todos(f"Jogador {jogador_atual} fez a jogada em {linha}, {coluna}")
                            # Alterna o turno após a jogada
                            jogador_atual = passar_turno(jogador_atual)  # Alterna o jogador
                            enviar_mensagem_para_todos(f"É a vez do jogador {jogador_atual} agora.\n") 
                            enviar_tabuleiro_para_todos()
                                
                            if jogo_terminado():
                                vencedor = verificar_vencedor()
                                if vencedor == 'EMPATE':
                                    enviar_mensagem_para_todos("O jogo terminou em empate!")
                                else:
                                    enviar_mensagem_para_todos(f"Jogador {vencedor} venceu!")
                                break

                        else:
                            cliente.send("Jogada inválida! Tente novamente.\n".encode('utf-8'))


            elif mensagem:
                enviar_mensagem_para_todos(f"Mensagem do Jogador {identificador}: {mensagem}\n")

    
        except ConnectionResetError:
            # Captura a desconexão de um cliente
            print(f"Jogador(a) {identificador} desconectado(a)!")
            for oponente in clientes:
                if oponente != cliente:
                    oponente.send("Seu oponente se desconectou!\nVocê é o grande vencedor! 🏆".encode('utf-8'))
            time.sleep(8)  # Dá tempo para o jogador ler a mensagem
            for jogador in clientes:
                jogador.close()
            clientes.clear()
            break


# Inicialização do servidor
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORT))
servidor.listen(2)
print(f'Servidor iniciado em {HOST}:{PORT}')
print(f'Aguardando jogadores se conectarem...\n')

# Aceita conexões de jogadores
jogador_indice = 0
while jogador_indice < 2:
    cliente, endereco = servidor.accept()
    clientes.append(cliente)
    identificador = ids_jogadores[jogador_indice]
    thread = threading.Thread(target=gerenciar_cliente, args=(cliente, identificador))
    thread.start()
    jogador_indice += 1
    print(f"{cliente}\n")
print(f"Jogo Iniciado! Os 2 jogadores estão conectados!")