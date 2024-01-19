import os
import sys

import openai
import requests

openai.api_key = "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"
import speech_recognition as sr
import pyttsx3

# Configura la clave API de OpenAI

# Guardar referencia al stderr original
stderr_original = sys.stderr

# Redirigir stderr a /dev/null
with open(os.devnull, 'w') as fnull:
    sys.stderr = fnull
    # Importar las bibliotecas que causan los mensajes de ALSA

    # Restaurar stderr al valor original después de que las bibliotecas hayan sido importadas
    sys.stderr = stderr_original

# Inicializa el motor TTS
engine = pyttsx3.init()

def transcribe_audio_to_test(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language="es")
    except Exception as e:
        print(f"Error en la transcripción: {e}")
        return None


def generate_response(prompt):
    try:
        # Define el endpoint para el modelo de chat
        chat_endpoint = "https://api.openai.com/v1/chat/completions"

        # Define los datos de la petición
        data = {
            "model": "gpt-3.5-turbo",  # Asegúrate de usar el modelo correcto
            "messages": [
                {"role": "system", "content": "Tu mensaje de sistema inicial, si es necesario"},
                {"role": "user", "content": prompt}
            ]
        }

        # Define los encabezados, incluyendo tu API key
        headers = {
            "Authorization": f"Bearer {openai.api_key}",
            "Content-Type": "application/json",
        }

        # Realiza la petición POST
        response = requests.post(chat_endpoint, headers=headers, json=data)

        # Verifica la respuesta y devuelve el texto de la respuesta
        if response.status_code == 200:
            response_data = response.json()
            # Asegúrate de obtener la parte de la respuesta que necesitas
            return response_data['choices'][0]['message']['content']
        else:
            print(f"Error en la petición HTTP: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error al generar la respuesta: {e}")
        return None


voices = engine.getProperty('voices')
spanish_voice = None
for voice in voices:
    if "spanish" in voice.languages:
        spanish_voice = voice.id
if spanish_voice is not None:
    engine.setProperty('voice', spanish_voice)


def speak_text(text):
    engine.say(text)
    engine.runAndWait()


def main():
    while True:
        # Espera a que el usuario diga "Hola"
        print("Di 'Hola' para empezar a grabar")
        with sr.Microphone(device_index=13) as source:  # Usando el dispositivo con índice 13
            recognizer = sr.Recognizer()
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_google(audio, language="es")
                print(f"Transcripción inicial: {transcription}")  # Imprime lo que se entendió después de decir "Hola"
                if "hola" in transcription.lower():
                    # Graba audio
                    filename = "input.wav"
                    print("Dime qué quieres")
                    with sr.Microphone(device_index=13) as source:  # Asegurándose de usar el dispositivo con índice 13
                        recognizer = sr.Recognizer()
                        recognizer.adjust_for_ambient_noise(source)
                        source.pause_threshold = 1
                        audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
                        with open(filename, "wb") as f:
                            f.write(audio.get_wav_data())
                    # Transcribe el audio
                    text = transcribe_audio_to_test(filename)
                    print(
                        f"Transcripción de lo que el usuario quiere: {text}")  # Imprime la transcripción del audio grabado
                    if text:
                        print(f"Usuario: {text}")

                        # Genera la respuesta
                        response = generate_response(text)
                        print(f"Bot: {response}")

                        # Lee la respuesta utilizando GPT-3
                        speak_text(response)
            except Exception as e:
                print(f"Error en el reconocimiento de voz: {e}")


if __name__ == "__main__":
    main()
