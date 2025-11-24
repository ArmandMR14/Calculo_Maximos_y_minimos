import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

# =============================
#     RESOLVER ECUACIÓN
# =============================

def resolver_ecuacion_trig(ec_str, xmin, xmax):
    x = sp.symbols('x')

    # Pasar ecuación en texto a SymPy
    try:
        lado_izq, lado_der = ec_str.split("=")
        expr = sp.sympify(lado_izq) - sp.sympify(lado_der)
    except Exception as e:
        return None, f"Error al interpretar la ecuación: {e}"

    # Solución simbólica
    try:
        soluciones = sp.solve(sp.Eq(expr, 0), x)
    except Exception as e:
        return None, f"Error al resolver la ecuación: {e}"

    # Expandir soluciones periódicas
    sol_numericas = []
    for sol in soluciones:
        try:
            # Intentar solución numérica
            val = float(sol)
            if xmin <= val <= xmax:
                sol_numericas.append(val)
        except:
            # Si es solución general con 'n', hacer un muestreo
            n = sp.symbols('n', integer=True)
            for k in range(-10, 11):
                try:
                    s = sol.subs(n, k)
                    val = float(s)
                    if xmin <= val <= xmax:
                        sol_numericas.append(val)
                except:
                    pass

    sol_numericas = sorted(set([round(s, 5) for s in sol_numericas]))

    return sol_numericas, None


# =============================
#        GRAFICAR
# =============================

def graficar(ec_str, xmin, xmax, soluciones):
    x = sp.symbols('x')

    lado_izq, lado_der = ec_str.split("=")
    expr = sp.sympify(lado_izq) - sp.sympify(lado_der)

    # Convertir a función numérica
    f = sp.lambdify(x, expr, "numpy")

    X = np.linspace(xmin, xmax, 2000)
    Y = f(X)

    plt.figure(figsize=(8,4))
    plt.axhline(0, color="black", linewidth=1)
    plt.plot(X, Y, label=f"{ec_str}")

    # Marcar soluciones
    for s in soluciones:
        plt.scatter([s], [0], color="red")
        plt.text(s, 0, f"{s:.3f}", fontsize=9)

    plt.title("Solución de ecuación trigonométrica")
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.grid(True)
    plt.legend()
    plt.show()


# =============================
#       INTERFAZ TKINTER
# =============================

def ejecutar():
    ec = entrada_ec.get()
    try:
        xmin = float(entrada_min.get())
        xmax = float(entrada_max.get())
    except:
        messagebox.showerror("Error", "Rango inválido.")
        return

    soluciones, error = resolver_ecuacion_trig(ec, xmin, xmax)

    if error:
        messagebox.showerror("Error", error)
        return

    if not soluciones:
        messagebox.showinfo("Soluciones", "No se encontraron soluciones en este rango.")
    else:
        messagebox.showinfo("Soluciones", "\n".join([str(s) for s in soluciones]))

    graficar(ec, xmin, xmax, soluciones)


# =============================
#     VENTANA PRINCIPAL
# =============================

root = tk.Tk()
root.title("Resolución de ecuaciones trigonométricas")

tk.Label(root, text="Ecuación (ej: sin(x)=0.5):").pack()
entrada_ec = tk.Entry(root, width=40)
entrada_ec.pack()

tk.Label(root, text="Rango mínimo (x):").pack()
entrada_min = tk.Entry(root, width=20)
entrada_min.insert(0, "-6.283")  # -2π
entrada_min.pack()

tk.Label(root, text="Rango máximo (x):").pack()
entrada_max = tk.Entry(root, width=20)
entrada_max.insert(0, "6.283")   # 2π
entrada_max.pack()

tk.Button(root, text="Resolver y Graficar", command=ejecutar).pack(pady=10)

root.mainloop()
