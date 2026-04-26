from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torchaudio
import torch

MODELO = "lgris/wav2vec2-large-xlsr-open-brazilian-portuguese-v2"

AUDIOS = [
    "./audios/desligar lampada.wav", 
    "./audios/ligar lampada.wav"
]

TAXA_AMOSTRAGEM = 16_000

# CORREÇÃO: Mudar o valor por defeito de "gpu" para "cuda"
def iniciar(identificador_modelo, dispositivo = "cuda"):
    iniciado, processador, modelo = False, None, None

    try:
        processador = Wav2Vec2Processor.from_pretrained(identificador_modelo)
        modelo = Wav2Vec2ForCTC.from_pretrained(identificador_modelo).to(dispositivo)

        iniciado = True
    except Exception as e:
        print(f"erro inicializando o modelo: {e}")

    return iniciado, processador, modelo

def carregar_fala(audio_fala):
    audio, amostragem = torchaudio.load(audio_fala)
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim = 0, keepdim= True)

    adaptador_amostragem = torchaudio.transforms.Resample(amostragem, TAXA_AMOSTRAGEM)
    audio = adaptador_amostragem(audio)

    return audio.squeeze()

def transcrever(dispositivo, fala, modelo, processador):
   saida = processador(fala, return_tensors="pt", sampling_rate=TAXA_AMOSTRAGEM).input_values.to(dispositivo)
   saida = modelo(saida).logits

   predicao = torch.argmax(saida, dim=-1)
   transcricao = processador.batch_decode(predicao)[0]

   return transcricao.lower()

if __name__ == "__main__":
    iniciado, processador, modelo = iniciar(MODELO)
    if iniciado:
        dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
        print("modelo iniciado com sucesso")
        
        for audio in AUDIOS:
            fala = carregar_fala(audio)
            transcricao = transcrever(dispositivo, fala, modelo, processador)
            print(f"transcrição do audio {audio}: {transcricao}")

        # CORREÇÃO: O segundo ciclo 'for' que estava aqui foi removido porque era redundante e não fazia nada.