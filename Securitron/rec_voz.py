import os
import sys
from gtts import gTTS
from io import BytesIO
from pygame import mixer
import tempfile
import openai
import requests
import speech_recognition as sr
import pyttsx3

openai.api_key = "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"

# Guardar referencia al stderr original
stderr_original = sys.stderr

# Redirigir stderr a /dev/null
with open(os.devnull, 'w') as fnull:
    sys.stderr = fnull

    # Restaurar stderr al valor original después de que las bibliotecas hayan sido importadas
    sys.stderr = stderr_original

# Inicializa el motor TTS
engine = pyttsx3.init()

# Obtener y configurar la voz en español si está disponible
voices = engine.getProperty('voices')
spanish_voice_id = None
for voice in voices:
    # Aquí se busca 'es' en el identificador de idioma de la voz
    if 'es' in voice.languages:
        spanish_voice_id = voice.id
        break

def transcribe_audio_to_text(filename):
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

def record_voice(prompt, file_name="input.wav", timeout=10):
    """
    Grabar la voz del usuario y guardarla en un archivo.
    :param prompt: Texto que se le indica al usuario antes de grabar.
    :param file_name: Nombre del archivo donde se guardará la grabación.
    :param timeout: Tiempo máximo de grabación en segundos.
    :return: Nombre del archivo de audio grabado.
    """
    speak_text(prompt)
    with sr.Microphone(device_index=13) as source:
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print(prompt)
        audio = recognizer.listen(source, phrase_time_limit=timeout)
        with open(file_name, "wb") as f:
            f.write(audio.get_wav_data())
    return file_name



def speak_text(text, lang='es'):
    try:
        # Crear un objeto gTTS para el texto y el idioma especificado (español por defecto)
        tts = gTTS(text, lang=lang)

        # Guardar el audio en un buffer
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        # Cargar y reproducir el audio
        mixer.init()
        mixer.music.load(fp)
        mixer.music.play()

        # Esperar a que termine la reproducción del audio
        while mixer.music.get_busy():
            continue
    except Exception as e:
        print(f"Error al usar gTTS: {e}")


def main():
    saludo_inicial_realizado = False  # Variable de control para el saludo inicial
    while True:
        with sr.Microphone(device_index=13) as source:
            recognizer = sr.Recognizer()
            recognizer.adjust_for_ambient_noise(source, duration=1)

            if not saludo_inicial_realizado:
                # Espera a que el usuario diga "Hola"
                engine.say("Di 'Hola' para empezar a grabar")
                engine.runAndWait()
                audio = recognizer.listen(source, phrase_time_limit=None, timeout=5)  # 5 segundos de espera máxima
                try:
                    transcription = recognizer.recognize_google(audio, language="es")
                    print(
                        f"Transcripción inicial: {transcription}")  # Imprime lo que se entendió después de decir "Hola"
                    if "hola" in transcription.lower():
                        saludo_inicial_realizado = True  # Establece la variable a True después de reconocer "Hola"
                    else:
                        continue  # Si no se dice "Hola", vuelve a intentar
                except sr.WaitTimeoutError:
                    print("No se detectó audio en el tiempo de espera establecido. Vuelve a intentar.")
                    continue  # Si hay un timeout, vuelve a intentar
                except Exception as e:
                    print(f"Error en el reconocimiento de voz: {e}")
                    continue  # Si hay un error, vuelve a intentar

            # Proceso de grabación y respuesta después de decir "Hola"
            print("Dime qué quieres")
            recognizer.pause_threshold = 1.0
            audio = recognizer.listen(source, phrase_time_limit=10,
                                      timeout=5)  # 10 segundos de grabación máxima, 5 segundos de espera máxima
            with open("input.wav", "wb") as f:
                f.write(audio.get_wav_data())
            # Transcribe el audio
            text = transcribe_audio_to_text("input.wav")
            print(f"Transcripción de lo que el usuario quiere: {text}")  # Imprime la transcripción del audio grabado
            if text:
                print(f"Usuario: {text}")
                # Genera la respuesta
                response = generate_response(text)
                print(f"Bot: {response}")
                # Lee la respuesta utilizando TTS
                speak_text(response)


if __name__ == "__main__":
    main()
