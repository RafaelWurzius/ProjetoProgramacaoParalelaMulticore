import socket
import json
import threading
import time
from queue import Queue
from datetime import datetime

# Lista de carros compartilhada entre as threads (True: disponível, False: ocupado)
carros = [{"id": i, "disponivel": True} for i in range(1, 11)]  # 10 carros
carros_lock = threading.Lock()

# Fila de requisições para cada thread
filas = [Queue() for _ in range(6)]

# Variáveis globais para guardar os tempos das requisições de cada thread
tempos_threads = [None] * 6  # Inicialmente, nenhuma thread fez requisição

def processar_requisicoes(fila, thread_id):
    while True:
        if not fila.empty():
            requisicao = fila.get()
            id_passageiro = requisicao["id"]
            hora_requisicao = datetime.strptime(requisicao["hora_requisicao"], '%Y-%m-%d %H:%M:%S')

            # Atualiza o tempo da thread
            tempos_threads[thread_id] = hora_requisicao

            while True:
                # Verifica se a requisição é a mais antiga
                if requisicao_eh_mais_antiga(thread_id):
                    with carros_lock:  # Acessa a lista de carros com lock
                        # Seleciona o carro disponível mais próximo (aleatoriamente neste caso)
                        carro_disponivel = None
                        for carro in carros:
                            if carro["disponivel"]:
                                carro_disponivel = carro
                                break

                        if carro_disponivel:
                            # Aloca o carro e marca como ocupado
                            carro_disponivel["disponivel"] = False
                            print(f"Thread {thread_id + 1}: Carro {carro_disponivel['id']} alocado para passageiro {id_passageiro}")
                            
                            # Envia a confirmação ao passageiro
                            enviar_confirmacao_passageiro(requisicao["conn"], carro_disponivel)

                            # Envia a requisição ao motorista
                            enviar_ao_motorista(carro_disponivel, requisicao)

                            # Libera a lista
                            break
                        else:
                            print(f"Thread {thread_id + 1}: Todos os carros ocupados. Aguardando...", end="\r")
                            # time.sleep(1)  # Aguarda antes de tentar novamente
                else:
                    # Se não for a requisição mais antiga, espera e tenta novamente
                    # time.sleep(0.5)
                    pass

def requisicao_eh_mais_antiga(thread_id):
    """Verifica se a requisição da thread atual é a mais antiga entre todas as threads."""
    hora_thread = tempos_threads[thread_id]
    if hora_thread is None:
        return False

    for i, tempo in enumerate(tempos_threads):
        if i != thread_id and tempo and tempo < hora_thread:
            return False
    return True

def enviar_confirmacao_passageiro(conn, carro):
    """Envia a confirmação ao passageiro sobre qual carro aceitou a corrida."""
    confirmacao = {
        "mensagem": "Corrida aceita",
        "carro_id": carro["id"]
    }
    conn.sendall(json.dumps(confirmacao).encode('utf-8'))  # Envia a confirmação como JSON

def enviar_ao_motorista(carro, requisicao):
    """Envia a requisição ao motorista via socket."""
    motorista_host = 'localhost'
    motorista_port = 65433  # Porta do servidor 'motorista'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((motorista_host, motorista_port))
        
        dados_motorista = {
            "carro_id": carro["id"],
            "passageiro_id": requisicao["id"],
            "localizacao": requisicao["localizacao"],
            "hora_requisicao": requisicao["hora_requisicao"]
        }

        # Envia os dados ao motorista
        s.sendall(json.dumps(dados_motorista).encode('utf-8'))
        print(f"Requisição enviada ao motorista: {dados_motorista}")

def tratar_conexao(conn, addr):
    """Processa cada conexão de forma paralela."""
    print(f"Conectado a {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break

        requisicao = json.loads(data.decode('utf-8'))
        requisicao["conn"] = conn  # Adiciona a conexão para responder o passageiro
        print(f"Requisição recebida: {requisicao}")

        # Distribui a requisição para a fila de uma das threads
        menor_fila = min(filas, key=lambda q: q.qsize())
        menor_fila.put(requisicao)

def servidor_socket():
    # Configuração do socket
    host = 'localhost'
    port = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(100)  # Aumenta o backlog para 100

        print("Servidor rodando e aguardando requisições...")

        while True:
            conn, addr = s.accept()
            # Cria uma thread para cada conexão recebida
            t = threading.Thread(target=tratar_conexao, args=(conn, addr))
            t.daemon = True
            t.start()

def atualizar_disponibilidade_carros():
    """Thread que periodicamente altera o status dos carros para 'disponível'."""
    while True:
        time.sleep(15)  # Intervalo de 10 segundos para liberar os carros
        with carros_lock:
            for carro in carros:
                if not carro["disponivel"]:
                    carro["disponivel"] = True
                    print(f"Carro {carro['id']} está agora disponível.")
        print("Atualização de disponibilidade de carros concluída.")
        print("-" * 50)

if __name__ == "__main__":
    # Inicializa as threads de processamento
    for i in range(6):
        t = threading.Thread(target=processar_requisicoes, args=(filas[i], i))
        t.daemon = True
        t.start()

    # Inicia a thread de atualização de disponibilidade dos carros
    t_disponibilidade = threading.Thread(target=atualizar_disponibilidade_carros)
    t_disponibilidade.daemon = True
    t_disponibilidade.start()

    # Inicia o servidor de socket
    servidor_socket()
