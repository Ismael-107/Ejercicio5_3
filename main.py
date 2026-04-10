"""
Actividad 5_3 - Comparación de optimización y documentación en Python

Aplicación con interfaz gráfica (Tkinter) que compara el rendimiento
entre una versión optimizada y una no optimizada utilizando datos en
tiempo real de la ISS (International Space Station).

Incluye:
- Consumo de API
- Comparación de rendimiento
- Perfilado con cProfile
- Interfaz gráfica con Tkinter
"""

import tkinter as tk
from tkinter import messagebox
import requests
import time
import cProfile
import pstats
import io
from datetime import datetime
import random

API_URL = "http://api.open-notify.org/iss-now.json"


# ==============================
# FUNCIONES NO OPTIMIZADAS
# ==============================

def obtener_datos_no_opt():
    """
    Obtiene datos de la ISS de forma NO optimizada.

    Simula un código ineficiente con bucles innecesarios y cálculos redundantes.

    Returns:
        dict: Diccionario con latitud y longitud promedio.
    """
    try:
        response = requests.get(API_URL, timeout=5)
        data = response.json()

        lista = []
        for _ in range(10000):
            lista.append(float(data['iss_position']['latitude']))

        lat = sum(lista) / len(lista)

        lista2 = []
        for _ in range(10000):
            lista2.append(float(data['iss_position']['longitude']))

        lon = sum(lista2) / len(lista2)

        time.sleep(0.3)

        return {"lat": lat, "lon": lon}

    except Exception:
        return {"lat": 0, "lon": 0}


# ==============================
# FUNCIONES OPTIMIZADAS
# ==============================

def obtener_datos_opt():
    """
    Obtiene datos de la ISS de forma optimizada.

    Accede directamente a la API sin estructuras innecesarias.

    Returns:
        dict: Diccionario con latitud y longitud actuales.
    """
    try:
        data = requests.get(API_URL, timeout=5).json()

        return {
            "lat": float(data['iss_position']['latitude']),
            "lon": float(data['iss_position']['longitude'])
        }

    except Exception:
        return {"lat": 0, "lon": 0}


# ==============================
# PERFILADOR
# ==============================

def perfilar(func):
    """
    Ejecuta una función y mide su rendimiento con cProfile.

    Args:
        func (function): Función a analizar.

    Returns:
        tuple:
            - dict: Resultado de la función
            - float: Tiempo de ejecución
            - str: Estadísticas de profiling (cProfile)
    """
    pr = cProfile.Profile()
    pr.enable()

    inicio = time.time()
    resultado = func()
    fin = time.time()

    pr.disable()

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(5)

    return resultado, (fin - inicio), s.getvalue()


# ==============================
# INTERFAZ GRÁFICA
# ==============================

class App:
    """
    Clase principal de la aplicación Tkinter.

    Gestiona la interfaz gráfica, la comparación entre versiones
    y la actualización en tiempo real de los datos.
    """

    def __init__(self, root):
        """
        Inicializa la interfaz gráfica.

        Args:
            root (tk.Tk): Ventana principal de la aplicación.
        """
        self.root = root
        self.root.title("Comparación Optimización Python")
        self.root.geometry("900x500")

        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack(fill="both", expand=True)

        self.dibujar_estrellas()

        self.frame_no = tk.Frame(self.canvas, bg="#330000")
        self.frame_opt = tk.Frame(self.canvas, bg="#003300")

        self.canvas.create_window(0, 0, anchor="nw", window=self.frame_no, width=450, height=500)
        self.canvas.create_window(450, 0, anchor="nw", window=self.frame_opt, width=450, height=500)

        self.crear_panel(self.frame_no, "NO Optimizado", obtener_datos_no_opt)
        self.crear_panel(self.frame_opt, "Optimizado", obtener_datos_opt)

    def dibujar_estrellas(self):
        """
        Dibuja un fondo de estrellas aleatorias para estética espacial.
        """
        for _ in range(200):
            x = random.randint(0, 900)
            y = random.randint(0, 500)
            size = random.randint(1, 3)
            self.canvas.create_oval(x, y, x+size, y+size, fill="white", outline="")

    def crear_panel(self, frame, titulo, funcion):
        """
        Crea un panel de comparación en la interfaz.

        Args:
            frame (tk.Frame): Contenedor del panel.
            titulo (str): Título del panel.
            funcion (callable): Función de obtención de datos.
        """
        tk.Label(frame, text=titulo, font=("Arial", 14), fg="white", bg=frame['bg']).pack()

        datos = tk.Label(frame, text="Datos: ", fg="white", bg=frame['bg'])
        datos.pack()

        tiempo = tk.Label(frame, text="Tiempo: ", fg="white", bg=frame['bg'])
        tiempo.pack()

        hora = tk.Label(frame, text="Hora: ", fg="white", bg=frame['bg'])
        hora.pack()

        perfil = tk.Text(frame, height=10, bg="black", fg="lime")
        perfil.pack()

        tk.Button(frame, text="Help", command=self.mostrar_help).pack()

        def actualizar():
            resultado, t, stats = perfilar(funcion)

            datos.config(text=f"Lat: {resultado['lat']:.2f}, Lon: {resultado['lon']:.2f}")
            tiempo.config(text=f"Tiempo: {t:.5f}s")
            hora.config(text=f"Hora: {datetime.now().strftime('%H:%M:%S')}")

            perfil.delete("1.0", tk.END)
            perfil.insert(tk.END, stats)

            frame.after(5000, actualizar)

        actualizar()

    def mostrar_help(self):
        """
        Muestra ayuda con la documentación de las funciones principales.
        """
        texto = (
            obtener_datos_no_opt.__doc__ + "\n\n" +
            obtener_datos_opt.__doc__
        )
        messagebox.showinfo("Help", texto)


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()