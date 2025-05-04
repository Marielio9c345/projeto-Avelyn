# voz.py — Entrada de voz integrada
import sounddevice as sd
import scipy.io.wavfile
import tempfile
import whisper
import os

def capturar_audio_e_transcrever(duracao=5):
    fs = 44100
    gravacao = sd.rec(int(duracao * fs), samplerate=fs, channels=1)
    sd.wait()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        caminho_audio = tmpfile.name
        scipy.io.wavfile.write(caminho_audio, fs, gravacao)

    modelo = whisper.load_model("base")
    resultado = modelo.transcribe(caminho_audio)
    os.remove(caminho_audio)
    return resultado["text"]
