import socket
import threading

# Configurações do cliente
HOST = 'localhost'
PORT = 65432

def enviar_requisicao(cliente_id):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        mensagem = f"Requisicao de corrida do cliente {cliente_id}"
        s.sendall(mensagem.encode('utf-8'))

        # Receber a confirmação do consumidor
        confirmacao = s.recv(1024)
        print(f"Cliente {cliente_id} recebeu: {confirmacao.decode('utf-8')}")

def criar_thread_para_requisicao(cliente_id):
    t = threading.Thread(target=enviar_requisicao, args=(cliente_id,))
    t.start()

if __name__ == "__main__":
    for i in range(1, 101):  # Simulando 100 requisições simultâneas
        criar_thread_para_requisicao(i)
