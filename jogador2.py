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
import tkinter as tk

# Configuração do cliente
HOST = '127.0.0.1'
PORT = 5000

# Cria o cliente socket
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((HOST, PORT))

# Função para receber mensagens do servidor
def receber_mensagens():
    while True:
        try:
            mensagem = cliente.recv(1024).decode('utf-8')
            if not mensagem:
                break  # Sai do loop se não houver mensagem (conexão fechada)
            chat_text.config(state='normal')
            chat_text.insert('end', mensagem + '\n')
            chat_text.config(state='disabled')
            chat_text.see('end')
        except:
            break
    cliente.close()
    root.quit()  # Fecha a interface ao encerrar a conexão

# Função para enviar mensagens
def enviar_mensagem():
    mensagem = f"{entry_message.get()}"
    entry_message.delete(0, 'end')
    cliente.send(mensagem.encode('utf-8'))

# Função para desistir
def desistir():
    cliente.send("DESISTIR".encode('utf-8'))

# Função para contar peças
def contar():
    cliente.send("CONTAR".encode('utf-8'))

# Função para enviar a jogada
def enviar_jogada():
    linha = int(entry_linha.get())
    coluna = int(entry_coluna.get())
    cliente.send(f"JOGADA {linha} {coluna}".encode('utf-8'))

# Função para encerrar o cliente e enviar um comando ao servidor
def encerrar_cliente():
    try:
        cliente.send("SAIR".encode('utf-8'))  # Envia o comando de encerramento
    except:
        pass  # Ignora erros ao enviar mensagem se o cliente já estiver desconectado
    cliente.close()  # Fecha o socket
    root.destroy()  # Fecha a janela do Tkinter

# Interface gráfica com tkinter
root = tk.Tk()
root.title("Jogador 2 - Peças ⚪")


# Tela
chat_text = tk.Text(root, height=25, width=70, state='disabled')
chat_text.grid(row=0, column=0, padx=10, pady=20, sticky="w")

# Campo para entrada de mensagens
def configurar_placeholder(entry, texto):
    def on_focus_in(event):
        # Remove o placeholder apenas se o texto atual for o mesmo do placeholder
        if entry.get() == texto:
            entry.delete(0, 'end')
            entry.config(fg='black')

    def on_focus_out(event):
        # Reinsere o placeholder se o campo estiver vazio
        if entry.get() == "":
            entry.insert(0, texto)
            entry.config(fg='grey')

    # Configuração inicial do placeholder
    entry.insert(0, texto)
    entry.config(fg='grey')

    # Bind dos eventos
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

# Campo para digitar a mensagem
entry_message = tk.Entry(root, width=40)
entry_message.grid(row=1, column=0, padx=10, pady=0, sticky="w")

# Adiciona o placeholder "Digite uma mensagem"
configurar_placeholder(entry_message, "Digite uma mensagem")


# Botões
btn_send_message = tk.Button(root, text="Enviar Mensagem", command=enviar_mensagem, bg="blue", fg="white")
btn_send_message.grid(row=1, column=0, padx=280, pady=0, sticky="w")


# Labels e campos para digitar a jogada
label_linha = tk.Label(root, text="Linha:",)
label_linha.grid(row=2, column=0, padx=10, pady=10, sticky="w")

entry_linha = tk.Entry(root, width=5)
entry_linha.grid(row=2, column=0, padx=50, pady=10, sticky="w")

label_coluna = tk.Label(root, text="Coluna:")
label_coluna.grid(row=2, column=0, padx=90, pady=10, sticky="w")

entry_coluna = tk.Entry(root, width=5)
entry_coluna.grid(row=2, column=0, padx=140, pady=10, sticky="w")

# Botão para enviar jogada
btn_send_jogada = tk.Button(root, text="Enviar Jogada", command=enviar_jogada, bg="green", fg="white")
btn_send_jogada.grid(row=2, column=0, padx=190, pady=10, sticky="w")

# Botão para desistir
btn_desistir = tk.Button(root, text="Desistir", command=desistir, bg="red", fg="white")
btn_desistir.grid(row=2, column=0, padx=285, pady=10, sticky="w")

# Botão para contar peças
btn_contar = tk.Button(root, text="Contar Peças", command=contar, bg="gray", fg="white")
btn_contar.grid(row=2, column=0, padx=345, pady=10, sticky="w")


# Vincula o evento de fechamento da janela ao encerrar_cliente
root.protocol("WM_DELETE_WINDOW", encerrar_cliente)

# Thread para receber mensagens
thread_receber = threading.Thread(target=receber_mensagens)
thread_receber.start()

root.mainloop()