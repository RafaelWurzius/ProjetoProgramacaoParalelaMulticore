import socket
import threading
import queue
import time

# Configurações do servidor
HOST = 'localhost'
PORT = 65432

# Definindo o número de carros disponíveis
NUM_CARROS = 10
carros_disponiveis = queue.Queue()
requisicoes_em_espera = queue.Queue()

for i in range(1, NUM_CARROS + 1):
    carros_disponiveis.put(f"Carro {i}")

def terminarCorrida():
    while True:
        for i in range(1, NUM_CARROS + 1):
            time.sleep(2)  # Simulando o tempo de uma corrida
            carros_disponiveis.put(f"Carro {i}")

def processar_requisicoes():
    while True:
        if carros_disponiveis.empty():
            pass
        else:
            cliente, conn, addr = requisicoes_em_espera.get()
            # try:
            carro = carros_disponiveis.get_nowait()
            print(f"{carro} atribuído para {cliente}")

            # Enviar confirmação para o produtor
            conn.sendall(f"{carro} atribuído com sucesso".encode('utf-8'))
            conn.close()

def handle_requisicao(conn, addr):
    # with conn:
    data = conn.recv(1024)
    if data:
        cliente_id = data.decode('utf-8').split()[-1]
        print(f"Recebido: Requisição de corrida do cliente {cliente_id} de {addr}")
        requisicoes_em_espera.put((f"cliente {cliente_id}", conn, addr))

def servidor():
    
    threading.Thread(target=processar_requisicoes, daemon=True).start()
    threading.Thread(target=terminarCorrida, daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_requisicao, args=(conn, addr))
            t.start()

if __name__ == "__main__":
    servidor()
