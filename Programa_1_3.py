import tkinter as tk
from tkinter import messagebox
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageTk


def formatear_funcion(expr):
    """Convierte una expresión sympy a formato legible"""
    x = sp.Symbol('x')
    expr_sym = sp.sympify(expr)
    
    # Convertir a string y reemplazar formatos
    expr_str = str(expr_sym)
    
    # Reemplazos para mejor legibilidad
    reemplazos = {
        '**': '^',
        '*': '*',
        'sin': 'sen',
        'asin': 'arcsen',
        'acos': 'arccos',
        'atan': 'arctan'
    }
    
    for viejo, nuevo in reemplazos.items():
        expr_str = expr_str.replace(viejo, nuevo)
    
    return expr_str, expr_sym


def calcular():
    expr_str = entry_func.get()
    try:
        x = sp.Symbol('x')
        f = sp.sympify(expr_str)
        f_prime = sp.diff(f, x)
        
        # Formatear funciones para mostrar
        f_str, _ = formatear_funcion(expr_str)
        f_prime_str, _ = formatear_funcion(str(f_prime))
        
        # Mostrar función y derivada en la interfaz
        label_func.config(text=f"f(x) = {f_str}")
        label_derivada.config(text=f"f'(x) = {f_prime_str}")
        
        # Mostrar también en formato matemático avanzado
        try:
            from sympy.printing.pretty import pretty
            func_pretty = pretty(f, use_unicode=True)
            derivada_pretty = pretty(f_prime, use_unicode=True)
            label_func_pretty.config(text=f"f(x) = {func_pretty}")
            label_derivada_pretty.config(text=f"f'(x) = {derivada_pretty}")
        except:
            label_func_pretty.config(text="")
            label_derivada_pretty.config(text="")

        # Puntos críticos
        critical_points = sp.solve(sp.Eq(f_prime, 0), x)

        # Función numérica
        f_lamb = sp.lambdify(x, f, 'numpy')

        # Determinar rango automáticamente basado en puntos críticos
        if critical_points:
            # Usar puntos críticos para determinar el rango
            real_points = [float(c) for c in critical_points if c.is_real]
            if real_points:
                x_min = min(real_points) - 2
                x_max = max(real_points) + 2
            else:
                x_min, x_max = -10, 10
        else:
            # Si no hay puntos críticos, usar rango por defecto
            x_min, x_max = -10, 10

        # Asegurar que el rango tenga un tamaño mínimo
        if x_max - x_min < 4:
            center = (x_min + x_max) / 2
            x_min = center - 2
            x_max = center + 2

        x_vals = np.linspace(x_min, x_max, 400)
        y_vals = f_lamb(x_vals)

        # Calcular límites de y
        y_min = np.min(y_vals)
        y_max = np.max(y_vals)
        
        # Ajustar para incluir puntos críticos
        for c in critical_points:
            if c.is_real:
                y_c = float(f.subs(x, c))
                y_min = min(y_min, y_c)
                y_max = max(y_max, y_c)

        # Agregar márgenes
        y_range = y_max - y_min
        if y_range == 0:  # Para funciones constantes
            y_min -= 1
            y_max += 1
        else:
            margin = y_range * 0.1  # 10% de margen
            y_min -= margin
            y_max += margin

        # Hacer la gráfica proporcional
        x_range = x_max - x_min
        y_range_adj = y_max - y_min
        
        # Calcular relación de aspecto para que sea proporcional
        fig_width = 8
        fig_height = 6
        
        # Ajustar altura según el rango de y vs x
        desired_ratio = y_range_adj / x_range
        current_ratio = fig_height / fig_width
        
        if desired_ratio > current_ratio:
            # La función es más "alta" que "ancha"
            fig_height = fig_width * desired_ratio
        else:
            # La función es más "ancha" que "alta"
            fig_width = fig_height / desired_ratio
        
        # Limitar el tamaño máximo de la figura
        fig_width = min(fig_width, 12)
        fig_height = min(fig_height, 10)
        
        # Limitar el tamaño mínimo de la figura
        fig_width = max(fig_width, 6)
        fig_height = max(fig_height, 4)



        plt.figure(figsize=(fig_width, fig_height))
        plt.plot(x_vals, y_vals, color="blue", label=f"f(x) = {f_str}", linewidth=2)

        # Marcar máximos y mínimos
        for c in critical_points:
            if c.is_real:
                y_c = float(f.subs(x, c))
                f2 = sp.diff(f_prime, x)
                d2_val = float(f2.subs(x, c))
                if d2_val > 0:
                    tipo = "mínimo"
                    color = "green"
                elif d2_val < 0:
                    tipo = "máximo"
                    color = "red"
                else:
                    tipo = "inflexión"
                    color = "black"
                plt.scatter(float(c), y_c, color=color, s=100, zorder=5,
                            label=f"{tipo} en x={float(c):.2f}")

        # Establecer límites y hacer ejes proporcionales
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        
        # Hacer que la escala sea igual en ambos ejes (proporcional)
        plt.gca().set_aspect('auto')  # 'auto' para ajuste automático
        
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.title(f"Función: f(x) = {f_str}\nDerivada: f'(x) = {f_prime_str}")
        plt.xlabel("x")
        plt.ylabel("y")
        
        # Ajustar diseño
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")


# Interfaz Tkinter
root = tk.Tk()
root.title("Máximos y Mínimos - Función y Derivada")

# Frame principal para organizar mejor los elementos
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10)

# Frame para la imagen y los controles
top_frame = tk.Frame(main_frame)
top_frame.pack(fill=tk.X)

# Cargar y mostrar la imagen kitty.jpg
try:
    # Intentar cargar la imagen
    image = Image.open("kitty.jpg")
    # Redimensionar la imagen si es muy grande (opcional)
    image = image.resize((150, 150), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    
    # Crear label para la imagen
    image_label = tk.Label(top_frame, image=photo)
    image_label.image = photo  # Mantener una referencia
    image_label.pack(side=tk.LEFT, padx=(0, 10))
    
except Exception as e:
    # Si hay error al cargar la imagen, mostrar un mensaje
    error_label = tk.Label(top_frame, text="No se pudo cargar kitty.jpg", 
                          fg="red", font=("Arial", 8))
    error_label.pack(side=tk.LEFT, padx=(0, 10))
    print(f"Error al cargar la imagen: {e}")

# Frame para los controles (derecha de la imagen)
controls_frame = tk.Frame(top_frame)
controls_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

tk.Label(controls_frame, text="Introduce una función en x:").pack(anchor=tk.W)
entry_func = tk.Entry(controls_frame, width=30)
entry_func.pack(fill=tk.X, pady=(0, 5))
entry_func.insert(0, "x**3 - 3*x")  # Ejemplo por defecto

tk.Button(controls_frame, text="Calcular", command=calcular).pack(fill=tk.X, pady=5)

# Frame para mostrar función y derivada
resultados_frame = tk.Frame(controls_frame)
resultados_frame.pack(fill=tk.X, pady=5)

# Labels para mostrar función y derivada formateadas
label_func = tk.Label(resultados_frame, text="f(x) = ", font=("Arial", 10, "bold"))
label_func.pack(anchor=tk.W)

label_derivada = tk.Label(resultados_frame, text="f'(x) = ", font=("Arial", 10, "bold"))
label_derivada.pack(anchor=tk.W)

# Labels para formato matemático avanzado (si está disponible)
label_func_pretty = tk.Label(resultados_frame, text="", font=("Courier New", 9))
label_func_pretty.pack(anchor=tk.W)

label_derivada_pretty = tk.Label(resultados_frame, text="", font=("Courier New", 9))
label_derivada_pretty.pack(anchor=tk.W)

# Instrucciones
instrucciones_frame = tk.Frame(main_frame)
instrucciones_frame.pack(fill=tk.X, pady=(10, 0))

instrucciones = """Ejemplos:
x^2 + 2*x + 1      (x al cuadrado más 2x más 1)
x^3 - 3*x          (x al cubo menos 3x)
sin(x)             (seno de x)
cos(x)             (coseno de x)
exp(x)             (exponencial de x)
log(x)             (logaritmo natural de x)
x^4 - 4*x^2        (x a la cuarta menos 4x al cuadrado)"""
tk.Label(instrucciones_frame, text=instrucciones, justify=tk.LEFT, 
         font=("Arial", 10), bg="lightyellow", relief=tk.SUNKEN, padx=5, pady=5).pack(fill=tk.X)

root.mainloop()
