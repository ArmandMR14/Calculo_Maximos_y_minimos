import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from sympy import symbols, solve, sympify, Eq, lambdify, pi
import os
from pathlib import Path

# =============================
#     CONFIGURACIÓN DE GUARDADO
# =============================

def obtener_proximo_nombre_grafica():
    """
    Encuentra el próximo nombre disponible para guardar gráficas
    Formato: grafica_1.png, grafica_2.png, ...
    """
    directorio = Path(".")
    patron = "grafica_*.png"
    
    # Encontrar el número más alto existente
    numero_max = 0
    for archivo in directorio.glob(patron):
        try:
            # Extraer número del nombre: grafica_123.png -> 123
            numero = int(archivo.stem.split('_')[1])
            numero_max = max(numero_max, numero)
        except (IndexError, ValueError):
            continue
    
    siguiente_numero = numero_max + 1
    return f"grafica_{siguiente_numero}.png"

# =============================
#     FUNCIONES DE CONVERSIÓN
# =============================

def radianes_a_grados(rad):
    """Convierte radianes a grados"""
    return rad * 180 / np.pi

def grados_a_radianes(grados):
    """Convierte grados a radianes"""
    return grados * np.pi / 180

# =============================
#     RESOLVER ECUACIÓN
# =============================

def resolver_ecuacion_trig(ec_str, xmin, xmax, en_grados=True):
    """
    Resuelve ecuación trigonométrica en el rango dado
    Devuelve soluciones en grados o radianes según parámetro
    """
    x = symbols('x')

    # Pasar ecuación en texto a SymPy
    try:
        if "=" in ec_str:
            lado_izq, lado_der = ec_str.split("=")
            expr = sympify(lado_izq) - sympify(lado_der)
        else:
            expr = sympify(ec_str)
    except Exception as e:
        return None, f"Error al interpretar la ecuación: {e}"

    # Solución simbólica
    try:
        soluciones = solve(Eq(expr, 0), x)
    except Exception as e:
        return None, f"Error al resolver la ecuación: {e}"

    # Procesar soluciones
    soluciones_finales = []
    for sol in soluciones:
        try:
            # Si es una expresión con n (solución general)
            if sol.has(sp.Symbol):
                n = symbols('n', integer=True)
                # Probar valores de n para encontrar soluciones en el rango
                for k in range(-10, 11):
                    try:
                        s_eval = sol.subs(n, k)
                        if s_eval.is_real:
                            val = float(s_eval)
                            # Convertir a grados si se solicita
                            if en_grados:
                                val = radianes_a_grados(val)
                            if xmin <= val <= xmax:
                                soluciones_finales.append(val)
                    except:
                        continue
            else:
                # Solución numérica directa
                val = float(sol)
                if en_grados:
                    val = radianes_a_grados(val)
                if xmin <= val <= xmax:
                    soluciones_finales.append(val)
                    
        except Exception as e:
            print(f"Advertencia: No se pudo procesar solución {sol}: {e}")

    # Eliminar duplicados y ordenar
    soluciones_finales = sorted(set([round(s, 5) for s in soluciones_finales]))
    
    return soluciones_finales, None

# =============================
#        GRAFICAR Y GUARDAR
# =============================

def graficar(ec_str, xmin, xmax, soluciones, en_grados=True):
    """
    Grafica la ecuación, marca las soluciones y guarda la imagen
    """
    x = symbols('x')

    try:
        if "=" in ec_str:
            lado_izq, lado_der = ec_str.split("=")
            expr = sympify(lado_izq) - sympify(lado_der)
        else:
            expr = sympify(ec_str)
    except Exception as e:
        messagebox.showerror("Error", f"Error al interpretar ecuación: {e}")
        return None

    # Convertir a función numérica
    f = lambdify(x, expr, "numpy")

    # Crear puntos para graficar
    if en_grados:
        # Convertir rango a radianes para evaluación
        X_rad = np.linspace(grados_a_radianes(xmin), grados_a_radianes(xmax), 2000)
        Y = f(X_rad)
        # Convertir de vuelta a grados para el eje X
        X_plot = radianes_a_grados(X_rad)
        xlabel = "x (grados)"
    else:
        X_plot = np.linspace(xmin, xmax, 2000)
        Y = f(X_plot)
        xlabel = "x (radianes)"

    # Crear figura
    plt.figure(figsize=(12, 6))
    plt.axhline(0, color="black", linewidth=1)
    plt.plot(X_plot, Y, label=f"{ec_str}", linewidth=2, color='blue')

    # Marcar soluciones
    if soluciones:
        for s in soluciones:
            plt.scatter([s], [0], color="red", zorder=5, s=80, edgecolors='black')
            offset_y = 0.1 * (max(Y) - min(Y)) if max(Y) != min(Y) else 0.1
            plt.text(s, offset_y, 
                    f"{s:.2f}°" if en_grados else f"{s:.3f}", 
                    fontsize=11, ha='center', 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8))

    unidad = "grados" if en_grados else "radianes"
    plt.title(f"Solución de: {ec_str} | Rango: [{xmin}, {xmax}] {unidad}", fontsize=12)
    plt.xlabel(xlabel, fontsize=11)
    plt.ylabel("f(x)", fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    # Guardar la gráfica
    nombre_archivo = obtener_proximo_nombre_grafica()
    try:
        plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        mensaje_guardado = f"Gráfica guardada como: {nombre_archivo}"
    except Exception as e:
        mensaje_guardado = f"Error al guardar: {e}"

    # Mostrar gráfica
    plt.show()
    
    return nombre_archivo, mensaje_guardado

# =============================
#       FUNCIÓN PRINCIPAL
# =============================

def ejecutar():
    """
    Función principal que ejecuta la resolución y graficación
    """
    ec = entrada_ec.get().strip()
    if not ec:
        messagebox.showerror("Error", "Por favor ingrese una ecuación.")
        return

    try:
        xmin = float(entrada_min.get())
        xmax = float(entrada_max.get())
    except:
        messagebox.showerror("Error", "Rango inválido.")
        return

    # Determinar si usar grados o radianes
    en_grados = var_grados.get()

    soluciones, error = resolver_ecuacion_trig(ec, xmin, xmax, en_grados)

    if error:
        messagebox.showerror("Error", error)
        return

    # Mostrar resultados
    if not soluciones:
        resultado = "No se encontraron soluciones en este rango."
        messagebox.showinfo("Soluciones", resultado)
    else:
        unidad = "°" if en_grados else " rad"
        soluciones_str = "\n".join([f"x = {s:.4f}{unidad}" for s in soluciones])
        resultado = f"Se encontraron {len(soluciones)} soluciones:\n\n{soluciones_str}"
        messagebox.showinfo("Soluciones encontradas", resultado)

    # Graficar y guardar
    nombre_archivo, mensaje_guardado = graficar(ec, xmin, xmax, soluciones, en_grados)
    
    # Mostrar mensaje del guardado
    messagebox.showinfo("Guardado exitoso", 
                       f"{mensaje_guardado}\n\nEcuación: {ec}\n"
                       f"Rango: [{xmin}, {xmax}] {'grados' if en_grados else 'radianes'}\n"
                       f"Soluciones encontradas: {len(soluciones)}")

# =============================
#     INTERFAZ GRÁFICA MEJORADA
# =============================

def crear_interfaz():
    """
    Crea y configura la interfaz gráfica
    """
    root = tk.Tk()
    root.title("Resolución de Ecuaciones Trigonométricas")
    root.geometry("550x450")
    root.resizable(True, True)

    # Frame principal
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Título
    titulo = ttk.Label(main_frame, text="Resolvedor de Ecuaciones Trigonométricas", 
                      font=("Arial", 14, "bold"))
    titulo.pack(pady=(0, 20))

    # Frame para ecuación
    frame_ec = ttk.LabelFrame(main_frame, text="Ecuación", padding="10")
    frame_ec.pack(fill=tk.X, pady=5)

    ttk.Label(frame_ec, text="Ingrese la ecuación (ej: sin(x)=0.5, 2*cos(x)-1=0):").pack(anchor=tk.W)
    global entrada_ec
    entrada_ec = ttk.Entry(frame_ec, width=50, font=("Arial", 10))
    entrada_ec.pack(fill=tk.X, pady=5)
    entrada_ec.insert(0, "sin(x)=0.5")

    # Frame para rango
    frame_rango = ttk.LabelFrame(main_frame, text="Rango de Solución", padding="10")
    frame_rango.pack(fill=tk.X, pady=5)

    # Sub-frame para inputs de rango
    frame_rango_inputs = ttk.Frame(frame_rango)
    frame_rango_inputs.pack(fill=tk.X)

    ttk.Label(frame_rango_inputs, text="Mínimo:").grid(row=0, column=0, padx=(0, 10))
    global entrada_min
    entrada_min = ttk.Entry(frame_rango_inputs, width=15)
    entrada_min.grid(row=0, column=1, padx=(0, 20))
    entrada_min.insert(0, "0")

    ttk.Label(frame_rango_inputs, text="Máximo:").grid(row=0, column=2, padx=(0, 10))
    global entrada_max
    entrada_max = ttk.Entry(frame_rango_inputs, width=15)
    entrada_max.grid(row=0, column=3)
    entrada_max.insert(0, "360")

    ttk.Label(frame_rango_inputs, text="(grados)").grid(row=0, column=4, padx=(10, 0))

    # Opción para grados/radianes
    global var_grados
    var_grados = tk.BooleanVar(value=True)
    check_grados = ttk.Checkbutton(frame_rango, text="Usar grados en lugar de radianes", 
                                  variable=var_grados)
    check_grados.pack(anchor=tk.W, pady=(10, 0))

    # Información de guardado
    info_guardado = ttk.Label(frame_rango, 
                             text="Las gráficas se guardan automáticamente como: grafica_1.png, grafica_2.png, ...",
                             font=("Arial", 8), foreground="gray")
    info_guardado.pack(anchor=tk.W, pady=(5, 0))

    # Frame para botones
    frame_botones = ttk.Frame(main_frame)
    frame_botones.pack(fill=tk.X, pady=20)

    btn_resolver = ttk.Button(frame_botones, text="Resolver y Graficar", 
                             command=ejecutar, style="Accent.TButton")
    btn_resolver.pack(pady=10)

    # Ejemplos
    frame_ejemplos = ttk.LabelFrame(main_frame, text="Ejemplos Rápidos", padding="10")
    frame_ejemplos.pack(fill=tk.BOTH, expand=True, pady=5)

    ejemplos = [
        "sin(x) = 0.5",
        "2*cos(x) + sqrt(3) = 0", 
        "tan(x) = 1",
        "sin(2*x) - sin(x) = 0",
        "cos(x) - 2*cos(x)*sin(x) = 0"
    ]

    # Frame para botones de ejemplos en grid
    frame_grid_ejemplos = ttk.Frame(frame_ejemplos)
    frame_grid_ejemplos.pack(fill=tk.BOTH, expand=True)

    for i, ejemplo in enumerate(ejemplos):
        btn_ejemplo = ttk.Button(frame_grid_ejemplos, text=ejemplo,
                                command=lambda e=ejemplo: entrada_ec.delete(0, tk.END) or entrada_ec.insert(0, e))
        btn_ejemplo.grid(row=i//2, column=i%2, padx=5, pady=2, sticky="ew")
    
    # Configurar columnas iguales
    frame_grid_ejemplos.columnconfigure(0, weight=1)
    frame_grid_ejemplos.columnconfigure(1, weight=1)

    return root

# =============================
#         INICIO
# =============================

if __name__ == "__main__":
    # Configurar estilo para mejor apariencia
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    # Crear directorio para gráficas si no existe
    Path("graficas").mkdir(exist_ok=True)
    
    root = crear_interfaz()
    root.mainloop()