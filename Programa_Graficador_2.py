import tkinter as tk
from tkinter import messagebox, ttk
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageTk
from sympy import oo
import warnings
warnings.filterwarnings('ignore')

# ==================== FUNCIONES DE VALIDACIÓN Y CÁLCULO ====================

def validar_funcion(expr):
    """Valida que la función sea correcta"""
    try:
        x = sp.Symbol('x')
        f = sp.parse_expr(expr, transformations='all')
        # Verificar que dependa de x
        if x not in f.free_symbols:
            raise ValueError("La función debe depender de la variable x")
        return f
    except Exception as e:
        raise ValueError(f"Función inválida: {e}")

def formatear_funcion(expr):
    """Convierte una expresión sympy a formato legible"""
    try:
        x = sp.Symbol('x')
        expr_sym = sp.parse_expr(expr, transformations='all')
        
        # Convertir a LaTeX para mejor visualización
        try:
            expr_str = sp.latex(expr_sym)
        except:
            expr_str = str(expr_sym)
        
        # Reemplazos para mejor legibilidad
        reemplazos = {
            '**': '^',
            'sin': 'sen',
            'asin': 'arcsen',
            'acos': 'arccos',
            'atan': 'arctan'
        }
        
        for viejo, nuevo in reemplazos.items():
            expr_str = expr_str.replace(viejo, nuevo)
        
        return expr_str, expr_sym
    except Exception as e:
        raise ValueError(f"Error al procesar la expresión: {e}")

def encontrar_puntos_criticos(f, x):
    """Encuentra puntos críticos de manera más robusta"""
    f_prime = sp.diff(f, x)
    
    # Resolver ecuación derivada = 0
    try:
        critical_points = sp.solve(sp.Eq(f_prime, 0), x)
    except:
        critical_points = []
    
    # Filtrar solo puntos reales y eliminar duplicados
    puntos_reales = []
    for punto in critical_points:
        if punto.is_real:
            try:
                valor = float(punto)
                # Evitar duplicados
                if not any(abs(valor - p[0]) < 1e-5 for p in puntos_reales):
                    puntos_reales.append((valor, 'derivada_cero'))
            except:
                continue
    
    return puntos_reales

def clasificar_punto_critico(f, x, punto):
    """Clasifica un punto crítico de manera más precisa"""
    f_prime = sp.diff(f, x)
    f_double_prime = sp.diff(f_prime, x)
    
    try:
        seg_derivada = f_double_prime.subs(x, punto)
        if seg_derivada > 0:
            return "mínimo"
        elif seg_derivada < 0:
            return "máximo"
        else:
            # Usar criterio de mayor orden
            return "posible punto de inflexión"
    except:
        return "indeterminado"

def determinar_rango_optimo(f, critical_points, x):
    """Determina el rango óptimo para la gráfica"""
    if critical_points:
        puntos_x = [p[0] for p in critical_points]
        x_min = min(puntos_x) - 3
        x_max = max(puntos_x) + 3
    else:
        # Evaluar la función en algunos puntos para determinar comportamiento
        try:
            # Probar diferentes rangos para ver dónde está definida la función
            test_points = np.linspace(-10, 10, 50)
            f_lamb = sp.lambdify(x, f, 'numpy')
            y_test = f_lamb(test_points)
            defined_points = test_points[np.isfinite(y_test)]
            if len(defined_points) > 0:
                x_min = max(-10, np.min(defined_points) - 2)
                x_max = min(10, np.max(defined_points) + 2)
            else:
                x_min, x_max = -5, 5
        except:
            x_min, x_max = -5, 5
    
    # Asegurar un rango mínimo
    if x_max - x_min < 4:
        center = (x_min + x_max) / 2
        x_min = center - 2
        x_max = center + 2
    
    return x_min, x_max

def calcular_integral(f, x):
    """Calcula la integral indefinida"""
    try:
        return sp.integrate(f, x)
    except:
        return "No se pudo calcular la integral"

def calcular_taylor(f, x, punto=0, orden=5):
    """Calcula serie de Taylor alrededor de un punto"""
    try:
        return sp.series(f, x, punto, orden).removeO()
    except:
        return "No se pudo calcular la serie de Taylor"

# ==================== FUNCIONES DE VISUALIZACIÓN ====================

def crear_grafica_mejorada(f, f_str, f_prime_str, critical_points, x):
    """Crea una gráfica más informativa y profesional"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Configurar rango de x de manera más inteligente
    x_min, x_max = determinar_rango_optimo(f, critical_points, x)
    x_vals = np.linspace(x_min, x_max, 1000)
    
    # Convertir a función numérica
    try:
        f_lamb = sp.lambdify(x, f, 'numpy')
        f_prime_lamb = sp.lambdify(x, sp.diff(f, x), 'numpy')
        
        y_vals = f_lamb(x_vals)
        y_prime_vals = f_prime_lamb(x_vals)
        
        # Gráfica de la función
        ax1.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'f(x)')
        
        # Marcar puntos críticos
        for punto, _ in critical_points:
            y_val = float(f.subs(x, punto))
            tipo = clasificar_punto_critico(f, x, punto)
            color = 'green' if 'mínimo' in tipo else 'red' if 'máximo' in tipo else 'orange'
            ax1.scatter(punto, y_val, color=color, s=100, zorder=5, 
                       label=f'{tipo} en x={punto:.2f}')
        
        ax1.set_title('Función y Puntos Críticos')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlabel('x')
        ax1.set_ylabel('f(x)')
        
        # Gráfica de la derivada
        ax2.plot(x_vals, y_prime_vals, 'r-', linewidth=2, label=f"f'(x)")
        ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        
        # Marcar donde la derivada es cero
        for punto, _ in critical_points:
            ax2.axvline(x=punto, color='gray', linestyle=':', alpha=0.7)
        
        ax2.set_title('Derivada de la Función')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlabel('x')
        ax2.set_ylabel("f'(x)")
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        plt.close()
        # Intentar gráfica simple si falla la doble
        return crear_grafica_simple(f, f_str, f_prime_str, critical_points, x)

def crear_grafica_simple(f, f_str, f_prime_str, critical_points, x):
    """Crea una gráfica simple como fallback"""
    x_min, x_max = determinar_rango_optimo(f, critical_points, x)
    x_vals = np.linspace(x_min, x_max, 1000)
    
    f_lamb = sp.lambdify(x, f, 'numpy')
    y_vals = f_lamb(x_vals)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'f(x) = {f_str}')
    
    # Marcar puntos críticos
    for punto, _ in critical_points:
        y_val = float(f.subs(x, punto))
        tipo = clasificar_punto_critico(f, x, punto)
        color = 'green' if 'mínimo' in tipo else 'red' if 'máximo' in tipo else 'orange'
        plt.scatter(punto, y_val, color=color, s=100, zorder=5, 
                   label=f'{tipo} en x={punto:.2f}')
    
    plt.title(f'Función: f(x) = {f_str}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.tight_layout()
    
    return plt.gcf()

# ==================== CLASE PRINCIPAL DE LA APLICACIÓN ====================

class CalculadoraCalculo:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Maximos, Minimos y Derivación")
        self.root.geometry("800x700")
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(main_frame, text="Calculadora de Cálculo Diferencial", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Frame de entrada
        input_frame = tk.LabelFrame(main_frame, text="Entrada de Función", 
                                   font=("Arial", 10, "bold"), padx=10, pady=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Entrada de función
        tk.Label(input_frame, text="f(x) =", font=("Arial", 11)).grid(row=0, column=0, sticky='w')
        
        self.entry_func = tk.Entry(input_frame, width=40, font=("Courier New", 12))
        self.entry_func.grid(row=0, column=1, sticky='we', padx=5)
        self.entry_func.insert(0, "x**3 - 3*x")
        self.entry_func.bind('<Return>', lambda e: self.calcular())
        
        # Configurar peso de columna para que se expanda
        input_frame.columnconfigure(1, weight=1)
        
        # Botones
        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='we')
        
        tk.Button(button_frame, text="Calcular", command=self.calcular, 
                 bg="lightblue", font=("Arial", 10, "bold"), width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Limpiar", command=self.limpiar,
                 bg="lightyellow", font=("Arial", 10), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Ejemplos", command=self.mostrar_ejemplos,
                 bg="lightgreen", font=("Arial", 10), width=10).pack(side=tk.LEFT, padx=5)
        
        # Frame de resultados
        self.result_frame = tk.LabelFrame(main_frame, text="Resultados", 
                                        font=("Arial", 10, "bold"), padx=10, pady=10)
        self.result_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook (pestañas) para organizar resultados
        self.notebook = ttk.Notebook(self.result_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de resultados básicos
        self.basic_tab = tk.Frame(self.notebook)
        self.notebook.add(self.basic_tab, text="Análisis Básico")
        
        # Pestaña de resultados avanzados
        self.advanced_tab = tk.Frame(self.notebook)
        self.notebook.add(self.advanced_tab, text="Análisis Avanzado")
        
        # Configurar pestaña básica
        self.setup_basic_tab()
        
        # Configurar pestaña avanzada
        self.setup_advanced_tab()
        
        # Configurar estilos de texto
        self.text_basic.tag_configure("titulo", font=("Arial", 11, "bold"), 
                                     foreground="darkblue")
        self.text_basic.tag_configure("subtitulo", font=("Arial", 10, "bold"), 
                                     foreground="darkred")
        self.text_basic.tag_configure("resultado", font=("Courier New", 10))
        
        self.text_advanced.tag_configure("titulo", font=("Arial", 11, "bold"), 
                                        foreground="darkblue")
        self.text_advanced.tag_configure("resultado", font=("Courier New", 9))
    
    def setup_basic_tab(self):
        """Configura la pestaña de análisis básico"""
        # Área de texto para resultados básicos
        self.text_basic = tk.Text(self.basic_tab, wrap=tk.WORD, height=20)
        scrollbar_basic = tk.Scrollbar(self.basic_tab, command=self.text_basic.yview)
        self.text_basic.config(yscrollcommand=scrollbar_basic.set)
        
        self.text_basic.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_basic.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_advanced_tab(self):
        """Configura la pestaña de análisis avanzado"""
        # Área de texto para resultados avanzados
        self.text_advanced = tk.Text(self.advanced_tab, wrap=tk.WORD, height=20)
        scrollbar_advanced = tk.Scrollbar(self.advanced_tab, command=self.text_advanced.yview)
        self.text_advanced.config(yscrollcommand=scrollbar_advanced.set)
        
        self.text_advanced.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_advanced.pack(side=tk.RIGHT, fill=tk.Y)
    
    def calcular(self):
        """Realiza todos los cálculos y muestra resultados"""
        try:
            expr = self.entry_func.get().strip()
            if not expr:
                messagebox.showwarning("Advertencia", "Por favor ingresa una función")
                return
            
            # Validar y procesar función
            f = validar_funcion(expr)
            x = sp.Symbol('x')
            
            # Cálculos básicos
            f_prime = sp.diff(f, x)
            puntos_criticos = encontrar_puntos_criticos(f, x)
            
            # Clasificar puntos críticos
            puntos_clasificados = []
            for punto, _ in puntos_criticos:
                tipo = clasificar_punto_critico(f, x, punto)
                puntos_clasificados.append((punto, tipo))
            
            # Mostrar resultados en las pestañas
            self.mostrar_resultados_basicos(f, f_prime, puntos_clasificados, x)
            self.mostrar_resultados_avanzados(f, x)
            
            # Crear y mostrar gráfica
            fig = crear_grafica_mejorada(f, sp.latex(f), sp.latex(f_prime), 
                                       puntos_clasificados, x)
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
    
    def mostrar_resultados_basicos(self, f, f_prime, puntos_criticos, x):
        """Muestra resultados básicos en la primera pestaña"""
        self.text_basic.delete(1.0, tk.END)
        
        # Función original
        self.text_basic.insert(tk.END, "FUNCIÓN ANALIZADA:\n", "titulo")
        self.text_basic.insert(tk.END, f"f(x) = {sp.pretty(f, use_unicode=True)}\n\n")
        
        # Derivada
        self.text_basic.insert(tk.END, "DERIVADA PRIMERA:\n", "titulo")
        self.text_basic.insert(tk.END, f"f'(x) = {sp.pretty(f_prime, use_unicode=True)}\n\n")
        
        # Puntos críticos
        self.text_basic.insert(tk.END, "PUNTOS CRÍTICOS:\n", "titulo")
        if puntos_criticos:
            for punto, tipo in puntos_criticos:
                y_val = f.subs(x, punto)
                self.text_basic.insert(tk.END, 
                    f"• x = {punto:.4f}, f(x) = {float(y_val):.4f} → {tipo}\n", "resultado")
        else:
            self.text_basic.insert(tk.END, "No se encontraron puntos críticos\n")
        
        # Segunda derivada
        f_double_prime = sp.diff(f_prime, x)
        self.text_basic.insert(tk.END, "\nDERIVADA SEGUNDA:\n", "titulo")
        self.text_basic.insert(tk.END, f"f''(x) = {sp.pretty(f_double_prime, use_unicode=True)}\n\n")
        
        # Información sobre concavidad
        self.text_basic.insert(tk.END, "CONCAVIDAD:\n", "titulo")
        try:
            # Analizar signo de la segunda derivada
            if f_double_prime.is_constant():
                signo = "positiva" if f_double_prime > 0 else "negativa" if f_double_prime < 0 else "cero"
                self.text_basic.insert(tk.END, f"La función es cóncava hacia {signo} en todo su dominio\n")
            else:
                self.text_basic.insert(tk.END, "La concavidad varía en diferentes intervalos\n")
        except:
            self.text_basic.insert(tk.END, "No se pudo determinar la concavidad\n")
    
    def mostrar_resultados_avanzados(self, f, x):
        """Muestra resultados avanzados en la segunda pestaña"""
        self.text_advanced.delete(1.0, tk.END)
        
        # Integral
        self.text_advanced.insert(tk.END, "INTEGRAL INDEFINIDA:\n", "titulo")
        integral = calcular_integral(f, x)
        self.text_advanced.insert(tk.END, f"∫ f(x) dx = {sp.pretty(integral, use_unicode=True)}\n\n", "resultado")
        
        # Serie de Taylor
        self.text_advanced.insert(tk.END, "SERIE DE TAYLOR (alrededor de x=0):\n", "titulo")
        taylor = calcular_taylor(f, x)
        self.text_advanced.insert(tk.END, f"{sp.pretty(taylor, use_unicode=True)}\n\n", "resultado")
        
        # Límites
        self.text_advanced.insert(tk.END, "LÍMITES:\n", "titulo")
        try:
            lim_inf_pos = sp.limit(f, x, oo)
            lim_inf_neg = sp.limit(f, x, -oo)
            self.text_advanced.insert(tk.END, f"Límite cuando x → +∞: {sp.pretty(lim_inf_pos, use_unicode=True)}\n", "resultado")
            self.text_advanced.insert(tk.END, f"Límite cuando x → -∞: {sp.pretty(lim_inf_neg, use_unicode=True)}\n\n", "resultado")
        except:
            self.text_advanced.insert(tk.END, "Límites no disponibles\n\n")
        
        # Información del dominio
        self.text_advanced.insert(tk.END, "INFORMACIÓN DEL DOMINIO:\n", "titulo")
        try:
            # Buscar puntos donde la función no está definida
            singularidades = sp.singularities(f, x)
            if singularites:
                self.text_advanced.insert(tk.END, f"Puntos singulares: {singularities}\n", "resultado")
            else:
                self.text_advanced.insert(tk.END, "La función parece estar definida para todos los reales\n", "resultado")
        except:
            self.text_advanced.insert(tk.END, "No se pudo analizar el dominio completamente\n", "resultado")
    
    def limpiar(self):
        """Limpia todos los campos"""
        self.entry_func.delete(0, tk.END)
        self.text_basic.delete(1.0, tk.END)
        self.text_advanced.delete(1.0, tk.END)
    
    def mostrar_ejemplos(self):
        """Muestra ejemplos de funciones"""
        ejemplos = [
            "x^2 + 2*x + 1",
            "x^3 - 3*x",
            "sin(x)",
            "cos(x)",
            "exp(x)",
            "log(x + 1)",
            "1/(x^2 + 1)",
            "sqrt(x^2 + 1)",
            "x*sin(x)",
            "exp(-x^2)"
        ]
        
        # Crear ventana de ejemplos
        ejemplos_window = tk.Toplevel(self.root)
        ejemplos_window.title("Ejemplos de Funciones")
        ejemplos_window.geometry("300x400")
        
        tk.Label(ejemplos_window, text="Selecciona un ejemplo:", 
                font=("Arial", 11, "bold")).pack(pady=10)
        
        for ejemplo in ejemplos:
            def make_lambda(ej=ejemplo):
                return lambda: self.seleccionar_ejemplo(ej, ejemplos_window)
            
            btn = tk.Button(ejemplos_window, text=ejemplo, command=make_lambda(),
                          font=("Courier New", 9), width=30, anchor='w')
            btn.pack(pady=2, padx=10)
    
    def seleccionar_ejemplo(self, ejemplo, window):
        """Selecciona un ejemplo y cierra la ventana"""
        self.entry_func.delete(0, tk.END)
        self.entry_func.insert(0, ejemplo.replace('^', '**'))
        window.destroy()
        self.calcular()

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    try:
        root = tk.Tk()
        app = CalculadoraCalculo(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error Inesperado", f"Error al iniciar la aplicación: {e}")

if __name__ == "__main__":
    main()
