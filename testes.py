import unittest
from assistente import *

COMANDO_LIGAR_LAMPADA = "Asistente-Virtual\assistente virtual\audios\ligar lampada.wav"
COMANDO_DESLIGAR_LAMPADA = "Asistente-Virtual\assistente virtual\audios\desligar lampada.wav"

class TestesLampada(unittest.TestCase):
    @classmethod

    def setUpClass(cls):
        cls.dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"

        cls.iniciado, cls.processador, cls.modelo, cls.palavras_de_parada, cls.acoes = iniciar_assistente(cls.dispositivo)

        return super().setUpClass()
    
    def testar_01_assistente_iniciado(self):
        self.assertTrue(self.iniciado)
    
    def testar_02_ligar_lampada(self):
        fala = carregar_fala(COMANDO_LIGAR_LAMPADA)
        self.assertIsNotNone(fala)

        comando = transcrever(self.dispositivo, fala, self.modelo, self.processador)
        self.assertIsNotNone(comando)

        valido, _, _, _, validar_comando(comando, self.acoes)

        self.assertTrue(valido)
unittest.main()