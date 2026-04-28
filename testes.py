import sys
sys.stdout.reconfigure(encoding='utf-8')

import unittest
import torch
import torchaudio
import os


from assistente import iniciar_assistente, processar_transcricao, validar_comando
from transcritor import transcrever

PASTA_AUDIOS = "audios_testes" 


AUDIO_ABRIR = os.path.join(PASTA_AUDIOS, "abrir_galinheiro_sul.wav")
AUDIO_ALIMENTAR_PORCOS = os.path.join(PASTA_AUDIOS, "alimentar_porcos_celeiro.wav")
AUDIO_ALIMENTAR_VACAS = os.path.join(PASTA_AUDIOS, "alimentar_vacas_celeiro.wav")
AUDIO_PLANTAR = os.path.join(PASTA_AUDIOS, "plantar_batata_norte.wav")
AUDIO_REGAR_CAMPO = os.path.join(PASTA_AUDIOS, "regar_plantacoes_campo.wav")
AUDIO_REGAR_ESTUFA = os.path.join(PASTA_AUDIOS, "regar_plantacoes_estufa.wav")

class TestesFazenda(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Inicializa a IA uma única vez para todos os testes."""
        cls.dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
        print("\n[TESTES] Inicializando os modelos de IA para os testes. Aguarde...")
        cls.iniciado, cls.processador, cls.modelo, cls.palavras_de_parada, cls.acoes = iniciar_assistente(cls.dispositivo)

    def testar_01_assistente_iniciado(self):
        self.assertTrue(self.iniciado, "Falha: O assistente não iniciou corretamente.")

    def auxiliar_testar_comando(self, caminho_audio, acao_esperada):
        """Função que automatiza o processo de teste de cada áudio."""
        fala, _ = torchaudio.load(caminho_audio)
        self.assertIsNotNone(fala, f"Falha ao carregar o áudio -> {caminho_audio}")

        transcricao = transcrever(self.dispositivo, fala.squeeze(), self.modelo, self.processador)
        self.assertIsNotNone(transcricao, "Falha: A transcrição falhou e retornou vazia.")

        comando = processar_transcricao(transcricao, self.palavras_de_parada)
        valido, acao, objeto, local = validar_comando(comando, self.acoes)

        self.assertTrue(valido, f"Comando não validado: '{transcricao}' do arquivo {caminho_audio}")
        self.assertEqual(acao, acao_esperada, f"Ação errada. Esperava '{acao_esperada}', reconheceu '{acao}'.")

    # ----- BATERIA DE TESTES -----

    def testar_02_abrir_galinheiro(self):
        self.auxiliar_testar_comando(AUDIO_ABRIR, "abrir")

    def testar_03_alimentar_porcos(self):
        self.auxiliar_testar_comando(AUDIO_ALIMENTAR_PORCOS, "alimentar")

    def testar_04_alimentar_vacas(self):
        self.auxiliar_testar_comando(AUDIO_ALIMENTAR_VACAS, "alimentar")

    def testar_05_plantar_batata(self):
        self.auxiliar_testar_comando(AUDIO_PLANTAR, "plantar")

    def testar_06_regar_campo(self):
        self.auxiliar_testar_comando(AUDIO_REGAR_CAMPO, "regar")

    def testar_07_regar_estufa(self):
        self.auxiliar_testar_comando(AUDIO_REGAR_ESTUFA, "regar")

if __name__ == "__main__":
    unittest.main()