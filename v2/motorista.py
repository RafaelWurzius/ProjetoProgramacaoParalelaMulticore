import socket
import json

def aceitar_corrida(requisicao):
    """Processa a requisição e "aceita" a corrida."""
    carro_id = requisicao["carro_id"]
    passageiro_id = requisicao["passageiro_id"]
    localizacao = requisicao["localizacao"]
    hora_requisicao = requisicao["hora_requisicao"]

    print(f"Carro {carro_id} aceitou a corrida do passageiro {passageiro_id}.")
    print(f"Localização do passageiro: {localizacao}")
    print(f"Hora da requisição: {hora_requisicao}")
    print("-" * 50)

def servidor_motorista():
    # Configuração do socket
    host = 'localhost'
    port = 65433  # Porta que o backend usa para se comunicar com o motorista

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        print("Servidor motorista aguardando requisições...")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Conectado ao backend {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break

                    # Recebe a requisição do backend
                    requisicao = json.loads(data.decode('utf-8'))
                    print(f"Requisição recebida: {requisicao}")

                    # Aceita a corrida
                    aceitar_corrida(requisicao)

if __name__ == "__main__":
    servidor_motorista()
