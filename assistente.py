import os
import json
import secrets
import sounddevice as sd
import soundfile as sf
import torchaudio
import torch
from threading import Thread
from nltk import word_tokenize, corpus
from inicializador_modelo import *
from transcritor import *

# Importa o nosso novo módulo atuador
import fazenda

# Configuração de caminhos absolutos (à prova de falhas no Windows)
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
CONFIGURACAO = os.path.join(DIRETORIO_ATUAL, "config.json")
CAMINHO_AUDIO_FALAS = os.path.join(DIRETORIO_ATUAL, "temp")

LINGUAGEM = "portuguese"
TEMPO_GRAVACAO = 5

ATUADORES = [
    {
        "nome": "fazenda",
        "iniciar": fazenda.iniciar,
        "atuar": fazenda.atuar
    }
]

def iniciar_assistente(dispositivo):
    iniciado, processador, modelo = iniciar_modelo(MODELO, dispositivo)

    palavras_de_parada = set(corpus.stopwords.words(LINGUAGEM))

    with open(CONFIGURACAO, "r", encoding="utf-8") as arquivo_configuracao:
        configuracoes = json.load(arquivo_configuracao)
        acoes = configuracoes["acoes"]

    for atuador in ATUADORES:
        atuador["iniciar"]()

    return iniciado, processador, modelo, palavras_de_parada, acoes

def capturar_fala():
    print("\nGravando... (Fale o comando de agricultura)")

    fala = sd.rec(int(TEMPO_GRAVACAO * TAXA_AMOSTRAGEM), samplerate=TAXA_AMOSTRAGEM, channels=1)
    sd.wait()

    print("Gravação finalizada!")
    return fala

def gravar_fala(fala):
    # Cria a pasta temp automaticamente se não existir
    if not os.path.exists(CAMINHO_AUDIO_FALAS):
        os.makedirs(CAMINHO_AUDIO_FALAS)

    gravado = False
    arquivo = os.path.join(CAMINHO_AUDIO_FALAS, f"{secrets.token_hex(32).lower()}.wav")

    try:
        sf.write(arquivo, fala, TAXA_AMOSTRAGEM)
        gravado = True
    except Exception as e:
        print(f"Ocorreu um erro gravando o áudio: {e}")

    return gravado, arquivo

def processar_transcricao(transcricao, palavras_de_parada):
    tokens = word_tokenize(transcricao)
    comando = [token for token in tokens if token not in palavras_de_parada]
    return comando

def validar_comando(comando, acoes):
    valido, acao, objeto, local = False, None, None, None

    # Lógica de validação inteligente: busca as palavras em qualquer ordem na frase
    for acao_configurada in acoes:
        if acao_configurada["nome"] in comando:
            for obj in acao_configurada["dispositivos"]:
                if obj in comando:
                    for loc in acao_configurada.get("locais", []):
                        if loc in comando:
                            acao = acao_configurada["nome"]
                            objeto = obj
                            local = loc
                            valido = True
                            return valido, acao, objeto, local

    return valido, acao, objeto, local

def executar_comando(acao, objeto, local):
    for atuador in ATUADORES:
        atuacao = Thread(target=atuador["atuar"], args=[acao, objeto, local]) 
        atuacao.start()

def exibir_menu():
    print("\n ___________________________________________")
    print("|                                           |")
    print("|        🚜 ASSISTENTE FAZENDA HI-TECH 🌾   |")
    print("|___________________________________________|")
    print("|                                           |")
    print("| [1] 🎙️  Ouvir comando                      |")
    print("| [2] 📜 Listar comandos possíveis          |")
    print("| [3] ❌ Sair do assistente                 |")
    print("|___________________________________________|\n")

def listar_comandos(acoes):
    print("\n" + "="*43)
    print("           COMANDOS RECONHECIDOS           ")
    print("="*43)
    for acao_config in acoes:
        nome_acao = acao_config["nome"].upper()
        objetos = ", ".join(acao_config["dispositivos"])
        locais = ", ".join(acao_config.get("locais", []))
        
        print(f"➜ AÇÃO: {nome_acao}")
        print(f"  Pode atuar sobre: [{objetos}]")
        print(f"  Nos locais:       [{locais}]")
        print("-" * 43)

if __name__ == "__main__":
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"

    iniciado, processador, modelo, palavras_de_parada, acoes = iniciar_assistente(dispositivo)
    
    if iniciado:
        while True:
            exibir_menu()
            opcao = input("Escolha uma opção (1, 2 ou 3): ")

            if opcao == "1":
                fala = capturar_fala()
                gravado, arquivo = gravar_fala(fala)
                
                if gravado:
                    print("\nRealizando transcrição, aguarde...")

                    # O torchaudio agora vai usar o FFmpeg nativo configurado
                    fala_carregada, _ = torchaudio.load(arquivo)
                    transcricao = transcrever(dispositivo, fala_carregada.squeeze(), modelo, processador)
                    
                    print(f"Você disse: '{transcricao}'")

                    comando = processar_transcricao(transcricao, palavras_de_parada)
                    
                    valido, acao, objeto, local = validar_comando(comando, acoes)
                    if valido:
                        executar_comando(acao, objeto, local)
                    else:
                        print("\n[!] Comando não compreendido ou incompleto. Certifique-se de dizer a ação, o objeto e o local.")
            
            elif opcao == "2":
                listar_comandos(acoes)
                
            elif opcao == "3":
                print("\nEncerrando os sistemas da Fazenda Hi-Tech. Até logo!\n")
                break
            
            else:
                print("\n[!] Opção inválida! Por favor, digite 1, 2 ou 3.")
    else:
        print("Não foi possível iniciar o assistente. Verifique os modelos.")