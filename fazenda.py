import os
import pygame

# Configuração do caminho dos áudios
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
PASTA_AUDIOS = os.path.join(DIRETORIO_ATUAL, "audios_fazenda")

def iniciar():
    # Inicializa o motor de áudio do pygame
    pygame.mixer.init()
    print("🚜 Sistemas da Fazenda Hi-Tech inicializados com sucesso! 🌾")

def tocar_som(nome_arquivo):
    """Função auxiliar para tocar o som sem travar o código se o arquivo não existir"""
    caminho_som = os.path.join(PASTA_AUDIOS, nome_arquivo)
    if os.path.exists(caminho_som):
        pygame.mixer.music.load(caminho_som)
        pygame.mixer.music.play()
    else:
        print(f"  [!] (Aviso: O arquivo de áudio '{nome_arquivo}' não foi encontrado na pasta 'audios_fazenda')")

def atuar(acao, objeto, local):
    preposicoes = {
        "estufa": "na",
        "campo": "no",
        "norte": "no setor",
        "leste": "no setor",
        "sul": "no setor",
        "pasto": "no",
        "celeiro": "no"
    }
    
    preposicao = preposicoes.get(local, "em")

    if acao == "plantar":
        print(f"\n🌱 [FAZENDA] ➜ Plantando sementes de {objeto} {preposicao} {local}. 🌱")
        tocar_som("plantar.mp3")
        
    elif acao == "regar":
        print(f"\n💧 [FAZENDA] ➜ Regando as {objeto} {preposicao} {local}. 💧")
        tocar_som("regar.mp3")
        
    elif acao == "abrir":
        print(f"\n🚪 [FAZENDA] ➜ Abrindo as portas do {objeto} {preposicao} {local}. 🚪")
        tocar_som("abrir_porta.mp3")
        
    elif acao == "alimentar":
        # Escolhe o emoji e o som certo dependendo do animal
        if objeto == "vacas":
            emoji = "🐄"
            som = "vaca.mp3"
        elif objeto == "galinhas":
            emoji = "🐔"
            som = "galinha.mp3"
        elif objeto == "porcos":
            emoji = "🐖"
            som = "porco.mp3"
        else:
            emoji = "🌾"
            som = "alimentar.mp3"

        print(f"\n{emoji} [FAZENDA] ➜ Distribuindo ração para as {objeto} {preposicao} {local}.  {emoji}")
        tocar_som(som)
        
    else:
        print("\n❓ [FAZENDA] ➜ Comando de agricultura não reconhecido.")