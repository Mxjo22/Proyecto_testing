import tkinter as tk
from tkinter import ttk, messagebox
 
from datos import especialidades, medicos
from funciones import (
    cargar_citas,
    actualizar_horarios,
    registrar_cita,
    consultar_cita,
    cancelar_cita,
    reasignar_cita,
    obtener_medicos_reasignacion,
    obtener_horarios_medico
)
 
 
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Citas Medicas")
        self.root.geometry("980x560")
        self.root.configure(bg="#f5fbff")
 
        cargar_citas()
        actualizar_horarios()
 
        self.ui()
 
    # ── Construccion de la interfaz ──────────────────────────────────────────
 
    def ui(self):
        tk.Label(
            self.root,
            text="SISTEMA DE CITAS MEDICAS",
            bg="#f5fbff",
            fg="#1787c8",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=10)
 
        form = tk.Frame(self.root, bg="#f5fbff")
        form.pack(pady=6)
 
        tk.Label(form, text="DNI", bg="#f5fbff").grid(row=0, column=0)
        tk.Label(form, text="NOMBRE", bg="#f5fbff").grid(row=0, column=1)
        tk.Label(form, text="ESPECIALIDAD", bg="#f5fbff").grid(row=0, column=2)
        tk.Label(form, text="MEDICO", bg="#f5fbff").grid(row=0, column=3)
        tk.Label(form, text="HORARIO", bg="#f5fbff").grid(row=0, column=4)
 
        self.entry_dni = tk.Entry(form, width=14)
        self.entry_dni.grid(row=1, column=0, padx=4)
 
        self.entry_nombre = tk.Entry(form, width=22)
        self.entry_nombre.grid(row=1, column=1, padx=4)
 
        self.combo_esp = ttk.Combobox(
            form,
            values=list(especialidades.values()),
            width=18,
            state="readonly"
        )
        self.combo_esp.grid(row=1, column=2, padx=4)
        self.combo_esp.bind("<<ComboboxSelected>>", self.cargar_medicos)
 
        self.combo_med = ttk.Combobox(form, width=16, state="readonly")
        self.combo_med.grid(row=1, column=3, padx=4)
        self.combo_med.bind("<<ComboboxSelected>>", self.cargar_horarios)
 
        self.combo_hor = ttk.Combobox(form, width=18, state="readonly")
        self.combo_hor.grid(row=1, column=4, padx=4)
 
        tk.Button(
            form,
            text="Registrar cita",
            bg="#28a8e0",
            fg="white",
            relief="flat",
            command=self.registrar
        ).grid(row=1, column=5, padx=8)
 
        acciones = tk.Frame(self.root, bg="#f5fbff")
        acciones.pack(pady=8)
 
        tk.Label(acciones, text="Consultar por DNI:", bg="#f5fbff").pack(side="left")
 
        self.entry_buscar = tk.Entry(acciones, width=16)
        self.entry_buscar.pack(side="left", padx=4)
 
        tk.Button(
            acciones, text="Consultar", bg="#28a8e0", fg="white", relief="flat",
            command=self.consultar
        ).pack(side="left", padx=3)
 
        tk.Button(
            acciones, text="Listar agenda", bg="#28a8e0", fg="white", relief="flat",
            command=self.listar
        ).pack(side="left", padx=3)
 
        tk.Button(
            acciones, text="Ocultar", bg="#28a8e0", fg="white", relief="flat",
            command=self.ocultar
        ).pack(side="left", padx=3)
 
        tk.Button(
            acciones, text="Cancelar cita", bg="#28a8e0", fg="white", relief="flat",
            command=self.cancelar
        ).pack(side="left", padx=3)
 
        tk.Button(
            acciones, text="Reasignar", bg="#28a8e0", fg="white", relief="flat",
            command=self.reasignar
        ).pack(side="left", padx=3)
 
        columnas = ("dni", "paciente", "especialidad", "medico", "fecha", "estado")
 
        self.tabla = ttk.Treeview(
            self.root,
            columns=columnas,
            show="headings",
            height=16,
            selectmode="extended"   # permite seleccion multiple
        )
 
        self.tabla.heading("dni", text="DNI")
        self.tabla.heading("paciente", text="PACIENTE")
        self.tabla.heading("especialidad", text="ESPECIALIDAD")
        self.tabla.heading("medico", text="MEDICO")
        self.tabla.heading("fecha", text="FECHA")
        self.tabla.heading("estado", text="ESTADO")
 
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)
 
    # ── Callbacks de combos ──────────────────────────────────────────────────
 
    def cargar_medicos(self, _ = None):
        """
        DEFECTO #18 CORREGIDO: parametro 'e' renombrado a '_' para indicar
        que es requerido por el callback de Tkinter pero no se usa internamente.
        """
        esp = self.combo_esp.get()
        lista = [m for m in medicos if medicos[m]["especialidad"] == esp]
        self.combo_med["values"] = lista
        self.combo_med.set("")
        # DEFECTO #1 CORREGIDO (parte interfaz): limpiar combo de horario
        # al cambiar de medico para evitar horarios de otro medico.
        self.combo_hor.set("")
        self.combo_hor["values"] = []
 
    def cargar_horarios(self, _ = None):
        """
        DEFECTO #18 CORREGIDO: parametro renombrado a '_'.
        DEFECTO #1 CORREGIDO: el combo se limpia siempre antes de cargar.
        DEFECTO #8 CORREGIDO: aviso cuando no hay horarios disponibles.
        """
        medico = self.combo_med.get()
        self.combo_hor.set("")
        self.combo_hor["values"] = []
        if medico:
            horarios = medicos[medico]["horarios"]
            if not horarios:
                messagebox.showwarning(
                    "Sin disponibilidad",
                    f"El {medico} no tiene horarios disponibles.\n"
                    "Por favor elija otro medico."
                )
            else:
                self.combo_hor["values"] = horarios
 
    # ── Tabla ────────────────────────────────────────────────────────────────
 
    def mostrar(self, datos):
        self.ocultar()
        for c in datos:
            self.tabla.insert(
                "", "end",
                values=(
                    c["dni"],
                    c["paciente"],
                    c["especialidad"],
                    c["medico"],
                    c["fecha_hora"],
                    c["estado"]
                )
            )
 
    def listar(self):
        self.mostrar(consultar_cita(""))
 
    def ocultar(self):
        for i in self.tabla.get_children():
            self.tabla.delete(i)
 
    # ── Acciones ─────────────────────────────────────────────────────────────
 
    def registrar(self):
        """
        DEFECTO #10 CORREGIDO: validacion de campos vacios en la capa de
        vista antes de llegar a la logica de negocio.
        """
        if not self.combo_esp.get():
            messagebox.showerror("Error", "Seleccione una especialidad")
            return
        if not self.combo_med.get():
            messagebox.showerror("Error", "Seleccione un medico")
            return
        if not self.combo_hor.get():
            messagebox.showerror("Error", "Seleccione un horario")
            return
 
        ok, msg = registrar_cita(
            self.entry_dni.get().strip(),
            self.entry_nombre.get().strip(),
            self.combo_esp.get(),
            self.combo_med.get(),
            self.combo_hor.get()
        )
 
        if ok:
            messagebox.showinfo("Correcto", msg)
            self.entry_dni.delete(0, tk.END)
            self.entry_nombre.delete(0, tk.END)
            self.combo_esp.set("")
            self.combo_med.set("")
            self.combo_hor.set("")
        else:
            messagebox.showerror("Error", msg)
 
    def consultar(self):
        dni = self.entry_buscar.get().strip()
        if dni == "":
            messagebox.showerror("Error", "Ingrese DNI")
            return
 
        datos = consultar_cita(dni)
        if not datos:
            messagebox.showinfo("Consulta", "No se encontraron citas")
            self.ocultar()
            return
 
        self.mostrar(datos)
 
    def cancelar(self):
        """
        DEFECTO #6 CORREGIDO: se itera TODA la seleccion, no solo sel[0].
        DEFECTO #9 CORREGIDO: se refresca el combobox de horarios tras cancelar.
        """
        sel = self.tabla.selection()
        if not sel:
            messagebox.showerror("Error", "Seleccione al menos una cita")
            return
 
        canceladas, errores = 0, []
        for item in sel:
            valores = self.tabla.item(item, "values")
            ok, msg = cancelar_cita(valores)
            if ok:
                canceladas += 1
            else:
                errores.append(msg)
 
        self.ocultar()
 
        # DEFECTO #9 CORREGIDO: refrescar combo si hay medico seleccionado
        if self.combo_med.get():
            self.cargar_horarios()
 
        if errores:
            messagebox.showerror("Errores", "\n".join(errores))
        else:
            messagebox.showinfo("Correcto", f"{canceladas} cita(s) canceladas.")
 
    def reasignar(self):
        """
        DEFECTO #7 CORREGIDO: se exige exactamente una seleccion; si hay
        mas de una fila seleccionada se muestra un aviso claro.
        """
        sel = self.tabla.selection()
        if not sel:
            messagebox.showerror("Error", "Seleccione una cita")
            return
 
        if len(sel) > 1:
            messagebox.showerror(
                "Seleccion invalida",
                "Solo puede reasignar una cita a la vez.\n"
                "Seleccione unicamente una fila."
            )
            return
 
        valores = self.tabla.item(sel[0], "values")
 
        ventana = tk.Toplevel(self.root)
        ventana.title("Reasignar")
        ventana.geometry("320x170")
        ventana.configure(bg="#f5fbff")
 
        tk.Label(ventana, text="Nuevo medico", bg="#f5fbff").pack(pady=4)
 
        combo_med = ttk.Combobox(
            ventana,
            values=obtener_medicos_reasignacion(valores[2]),
            state="readonly"
        )
        combo_med.pack()
 
        tk.Label(ventana, text="Nuevo horario", bg="#f5fbff").pack(pady=4)
 
        combo_hor = ttk.Combobox(ventana, state="readonly")
        combo_hor.pack()
 
        def cargar(_ = None):
            """
            DEFECTO #20 CORREGIDO: parametro renombrado a '_'.
            """
            medico = combo_med.get()
            combo_hor["values"] = obtener_horarios_medico(medico)
 
        combo_med.bind("<<ComboboxSelected>>", cargar)
 
        def guardar():
            ok, msg = reasignar_cita(
                valores,
                combo_med.get(),
                combo_hor.get()
            )
            if ok:
                ventana.destroy()
                self.ocultar()
                messagebox.showinfo("Correcto", msg)
            else:
                messagebox.showerror("Error", msg)
 
        tk.Button(
            ventana,
            text="Guardar",
            bg="#28a8e0",
            fg="white",
            relief="flat",
            command=guardar
        ).pack(pady=10)