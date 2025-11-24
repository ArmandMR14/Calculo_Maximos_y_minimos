import re
import tkinter as tk
from tkinter import messagebox, Toplevel, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


# -----------------------------------
#   PARSER DE ECUACIONES LINEALES
# -----------------------------------
def parsear(ec):
    ec = ec.replace(" ", "")

    if "=" not in ec:
        raise ValueError("La ecuación debe incluir '='")

    izq, der = ec.split("=")
    d = float(der)

    izq = izq.replace("-", "+-")
    if izq[0] == "+":
        izq = izq[1:]

    terminos = izq.split("+")

    a = b = c = 0.0
    patron = re.compile(r"([+-]?\d*\.?\d*)(x|y|z)")

    for t in terminos:
        if t == "":
            continue

        m = patron.fullmatch(t)
        if not m:
            raise ValueError(f"Término inválido: {t}")

        coef, var = m.groups()

        if coef in ("", "+", "-"):
            coef = coef + "1"

        coef = float(coef)

        if var == "x":
            a += coef
        elif var == "y":
            b += coef
        elif var == "z":
            c += coef

    return a, b, c, d


# -----------------------------------
#   DETERMINANTE 3x3
# -----------------------------------
def det3(m):
    return (
        m[0][0] * (m[1][1]*m[2][2] - m[1][2]*m[2][1]) -
        m[0][1] * (m[1][0]*m[2][2] - m[1][2]*m[2][0]) +
        m[0][2] * (m[1][0]*m[2][1] - m[1][1]*m[2][0])
    )


# -----------------------------------
#   CRAMER + pasos detallados
# -----------------------------------
def cramer_pasos(a1,b1,c1,d1, a2,b2,c2,d2, a3,b3,c3,d3):

    A = [
        [a1,b1,c1],
        [a2,b2,c2],
        [a3,b3,c3]
    ]

    Ax = [
        [d1,b1,c1],
        [d2,b2,c2],
        [d3,b3,c3]
    ]

    Ay = [
        [a1,d1,c1],
        [a2,d2,c2],
        [a3,d3,c3]
    ]

    Az = [
        [a1,b1,d1],
        [a2,b2,d2],
        [a3,b3,d3]
    ]

    detA = det3(A)
    detAx = det3(Ax)
    detAy = det3(Ay)
    detAz = det3(Az)

    if detA == 0:
        raise ValueError("El sistema NO tiene solución única (det(A)=0)")

    x = detAx / detA
    y = detAy / detA
    z = detAz / detA

    pasos = f"""
Matriz A:
{A}

Ax:
{Ax}

Ay:
{Ay}

Az:
{Az}

det(A)  = {detA}
det(Ax) = {detAx}
det(Ay) = {detAy}
det(Az) = {detAz}

x = det(Ax) / det(A) = {x}
y = det(Ay) / det(A) = {y}
z = det(Az) / det(A) = {z}
"""

    return x, y, z, pasos


# -----------------------------------
#   GRAFICAR PLANOS EN 3D
# -----------------------------------
def graficar(a1,b1,c1,d1, a2,b2,c2,d2, a3,b3,c3,d3, x,y,z):

    X = np.linspace(-10,10,20)
    Y = np.linspace(-10,10,20)
    X, Y = np.meshgrid(X, Y)

    def plano(a,b,c,d):
        if c == 0:
            return None
        return (d - a*X - b*Y)/c

    Z1 = plano(a1,b1,c1,d1)
    Z2 = plano(a2,b2,c2,d2)
    Z3 = plano(a3,b3,c3,d3)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    ax.plot_surface(X,Y,Z1,alpha=0.5,color="red")
    ax.plot_surface(X,Y,Z2,alpha=0.5,color="green")
    ax.plot_surface(X,Y,Z3,alpha=0.5,color="blue")

    ax.scatter([x],[y],[z],color="black",s=80)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.title("Intersección de 3 Planos — Método de Cramer")
    plt.show()


# -----------------------------------
#   TKINTER — INTERFAZ
# -----------------------------------
def resolver():
    try:
        a1,b1,c1,d1 = parsear(e1.get())
        a2,b2,c2,d2 = parsear(e2.get())
        a3,b3,c3,d3 = parsear(e3.get())

        x,y,z,pasos = cramer_pasos(
            a1,b1,c1,d1,
            a2,b2,c2,d2,
            a3,b3,c3,d3
        )

        # Ventana con pasos
        win = Toplevel(root)
        win.title("Pasos del Método de Cramer")
        texto = scrolledtext.ScrolledText(win, width=70, height=30)
        texto.pack()
        texto.insert("end", pasos)

        # Gráfica
        graficar(a1,b1,c1,d1, a2,b2,c2,d2, a3,b3,c3,d3, x,y,z)

    except Exception as e:
        messagebox.showerror("Error", str(e))


root = tk.Tk()
root.title("Cramer 3x3 — Todo en Python")

tk.Label(root, text="Ecuación 1:").pack()
e1 = tk.Entry(root, width=40); e1.pack()

tk.Label(root, text="Ecuación 2:").pack()
e2 = tk.Entry(root, width=40); e2.pack()

tk.Label(root, text="Ecuación 3:").pack()
e3 = tk.Entry(root, width=40); e3.pack()

tk.Button(root, text="Resolver y Graficar", command=resolver).pack(pady=10)

root.mainloop()
