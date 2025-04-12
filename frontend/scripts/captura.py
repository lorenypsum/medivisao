from js import document, navigator, console, window
from pyscript import when
import asyncio
from pyodide.ffi import to_js
import js

video = document.getElementById("webcam")
canvas = document.createElement("canvas")
usuario = window.sessionStorage.getItem("usuario") or "anonimo"

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

        salvar_no_computador(image_data)
        salvar_no_backend(image_data)

        window.alert("Imagem capturada com sucesso!")
        console.log("Imagem capturada e salva no back-end.")

        # Desliga a câmera
        stream = video.srcObject
        if stream:
            stream.getTracks()[0].stop()
        video.classList.add("hidden")
        document.getElementById("capturar-foto").classList.add("hidden")
        console.log("Webcam desligada.")
        

    except Exception as e:
        window.alert("Erro ao capturar imagem: " + str(e))

# Salvar como download local
def salvar_no_computador(image_data):
    link = document.createElement("a")
    link.href = image_data
    link.download = f"imagem_{usuario}.png"
    link.click()
    console.log("💾 Imagem baixada")

# Enviar para o backend
def salvar_no_backend(image_data):
    payload = to_js({
        "usuario": usuario,
        "imagem": image_data
    })
    js.fetch("/api/imagens", {
        "method": "POST",
        "body": window.JSON.stringify(payload),
        "headers": to_js({"Content-Type": "application/json"})
    }).then(lambda r: carregar_galeria())

# Carrega imagens do backend
def carregar_galeria():
    js.fetch(f"/api/imagens?usuario={usuario}")\
        .then(lambda r: r.json())\
        .then(mostrar_imagens)

def mostrar_imagens(imagens):
    galeria = document.getElementById("galeria-imagens")
    galeria.innerHTML = ""
    for img in imagens:
        container = document.createElement("div")
        container.className = "relative"

        imagem = document.createElement("img")
        imagem.src = img["imagem"]
        imagem.className = "rounded border w-full"

        botao = document.createElement("button")
        botao.innerText = "🗑"
        botao.className = "absolute top-1 right-1 bg-red-500 text-white px-2 py-1 rounded"
        botao.onclick = lambda e, id=img["id"]: deletar_imagem(id)

        container.appendChild(imagem)
        container.appendChild(botao)
        galeria.appendChild(container)

# Deletar imagem do backend
def deletar_imagem(id):
    js.fetch(f"/api/imagens/{id}", {
        "method": "DELETE"
    }).then(lambda r: carregar_galeria())    

@when("click", "#logout-btn")
def sair(_):
    window.sessionStorage.clear()
    window.location.href = "index.html"

# Carrega imagens ao abrir página
carregar_galeria()