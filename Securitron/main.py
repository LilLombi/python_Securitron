
from pathlib import Path
from reconocimiento_facial import *

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    count_equals("daniel")
=======
from User import User
from rec_voz import record_voice, transcribe_audio_to_text, speak_text
from reconocimiento_facial import get_photo, check_user


def get_user_data():
    # Grabar y transcribir el nombre
    name_audio = record_voice("Por favor, di tu nombre:")
    name = transcribe_audio_to_text(name_audio)

    # Grabar y transcribir el apellido
    surname_audio = record_voice("Por favor, di tu apellido:")
    surname = transcribe_audio_to_text(surname_audio)

    # Grabar y transcribir la edad
    age_audio = record_voice("Por favor, di tu edad:")
    age = transcribe_audio_to_text(age_audio)

    return name, surname, age


def main():
    # Obtener datos del usuario por voz
    name, surname, age = get_user_data()
    if not all([name, surname, age]):
        print("No se pudieron capturar correctamente los datos del usuario.")
        return

    # Crear instancia de usuario
    user = User(name, surname, age)

    # Tomar foto del usuario
    print(f"Hola {user.name}, por favor mira a la cámara para tomar una foto.")
    speak_text(f"Hola {user.name}, por favor mira a la cámara para tomar una foto.")
    filename = get_photo(f"{user.name}_{user.surname}")

    # Verificar si el usuario está registrado y si coincide con la persona en la foto
    user_exists, user_matched = check_user(user.name)

    if user_exists and user_matched:
        print(f"Bienvenido de nuevo, {user.name}!")
        speak_text(f"Bienvenido de nuevo, {user.name}!")
    elif user_exists and not user_matched:
        print(f"Usuario {user.name} detectado pero la persona en la foto no coincide.")
        speak_text(f"Usuario {user.name} detectado pero la persona en la foto no coincide.")
    else:
        print(f"Usuario {user.name} registrado con éxito.")
        speak_text(f"Usuario {user.name} registrado con éxito.")


if __name__ == "__main__":
    main()
