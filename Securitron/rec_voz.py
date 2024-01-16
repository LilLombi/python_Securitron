import openai
import speech_recognition as sr
import pyttsx3
import time

# Imprime la lista de dispositivos de entrada disponibles
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"Device {index}: {name}")

# Inicializa el motor TTS
engine = pyttsx3.init()

# Abre el archivo en modo lectura
with open('clave_api.txt', 'r') as file:
    # Lee la clave API desde el archivo
    clave_api = file.read().strip()

# Asigna la clave API a openai.api_key
openai.api_key = clave_api

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
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=4000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response["choices"][0]["text"]

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
        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_google(audio, language="es")
                if transcription.lower() == "hola":
                    # Graba audio
                    filename = "input.wav"
                    print("Dime qué quieres")
                    with sr.Microphone() as source:
                        recognizer = sr.Recognizer()
                        source.pause_threshold = 1
                        audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
                        with open(filename, "wb") as f:
                            f.write(audio.get_wav_data())
                    # Transcribe el audio
                    text = transcribe_audio_to_test(filename)
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
