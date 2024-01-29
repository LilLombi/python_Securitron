from pathlib import Path
import cv2
import face_recognition as fr
import numpy as np
from PIL import Image as im
import os
from rec_voz import speak_text

dir = Path("images")


# COMPROBAR SI EL USUARIO ESTÁ REGISTRADO Y DARLE LA BIENVENIDA
def check_user(name):
    fotos = cargar_imagenes(name)
    fotos = asignar_perfil_color(fotos)
    facial_codes = get_cod_faces(fotos)

    # Obtener la codificación facial del usuario a verificar
    face2check = recognize_user()
    face2check = asignar_perfil_color(face2check)
    face2check_codes = get_cod_faces(face2check)

    # Comparar las codificaciones faciales del usuario con las codificaciones conocidas
    results = compare_all_with_control(facial_codes, face2check_codes)

    # Decidir si el usuario coincide
    user_matched = any(result['matches'] for result in results)

    if user_matched:
        v = f'Bienvenido, {name}'
        speak_text(v, 'es')
    else:
        v = 'Quieto ahí, no tengo idea de quién eres. Abandona mi zona antes de que te fría con un rayo láser'
        speak_text(v, 'es')


# TOMAR UNA CAPTURA DEL ROSTRO PARA IDENTIFICAR AL USUARIO
def recognize_user():
    v = 'A ver, mírame bien'
    speak_text(v, 'es')
    captura = cv2.VideoCapture(0)

    while (True):
        ok, frame = captura.read()
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    captura.release()
    cv2.destroyAllWindows()

    if not ok:
        v = '¡No puedor, no puedor!'
        speak_text(v, 'es')
    else:
        return fr.face_encodings(frame)


# TOMAR UNA CAPTURA DEL ROSTRO PARA REGISTRAR AL USUARIO
def register_user(name):
    v = 'A ver, mírame bien'
    speak_text(v, 'es')
    captura = cv2.VideoCapture(0)

    while (True):
        ok, frame = captura.read()
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    captura.release()
    cv2.destroyAllWindows()

    if not ok:
        v = '¡No puedor, no puedor!'
        speak_text(v, 'es')
    else:
        cv2.imshow('frame', frame)
        data = im.fromarray(frame)
        num = count_equals(name)
        ectory = name + str(num) + ".png"
        data.save(Path(dir, ectory))

        return ectory


def count_equals(name):
    counter = 0
    for pic in os.listdir(dir):
        if pic.__contains__(name):
            counter += 1
    return counter


def cargar_imagenes(name):
    fotos = []
    for pic in os.listdir(dir):
        if pic.__contains__(name):
            file_path = os.path.join(dir, pic)
            # Cargar la imagen y asegurarse de que esté en formato uint8
            foto = fr.load_image_file(file_path)
            if foto.dtype != np.uint8:
                v = f"Tipo de datos inesperado {foto.dtype} en la imagen {file_path}, convirtiendo a uint8."
                speak_text(v, 'es')
                foto = (foto * 255).astype('uint8')
            fotos.append(foto)
    return fotos


def asignar_perfil_color(fotos_list):
    fotos_procesadas = []
    for foto in fotos_list:
        # Verificar el tipo de datos de la imagen y convertir si es necesario
        if foto.dtype == 'float64':
            foto = (foto * 255).astype('uint8')

        # Convertir la imagen de BGR a RGB
        foto_rgb = cv2.cvtColor(foto, cv2.COLOR_BGR2RGB)
        fotos_procesadas.append(foto_rgb)

    return fotos_procesadas


# top, right, botton, left
def localizar_cara(fotos_list):
    locations = []
    for i in fotos_list:
        locations.append(fr.face_locations(i)[0])  # puede detectar más caras... nos quedamos con la primera
    return locations


def get_cod_faces(fotos_list):
    cod_faces = []
    for i in fotos_list:
        encodings = fr.face_encodings(i)
        if encodings:
            cod_faces.append(encodings[0])
        else:
            print("No se encontraron rostros en una de las imágenes.")
    return cod_faces


def show_imgs(fotos_list):
    for index, f in enumerate(fotos_list):
        cv2.imshow(f'Foto {index}', f)


# Por defecto, el valor de la distancia para determinar si es true o false es 0.6
def compare_all_with_control(known_face_encodings, face_encoding_to_check):
    # Asegurarse de que face_encoding_to_check sea una lista de arrays de NumPy
    if not all(isinstance(encoding, np.ndarray) for encoding in face_encoding_to_check):
        print("face_encoding_to_check no contiene arrays de NumPy.")
        return False

    # Asegurarse de que cada encoding en face_encoding_to_check tenga las dimensiones correctas
    if not all(encoding.ndim == 1 and encoding.shape[0] == 128 for encoding in face_encoding_to_check):
        print("Uno o más codificaciones faciales a comparar tienen dimensiones incorrectas.")
        return False

    # Asegurarse de que known_face_encodings sea una lista de arrays de NumPy
    if not all(isinstance(encoding, np.ndarray) for encoding in known_face_encodings):
        print("known_face_encodings no contiene arrays de NumPy.")
        return False

    # Asegurarse de que cada encoding en known_face_encodings tenga las dimensiones correctas
    if not all(encoding.ndim == 1 and encoding.shape[0] == 128 for encoding in known_face_encodings):
        print("Uno o más codificaciones faciales conocidas tienen dimensiones incorrectas.")
        return False

    # Realizar la comparación con fr.compare_faces
    # Nota: Suponiendo que face_encoding_to_check es una lista de codificaciones faciales de la nueva cara
    results = []
    for new_encoding in face_encoding_to_check:
        # Compara la nueva cara con todas las caras conocidas
        matches = fr.compare_faces(known_face_encodings, new_encoding)
        distance = fr.face_distance(known_face_encodings, new_encoding)

        # Consideramos que la cara coincide si al menos una de las caras conocidas coincide
        results.append({'matches': matches, 'distance': distance})

    return results