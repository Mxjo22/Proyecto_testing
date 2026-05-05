import json
import os
from datos import medicos

ARCHIVO = "citas.json"
citas = []


def validar_nombre(nombre):
    nombre = nombre.strip()
    return nombre != "" and nombre.replace(" ", "").isalpha() and nombre == nombre.upper()


def cargar_citas():
    global citas

    if os.path.exists(ARCHIVO):
        try:
            with open(ARCHIVO, "r", encoding="utf-8") as f:
                citas = json.load(f)
        except:
            citas = []
    else:
        citas = []


def guardar_citas():
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(citas, f, indent=4, ensure_ascii=False)


def actualizar_horarios():
    for medico in medicos:
        medicos[medico]["horarios"] = list(dict.fromkeys(medicos[medico]["horarios"]))

    for cita in citas:
        if cita["estado"] != "Cancelada":
            medico = cita["medico"]
            fecha = cita["fecha_hora"]

            if medico in medicos and fecha in medicos[medico]["horarios"]:
                medicos[medico]["horarios"].remove(fecha)


def registrar_cita(dni, nombre, especialidad, medico, horario):
    if not dni.isdigit() or len(dni) != 8:
        return False, "DNI inválido"

    if not validar_nombre(nombre):
        return False, "Nombre en MAYÚSCULAS y solo letras"

    if not especialidad or not medico or not horario:
        return False, "Complete todos los campos"

    for c in citas:
        if c["medico"] == medico and c["fecha_hora"] == horario and c["estado"] != "Cancelada":
            return False, "Horario ocupado"

    citas.append({
        "dni": dni,
        "paciente": nombre,
        "especialidad": especialidad,
        "medico": medico,
        "fecha_hora": horario,
        "estado": "Pendiente"
    })

    if horario in medicos[medico]["horarios"]:
        medicos[medico]["horarios"].remove(horario)

    guardar_citas()
    return True, "Cita registrada"


def consultar_cita(dni):
    if dni.strip() == "":
        return citas

    return [c for c in citas if c["dni"] == dni.strip()]


def buscar_cita(valores):
    for i, c in enumerate(citas):
        if (
            c["dni"] == valores[0]
            and c["paciente"] == valores[1]
            and c["medico"] == valores[3]
            and c["fecha_hora"] == valores[4]
        ):
            return i

    return -1


def cancelar_cita(valores):
    idx = buscar_cita(valores)

    if idx == -1:
        return False, "Cita no encontrada"

    medico = citas[idx]["medico"]
    horario = citas[idx]["fecha_hora"]

    if horario not in medicos[medico]["horarios"]:
        medicos[medico]["horarios"].append(horario)

    del citas[idx]

    guardar_citas()

    return True, "Cita eliminada"


def obtener_medicos_reasignacion(especialidad):
    return [
        m for m in medicos
        if medicos[m]["especialidad"] == especialidad
    ]


def obtener_horarios_medico(medico):
    return medicos[medico]["horarios"]


def reasignar_cita(valores, nuevo_medico, nuevo_horario):
    idx = buscar_cita(valores)

    if idx == -1:
        return False, "Cita no encontrada"

    if nuevo_medico == "" or nuevo_horario == "":
        return False, "Complete los campos"

    viejo_medico = citas[idx]["medico"]
    viejo_horario = citas[idx]["fecha_hora"]

    if nuevo_horario not in medicos[nuevo_medico]["horarios"]:
        return False, "Horario no disponible"

    if viejo_horario not in medicos[viejo_medico]["horarios"]:
        medicos[viejo_medico]["horarios"].append(viejo_horario)

    medicos[nuevo_medico]["horarios"].remove(nuevo_horario)

    citas[idx]["medico"] = nuevo_medico
    citas[idx]["fecha_hora"] = nuevo_horario
    citas[idx]["estado"] = "Reasignada"

    guardar_citas()

    return True, "Cita reasignada"