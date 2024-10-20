import socket
import json
import time
import random
import threading
from datetime import datetime

def gerar_requisicao(id_passageiro):
    # Gera uma localização aleatória (latitude e longitude)
    localizacao = {
        "latitude": round(random.uniform(-90, 90), 6),
        "longitude": round(random.uniform(-180, 180), 6)
    }

    # Hora atual da requisição
    hora_requisicao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Cria o pacote JSON com os dados da requisição
    requisicao = {
        "id": id_passageiro,
        "localizacao": localizacao,
        "hora_requisicao": hora_requisicao
    }
    
    return requisicao

def enviar_requisicao(id_passageiro, host, port):
    # Estabelece conexão com o servidor (backend)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        
        # Gera e envia a requisição
        requisicao = gerar_requisicao(id_passageiro)
        pacote = json.dumps(requisicao).encode('utf-8')  # Converte para JSON e bytes
        s.sendall(pacote)  # Envia a requisição

        print(f"Requisição enviada: {requisicao}")
        
        # Recebe a confirmação de qual carro aceitou a corrida
        data = s.recv(1024)
        confirmacao = json.loads(data.decode('utf-8'))  # Decodifica a resposta
        print(f"Passageiro {id_passageiro}: Confirmação recebida - {confirmacao}")
    
        # time.sleep(random.uniform(1, 3))  # Simula um intervalo aleatório para envio das requisições

def simular_requisicoes_simultaneas(host, port):
    threads = []
    for id_passageiro in range(1, 101):  # Simulando 100 passageiros
        t = threading.Thread(target=enviar_requisicao, args=(id_passageiro, host, port))
        threads.append(t)
        t.start()

    # Aguarda todas as threads terminarem
    for t in threads:
        t.join()

if __name__ == "__main__":
    # Configurações do backend
    HOST = 'localhost'  # IP do servidor
    PORT = 65432        # Porta usada pelo servidor

    simular_requisicoes_simultaneas(HOST, PORT)
