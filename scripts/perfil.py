from js import document, navigator, console, window
from pyscript import when
import asyncio
from pyodide.ffi import to_js

# Simulação de dados de usuário
usuario_logado = {
    "nome": window.localStorage.getItem("nome") or "Xavier Batista Fernandes",
    "email": window.localStorage.getItem("email") or "xavier.batista@medivisao.com",
    "perfil": window.localStorage.getItem("perfil") or "médico",
    "foto": window.localStorage.getItem("foto") or "assets/persona-paciente.png"
}

video = document.getElementById("webcam")
canvas = document.createElement("canvas")
foto = document.getElementById("foto-perfil")

# Preencher os campos com os dados existentes
def carregar_dados():
    document.getElementById("user-nome").innerText = usuario_logado["nome"]
    document.getElementById("user-perfil").innerText = usuario_logado["perfil"]
    document.getElementById("nome").value = usuario_logado["nome"]
    document.getElementById("email").value = usuario_logado["email"]
    document.getElementById("perfil").value = usuario_logado["perfil"]

carregar_dados()

# Salvar alterações no formulário
@when("submit", "#form-perfil")
def salvar_dados(event):
    event.preventDefault()
    usuario_logado["nome"] = document.getElementById("nome").value
    usuario_logado["email"] = document.getElementById("email").value
    usuario_logado["perfil"] = document.getElementById("perfil").value

    # Atualiza no localStorage
    window.localStorage.setItem("nome", usuario_logado["nome"])
    window.localStorage.setItem("email", usuario_logado["email"])
    window.localStorage.setItem("perfil", usuario_logado["perfil"])

    carregar_dados()
    window.alert("Informações atualizadas com sucesso!")

# Ativa a câmera e mostra botão de capturar
@when("click", "#abrir-camera")
async def abrir_camera(event):
    try:
        constraints = to_js({"video": True})
        stream = await navigator.mediaDevices.getUserMedia(constraints)
        video.srcObject = stream
        video.classList.remove("hidden")
        document.getElementById("capturar-foto").classList.remove("hidden")

    except Exception as e:
        window.alert("Erro ao acessar a câmera: " + str(e))

# Captura imagem da câmera e salva no localStorage
@when("click", "#capturar-foto")
def capturar_foto(event):
    try:
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        ctx = canvas.getContext("2d")
        ctx.drawImage(video, 0, 0)

        image_data = canvas.toDataURL("image/png")
        foto.src = image_data
        usuario_logado["foto"] = image_data
        window.localStorage.setItem("foto", image_data)

        # Desliga a câmera
        stream = video.srcObject
        if stream:
            stream.getTracks()[0].stop()
        video.classList.add("hidden")
        document.getElementById("capturar-foto").classList.add("hidden")

        window.alert("Foto de perfil atualizada!")

    except Exception as e:
        window.alert("Erro ao capturar imagem: " + str(e))

@when("click", "#logout-btn")
def sair(_):
    window.sessionStorage.clear()
    window.location.href = "index.html"