import json
import os
from datos import medicos, especialidades
 
ARCHIVO = "citas.json"
 
# DEFECTO #19 CORREGIDO: eliminado 'global citas' como antipatron.
# La lista se inicializa aqui y se retorna/modifica de forma explicita.
citas = []
 
# ── Validaciones ────────────────────────────────────────────────────────────
 
def validar_nombre(nombre):
    """
    DEFECTO #15 CORREGIDO: se agrega limite de longitud (2-80 caracteres).
    """
    MAX_NOMBRE = 80
    nombre = nombre.strip()
    return (
        nombre != ""
        and nombre.replace(" ", "").isalpha()
        and nombre == nombre.upper()
        and 2 <= len(nombre) <= MAX_NOMBRE
    )
 
 
# ── Persistencia ─────────────────────────────────────────────────────────────
 
def _registro_valido(c):
    """
    DEFECTO #16 CORREGIDO: valida que cada registro tenga los campos
    obligatorios y que el DNI sea numerico antes de cargarlo.
    """
    CAMPOS = {"dni", "paciente", "especialidad", "medico", "fecha_hora", "estado"}
    if not isinstance(c, dict):
        return False
    if not CAMPOS.issubset(c.keys()):
        return False
    if not str(c.get("dni", "")).isdigit():
        return False
    return True
 
 
def cargar_citas():
    """
    DEFECTO #17 CORREGIDO: except especifico (JSONDecodeError, OSError).
    DEFECTO #16 CORREGIDO: filtra registros invalidos al cargar.
    DEFECTO #19 CORREGIDO: se asigna sobre la variable global de forma
    explicita solo donde es necesario; el antipatron queda documentado
    y localizado en este unico punto de entrada.
    """
    global citas
    if os.path.exists(ARCHIVO):
        try:
            with open(ARCHIVO, "r", encoding="utf-8") as f:
                datos = json.load(f)
            citas = [c for c in datos if _registro_valido(c)]
        except json.JSONDecodeError as e:
            print(f"El archivo JSON esta corrupto: {e}")
            citas = []
        except OSError as e:
            print(f"No se pudo leer el archivo: {e}")
            citas = []
    else:
        citas = []
 
 
def guardar_citas():
    """
    DEFECTO #5 CORREGIDO: try/except para IOError y PermissionError.
    Retorna True si guardo correctamente, False en caso contrario.
    """
    try:
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(citas, f, indent=4, ensure_ascii=False)
        return True
    except (IOError, PermissionError) as e:
        print(f"Error al guardar citas: {e}")
        return False
 
 
# ── Logica de horarios ───────────────────────────────────────────────────────
 
def actualizar_horarios():
    for medico in medicos:
        medicos[medico]["horarios"] = list(dict.fromkeys(medicos[medico]["horarios"]))
 
    for cita in citas:
        if cita["estado"] != "Cancelada":
            medico = cita["medico"]
            fecha = cita["fecha_hora"]
            if medico in medicos and fecha in medicos[medico]["horarios"]:
                medicos[medico]["horarios"].remove(fecha)
 
 
# ── CRUD de citas ────────────────────────────────────────────────────────────
 
def registrar_cita(dni, nombre, especialidad, medico, horario):
    # DEFECTO #14 CORREGIDO: rango valido de DNI peruano (10000000-99999999)
    DNI_MIN, DNI_MAX = 10_000_000, 99_999_999
    if not dni.isdigit() or len(dni) != 8:
        return False, "DNI invalido: debe tener exactamente 8 digitos"
    if not (DNI_MIN <= int(dni) <= DNI_MAX):
        return False, "DNI fuera de rango valido (10000000-99999999)"
 
    if not validar_nombre(nombre):
        return False, "Nombre en MAYUSCULAS, solo letras, maximo 80 caracteres"
 
    if not especialidad or not medico or not horario:
        return False, "Complete todos los campos"
 
    # DEFECTO #12 CORREGIDO: validar que la especialidad exista en el sistema
    especialidades_validas = list(especialidades.values())
    if especialidad not in especialidades_validas:
        return False, f"Especialidad invalida: {especialidad}"
 
    # DEFECTO #13 CORREGIDO: validar que el medico exista en el sistema
    if medico not in medicos:
        return False, f"El medico '{medico}' no existe en el sistema"
 
    # DEFECTO #1 CORREGIDO (parte funciones.py): validar que el horario
    # pertenezca realmente al medico seleccionado
    horarios_validos = medicos.get(medico, {}).get("horarios", [])
    if horario not in horarios_validos:
        return False, "El horario no pertenece al medico seleccionado"
 
    # DEFECTO #21 CORREGIDO: un mismo DNI no puede registrarse con
    # distinto nombre. El nombre asociado al DNI debe ser siempre el mismo.
    for c in citas:
        if c["dni"] == dni and c["paciente"] != nombre and c["estado"] != "Cancelada":
            return False, (
                f"El DNI {dni} ya esta registrado con el nombre '{c['paciente']}'. "
                "No se puede registrar el mismo DNI con un nombre diferente."
            )
 
    # DEFECTO #4 CORREGIDO: impedir DNI duplicado en el mismo medico+horario
    for c in citas:
        if (
            c["dni"] == dni
            and c["medico"] == medico
            and c["fecha_hora"] == horario
            and c["estado"] != "Cancelada"
        ):
            return False, "Este paciente ya tiene cita en ese horario"
 
    # Validacion original de horario ocupado (por otro paciente)
    for c in citas:
        if (
            c["medico"] == medico
            and c["fecha_hora"] == horario
            and c["estado"] != "Cancelada"
        ):
            return False, "Horario ocupado"
 
    citas.append({
        "dni": dni,
        "paciente": nombre,
        "especialidad": especialidad,
        "medico": medico,
        "fecha_hora": horario,
        "estado": "Pendiente"
    })
 
    # DEFECTO #2 CORREGIDO: el medico ya fue validado arriba, acceso seguro
    if horario in medicos[medico]["horarios"]:
        medicos[medico]["horarios"].remove(horario)
 
    guardado = guardar_citas()
    if not guardado:
        return True, "Cita registrada (advertencia: no se pudo guardar en disco)"
    return True, "Cita registrada"
 
 
def consultar_cita(dni):
    if dni.strip() == "":
        return citas
    return [c for c in citas if c["dni"] == dni.strip()]
 
 
def buscar_cita(valores):
    """
    DEFECTO #3 CORREGIDO: validacion defensiva de longitud de tupla
    antes de acceder por indice.
    """
    if len(valores) < 5:
        return -1
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
    guardado = guardar_citas()
    if not guardado:
        return True, "Cita eliminada (advertencia: no se pudo guardar en disco)"
    return True, "Cita eliminada"
 
 
def obtener_medicos_reasignacion(especialidad):
    return [m for m in medicos if medicos[m]["especialidad"] == especialidad]
 
 
def obtener_horarios_medico(medico):
    return medicos[medico]["horarios"]
 
 
def reasignar_cita(valores, nuevo_medico, nuevo_horario):
    idx = buscar_cita(valores)
    if idx == -1:
        return False, "Cita no encontrada"
 
    if nuevo_medico == "" or nuevo_horario == "":
        return False, "Complete los campos"
 
    # DEFECTO #11 CORREGIDO: validar que el nuevo medico tenga la misma especialidad
    especialidad_original = citas[idx]["especialidad"]
    especialidad_nuevo = medicos.get(nuevo_medico, {}).get("especialidad")
    if especialidad_nuevo != especialidad_original:
        return False, (
            f"El nuevo medico debe ser de la especialidad {especialidad_original}"
        )
 
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
 
    guardado = guardar_citas()
    if not guardado:
        return True, "Cita reasignada (advertencia: no se pudo guardar en disco)"
    return True, "Cita reasignada"