from js import document, navigator, console, window
from pyscript import when
import asyncio
from pyodide.ffi import to_js


# Simulação de dados de usuário
usuario_logado = {
    "name": window.localStorage.getItem("name") or "Insira seu nome completo.",
    "email": window.localStorage.getItem("email") or "Insira seu endereço de e-mail",
    "foto": window.localStorage.getItem("foto") or "assets/avatar-padrao.svg",
}

video = document.getElementById("webcam")
canvas = document.createElement("canvas")
foto = document.getElementById("foto-perfil")


# Preencher os campos com os dados existentes
def carregar_dados():
    document.getElementById("user-name").innerText = usuario_logado["name"]
    document.getElementById("name").value = usuario_logado["name"]


carregar_dados()


# Salvar alterações no formulário
@when("submit", "#form-perfil")
def salvar_dados(event):
    event.preventDefault()
    usuario_logado["name"] = document.getElementById("name").value

    # Atualiza no localStorage
    window.localStorage.setItem("name", usuario_logado["name"])

    carregar_dados()
    window.alert("Informações atualizadas com sucesso!")
    console.log("Dados do usuário atualizados:", usuario_logado)


# Ativa a câmera e mostra botão de capturar
@when("click", "#abrir-camera")
async def abrir_camera(event):
    try:
        constraints = to_js({"video": True})
        stream = await navigator.mediaDevices.getUserMedia(constraints)
        video.srcObject = stream
        video.classList.remove("hidden")
        document.getElementById("capturar-foto").classList.remove("hidden")
        console.log("📷 Webcam iniciada.")

    except Exception as e:
        window.alert("Erro ao acessar a câmera: " + str(e))
        console.log("Erro ao acessar a câmera:", str(e))


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
        console.log("Imagem capturada e salva no localStorage.")
        window.alert("Foto de perfil atualizada!")

    except Exception as e:
        window.alert("Erro ao capturar imagem: " + str(e))


@when("click", "#logout-btn")
def sair(_):
    window.sessionStorage.clear()
    window.location.href = "index.html"
