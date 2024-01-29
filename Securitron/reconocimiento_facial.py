from pathlib import Path
import cv2
import face_recognition as fr
from PIL import Image as im
import os

dir = Path("images")


# COMPROBAR SI EL USUARIO ESTÁ REGISTRADO Y DARLE LA BIENVENIDA
def check_user(name):
    fotos = cargar_imagenes(name)
    fotos = asignar_perfil_color(fotos)
    face2check = recognize_user()
    face2check = asignar_perfil_color(face2check)
    facial_code = get_cod_faces(fotos)
    same_person = compare_all_with_control(facial_code, face2check)

    if same_person:
        print('bienvenido, ' + name)
    else:
        print('quieto ahí, no tengo idea de quién eres. Abandona mi zona antes de que te fría con un rayo láser')


# TOMAR UNA CAPTURA DEL ROSTRO PARA IDENTIFICAR AL USUARIO
def recognize_user():
    print('A ver, mírame bien')
    captura = cv2.VideoCapture(0)

    while (True):
        ok, frame = captura.read()
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    captura.release()
    cv2.destroyAllWindows()

    if not ok:
        print('¡No puedor, no puedor!')
    else:
        return fr.face_encodings(frame)


# TOMAR UNA CAPTURA DEL ROSTRO PARA REGISTRAR AL USUARIO
def register_user(name):
    print('A ver, mírame bien')
    captura = cv2.VideoCapture(0)

    while (True):
        ok, frame = captura.read()
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    captura.release()
    cv2.destroyAllWindows()

    if not ok:
        print('¡No puedor, no puedor!')
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
            fotos.append(fr.load_image_file(dir, pic))
    return fotos


def asignar_perfil_color(fotos_list):
    for i in range(len(fotos_list)):
        fotos_list[i] = cv2.cvtColor(fotos_list[i], cv2.COLOR_BGR2RGB)
    return fotos_list


# top, right, botton, left
def localizar_cara(fotos_list):
    locations = []
    for i in fotos_list:
        locations.append(fr.face_locations(i)[0])  # puede detectar más caras... nos quedamos con la primera
    return locations


def get_cod_faces(fotos_list):
    cod_faces = []
    for i in fotos_list:
        cod_faces.append(fr.face_encodings(i)[0])
    return cod_faces


def show_imgs(fotos_list):
    for index, f in enumerate(fotos_list):
        cv2.imshow(f'Foto {index}', f)


# Por defecto, el valor de la distancia para determinar si es true o false es 0.6
def compare_all_with_control(cara_cod_list, face2check):
    control = False
    for i, fc in enumerate(cara_cod_list):
        control = fr.compare_faces(face2check, fc)
    return control
