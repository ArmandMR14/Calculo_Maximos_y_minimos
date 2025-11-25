import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from sympy import symbols, solve, sympify, Eq, lambdify, pi

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
#        GRAFICAR
# =============================

def graficar(ec_str, xmin, xmax, soluciones, en_grados=True):
    """
    Grafica la ecuación y marca las soluciones
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
        return

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

    plt.figure(figsize=(10, 6))
    plt.axhline(0, color="black", linewidth=1)
    plt.plot(X_plot, Y, label=f"{ec_str}", linewidth=2)

    # Marcar soluciones
    if soluciones:
        for s in soluciones:
            plt.scatter([s], [0], color="red", zorder=5, s=50)
            plt.text(s, 0.1 * max(Y) if max(Y) > 0 else 0.1 * min(Y), 
                    f"{s:.2f}°" if en_grados else f"{s:.3f}", 
                    fontsize=10, ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

    plt.title(f"Solución de ecuación trigonométrica ({'grados' if en_grados else 'radianes'})")
    plt.xlabel(xlabel)
    plt.ylabel("f(x)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

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
        messagebox.showinfo("Soluciones", "No se encontraron soluciones en este rango.")
    else:
        unidad = "°" if en_grados else " rad"
        soluciones_str = "\n".join([f"x = {s:.4f}{unidad}" for s in soluciones])
        messagebox.showinfo("Soluciones encontradas", 
                          f"Se encontraron {len(soluciones)} soluciones:\n\n{soluciones_str}")

    # Graficar
    graficar(ec, xmin, xmax, soluciones, en_grados)

# =============================
#     INTERFAZ GRÁFICA MEJORADA
# =============================

def crear_interfaz():
    """
    Crea y configura la interfaz gráfica
    """
    root = tk.Tk()
    root.title("Resolución de Ecuaciones Trigonométricas")
    root.geometry("500x400")
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

    # Frame para botones
    frame_botones = ttk.Frame(main_frame)
    frame_botones.pack(fill=tk.X, pady=20)

    btn_resolver = ttk.Button(frame_botones, text="Resolver y Graficar", 
                             command=ejecutar, style="Accent.TButton")
    btn_resolver.pack(pady=10)

    # Ejemplos
    frame_ejemplos = ttk.LabelFrame(main_frame, text="Ejemplos", padding="10")
    frame_ejemplos.pack(fill=tk.BOTH, expand=True, pady=5)

    ejemplos = [
        "sin(x) = 0.5",
        "2*cos(x) + sqrt(3) = 0", 
        "tan(x) = 1",
        "sin(2*x) - sin(x) = 0",
        "cos(x) - 2*cos(x)*sin(x) = 0"
    ]

    for i, ejemplo in enumerate(ejemplos):
        btn_ejemplo = ttk.Button(frame_ejemplos, text=ejemplo,
                                command=lambda e=ejemplo: entrada_ec.delete(0, tk.END) or entrada_ec.insert(0, e))
        btn_ejemplo.pack(fill=tk.X, pady=2)

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

    root = crear_interfaz()
    root.mainloop()