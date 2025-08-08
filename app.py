from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Base de datos (usuarios y contraseñas)
DIC = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7,
    'h': 8, 'i': 9, 'j': 10, 'k': 11, 'l': 12, 'm': 13, 'n': 14,
    'ñ': 15, 'o': 16, 'p': 17, 'q': 18, 'r': 19, 's': 20, 't': 21,
    'u': 22, 'v': 23, 'w': 24, 'x': 25, 'y': 26, 'z': 27,
    ' ': 0, '?': 28, '¿': 29, '.': 30, ':': 31, '¡': 32, '!': 33, ',': 34,"á":35,"é":36,"í":37,"ó":38,"ú":39
}
usuarios = pd.DataFrame(data=DIC)

# Diccionario letras-números
dic = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7,
    'h': 8, 'i': 9, 'j': 10, 'k': 11, 'l': 12, 'm': 13, 'n': 14,
    'ñ': 15, 'o': 16, 'p': 17, 'q': 18, 'r': 19, 's': 20, 't': 21,
    'u': 22, 'v': 23, 'w': 24, 'x': 25, 'y': 26, 'z': 27,
    ' ': 0, '?': 28, '¿': 29, '.': 30, ':': 31, '¡': 32, '!': 33, ',': 34
}
# Diccionario números-letra
dic_inv = {v: k for k, v in dic.items()}
#Funcion para convertir una string a una lista de números
def codificar_a_numero(texto):
    texto = texto.lower()
    return [dic.get(letra, 0) for letra in texto]
#Función para convertir una lista de números una matriz 4x4
def convertir_msj_matriz_4x4(lista):
    lista = lista[:16] + [0] * (16 - len(lista)) if len(lista) < 16 else lista[:16]
    return np.array(lista).reshape((4, 4))
#Función para rellenar una lista de números a una nueva lista con cierta extensión
def lista_clave_rellena(lista_clave, longitud):
    return (lista_clave * ((longitud // len(lista_clave)) + 1))[:longitud]
#Función para convertir una lista de números de cierta extensión a una matriz 4x4
def clave_matriz(clave_list):
    return np.array(clave_list).reshape((4, 4))
#Función para invertir una matriz
def inversa_matriz(matriz):
    return np.linalg.inv(matriz)
#Función para convertir un código a una matriz 4x4
def convertir_codigo_matriz(codigo):
    lista = [int(num) for num in codigo.split('-') if num.strip().isdigit()]
    return np.array(lista).reshape((4, 4))
#Función para codificar un mensaje
def mensaje_codificado_final(msj, password):
    lista_msj = codificar_a_numero(msj)
    matriz_A = convertir_msj_matriz_4x4(lista_msj)
    lista_clave = codificar_a_numero(password)
    matriz_B = clave_matriz(lista_clave_rellena(lista_clave, 16))
    matriz_C = np.matmul(matriz_A, matriz_B)
    return '-'.join(str(int(round(num))) for num in matriz_C.flatten())
#Función para decodificar un mensaje

def decodificar_mensaje(codigo, password):
    matriz_C = convertir_codigo_matriz(codigo)
    lista_clave = codificar_a_numero(password)
    matriz_B = clave_matriz(lista_clave_rellena(lista_clave, 16))
    matriz_inv_B = inversa_matriz(matriz_B)
    matriz_A = np.matmul(matriz_C, matriz_inv_B)
    matriz_A_int = np.rint(matriz_A).astype(int)
    letras = [dic_inv.get(num, '') for num in matriz_A_int.flatten()]
    return ''.join(letras)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['usuario']
        password = request.form['contraseña']
        validacion = usuarios[(usuarios['usuario'] == user) & (usuarios['contraseña'] == password)]
        if not validacion.empty:
            return redirect(url_for('opciones', user=user, password=password))
        else:
            mensaje = "❌ Usuario o contraseña incorrectos"
            return render_template('login.html', mensaje=mensaje)
    return render_template('login.html')

@app.route('/opciones')
def opciones():
    user = request.args.get('user')
    password = request.args.get('password')
    return render_template('opciones.html', user=user, password=password)

@app.route('/escribir', methods=['GET', 'POST'])
def escribir():
    if request.method == 'POST':
        mensaje = request.form['mensaje']
        password = request.form['password']
        codificado = mensaje_codificado_final(mensaje, password)
        return render_template('resultado.html', resultado=codificado, tipo="Mensaje codificado")
    user = request.args.get('user')
    password = request.args.get('password')
    return render_template('escribir.html', user=user, password=password)

@app.route('/leer', methods=['GET', 'POST'])
def leer():
    if request.method == 'POST':
        codigo = request.form['codigo']
        password = request.form['password']
        mensaje = decodificar_mensaje(codigo, password)
        return render_template('resultado.html', resultado=mensaje, tipo="Mensaje decodificado")
    user = request.args.get('user')
    password = request.args.get('password')
    return render_template('leer.html', user=user, password=password)


# Ejecutar el servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Toma el puerto que Render le indique
    app.run(host="0.0.0.0", port=port)









