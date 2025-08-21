from flask import Flask, render_template, request, redirect, url_for,session
import pandas as pd
import numpy as np
import os
import random
import math

app = Flask(__name__)
app.secret.key="mi_clave_ultra_secreta"
# Base de datos (usuarios y contraseñas)
DIC= {
    "usuario": ["claulopez", "Jacksoooon","Phdian", "Choco_Marii", "nadiashit","berenice", "pedrinho","davidlima","Esqueyosoyasi","Leohernandez","Lissete","ThePugG","Pollo","Yera","Eugene","Yenny_leal","MrPugs"],
    "contraseña": ["umpalumpa","moonwenee","Mimamimi","Ingatumais","vetealv","amoamifamilia","pecj6573","soydaviddd","DCOPN","Energia","cocacola","Pugcore","GaussJordan","Psique","ferrosolar","Tukola","Axeltorres2002"]
}
usuarios = pd.DataFrame(data=DIC)

# Diccionario letras-números
dic = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7,
    'h': 8, 'i': 9, 'j': 10, 'k': 11, 'l': 12, 'm': 13, 'n': 14,
    'ñ': 15, 'o': 16, 'p': 17, 'q': 18, 'r': 19, 's': 20, 't': 21,
    'u': 22, 'v': 23, 'w': 24, 'x': 25, 'y': 26, 'z': 27,
    ' ': 0, '?': 28, '¿': 29, '.': 30, ':': 31, '¡': 32, '!': 33, ',': 34,"á":35,"é":36,"í":37,"ó":38,"ú":39
}
# Diccionario números-letra
dic_inv = {v: k for k, v in dic.items()}
#Funcion para convertir una string a una lista de números
def codificar_a_numero(texto):
    texto = texto.lower()
    return [dic.get(letra, 0) for letra in texto]
#Función que convierte una lista de numeros a una matriz nxn
def matriz_tamano_nxn(lista):
    n=math.ceil(math.sqrt(len(lista)))
    lista=lista+[0]*(n*n-len(lista))
    return np.array(lista).reshape((n,n))
#Función que convierte un string a un numero entero (semilla)
def convertir_contra_a_num (contraseña,dicc):
    numeros=[str(dic[letra])for letra in contraseña.lower() if letra in dic]
    return int("".join(numeros))
#Función que genera una matriz invertible
def generar_matriz_invertible(tamano, low, high, eps, max_intentos,semilla):     
    random.seed(semilla)
    intentos = 0
    while True:
        intentos += 1
        # 1) Crear lista de tamano*tamano números aleatorios
        lista = [random.randint(low, high) for _ in range(tamano * tamano)]
        # 2) Convertir la lista a un array NumPy y darle forma (reshape) tamano x tamano
        matriz = np.array(lista).reshape(tamano, tamano)
        # 3) Calcular el determinante (número de punto flotante)
        det = np.linalg.det(matriz)
        # 4) Comprobar que no sea "casi" cero
        if abs(det) > eps:
            return matriz
            # 5) Salida segura si no encontramos en max_intentos
    if intentos >= max_intentos:
        raise RuntimeError(f"No se encontró una matriz invertible tras {max_intentos} intentos.")
#Función para invertir una matriz
def inversa_matriz(matriz):
    return np.linalg.inv(matriz)
#Función para convertir un código a una matriz nxn
def convertir_codigo_matriz(codigo):
    lista = [int(num) for num in codigo.split('-') if num.strip().isdigit()]
    n=math.ceil(math.sqrt(len(lista)))
    return np.array(lista).reshape((n,n))
#Función para codificar un mensaje
def mensaje_codificado_final(msj, password):
    lista_msj = codificar_a_numero(msj)
    matriz_A = matriz_tamano_nxn(lista_msj)
    semilla=convertir_contra_a_num (password,dic)
    matriz_B=generar_matriz_invertible(len(matriz_A),1,25,1e-6,1000,semilla)
    matriz_C = np.matmul(matriz_A, matriz_B)
    return '-'.join(str(int(round(num))) for num in matriz_C.flatten())
#Función para decodificar un mensaje
def decodificar_mensaje(codigo, password):
    matriz_C = convertir_codigo_matriz(codigo)
    semilla=convertir_contra_a_num (password,dic)
    matriz_B=generar_matriz_invertible(len(matriz_C),1,25,1e-6,1000,semilla)
    matriz_inv_B = inversa_matriz(matriz_B)
    matriz_A = np.matmul(matriz_C, matriz_inv_B)
    matriz_A_int = np.rint(matriz_A).astype(int)
    letras = [dic_inv.get(num, '') for num in matriz_A_int.flatten()]
    return ''.join(letras).capitalize()
@app.route('/', methods=['GET', 'POST'])
def login():
    mensaje=""
    if request.method == 'POST':
        user = request.form['usuario']
        password = request.form['contraseña']
        validacion = usuarios[(usuarios['usuario'] == user) & (usuarios['contraseña'] == password)]
        if not validacion.empty:
            session['usuario']=user
            session['contraseña']=password
            return redirect (url_for('opciones'))
        else:
            mensaje = "❌ Usuario o contraseña incorrectos"
    return render_template('login.html',mensaje=mensaje)

@app.route('/opciones')
def opciones():
    if "usuario" not in session: #si no hay sesion activa
        return redirect(url_for("login"))
    return render_template('opciones.html',user=session['usuario'], password=session['password'])
    

@app.route('/escribir', methods=['GET', 'POST'])
def escribir():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if request.method == 'POST':
        mensaje = request.form['mensaje']
        password = request.form['password']
        codificado = mensaje_codificado_final(mensaje, password)
        return render_template('resultado.html', resultado=codificado, tipo="Mensaje codificado")
    
    return render_template('escribir.html', user=session['usuario'], password=session['password'])

@app.route('/leer', methods=['GET', 'POST'])
def leer():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if request.method == 'POST':
        codigo = request.form['codigo']
        password = request.form['password']
        mensaje = decodificar_mensaje(codigo, password)
        return render_template('resultado.html', resultado=mensaje, tipo="Mensaje decodificado")
    return render_template('leer.html', user=session['usuario'], password=session['password'])
@app.route('/logout')
def logout():
    session.clear() #borra todo lo que hay en la sesión
    return redirect(url_for('login'))

# Ejecutar el servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Toma el puerto que Render le indique
    app.run(host="0.0.0.0", port=port)
























