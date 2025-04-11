from js import document, navigator, console, window
from pyscript import when
import asyncio
from pyodide.ffi import to_js

video = document.getElementById("webcam")
canvas = document.createElement("canvas")

# Inicializa webcam assim que a página carrega
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
        window.localStorage.setItem("foto", image_data)
        document.getElementById("preview").src = image_data
        window.alert("Imagem capturada com sucesso!")
        console.log("Imagem capturada e salva no localStorage.")

        # Desliga a câmera
        stream = video.srcObject
        if stream:
            stream.getTracks()[0].stop()
        video.classList.add("hidden")
        document.getElementById("capturar-foto").classList.add("hidden")
        console.log("Webcam desligada.")
        

    except Exception as e:
        window.alert("Erro ao capturar imagem: " + str(e))

@when("click", "#logout-btn")
def sair(_):
    window.sessionStorage.clear()
    window.location.href = "index.html"
