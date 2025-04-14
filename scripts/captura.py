from js import document, navigator, console, window, fetch
from pyodide.ffi import to_js
from pyscript import when
import asyncio
import json
import js
import os

# Update base URL dynamically based on environment
BASE_URL = (
    "https://generous-unduly-thrush.ngrok-free.app"
    if "https" in window.location.href
    else "http://localhost:8000"
)

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

        # Mostrar botão de download
        document.getElementById("download").classList.remove("hidden")
        # Mostrar botão de salvar
        document.getElementById("save_backend").classList.remove("hidden")

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
        console.log("Erro ao capturar imagem:", e)


# Salvar como download local
@when("click", "#download")
def download(image_data):
    try:
        link = document.createElement("a")
        link.href = image_data
        link.download = f"imagem_{usuario}.png"
        link.click()
        console.log("💾 Imagem baixada")
    except Exception as e:
        window.alert(f"Erro ao baixar imagem: {e}")
        console.log("Erro ao baixar imagem:", e)


# Enviar para o backend
@when("click", "#save_backend")
async def save(image_data):
    try:
        usuario_id = window.sessionStorage.getItem("usuario_id")
        imagem = window.localStorage.getItem("foto")

        if not usuario_id:
            usuario_id = "123"  # ID padrão para teste
        elif not imagem:
            window.alert("Usuário não autenticado ou imagem não capturada!")
            return

        payload = {
            "usuario_id": usuario_id,
            "original": imagem,
            "resize": None,
            "normalize": None,
            "gaussian": None,
            "clahe": None,
            "otsu": None,
            "resultado_final": None,
            "diagnostico": None,
            "probabilidade": None,
            "metadados": None,
        }

        # Conversão para JSON string
        body_json = json.dumps(payload)

        response = await fetch(
            f"{BASE_URL}/imagens",
            method="POST",
            body=body_json,
            headers=to_js({"Content-Type": "application/json"}),
        )

        if response.ok:
            result = await response.json()
            window.alert("Imagem salva com sucesso!")
            console.log("Imagem salva:", result)
        else:
            window.alert("Erro ao salvar imagem")
            console.log("Erro:", response.status)

        await fetch(
            "/api/imagens",
            {
                "method": "POST",
                "body": window.JSON.stringify(payload),
                "headers": to_js({"Content-Type": "application/json"}),
            },
        )
        await carregar_galeria()

    except Exception as e:
        window.alert(f"Erro ao salvar imagem: {e}")
        console.log("Erro ao salvar imagem:", e)


# Carrega imagens do backend
async def carregar_imagem():
    usuario_id = window.sessionStorage.getItem("usuario_id")
    if not usuario_id:
        console.warn("Usuário não autenticado.")
        return
    try:
        r = await js.fetch(f"{BASE_URL}/usuarios/{usuario_id}/imagens")
        mostrar_imagem(await r.json())
    except Exception as e:
        window.alert(f"Erro ao carregar imagens: {e}")
        console.log("Erro ao carregar imagens:", e)


def mostrar_imagem(js_imagem):
    try:
        imagem = js_imagem.to_py()
        preview = document.getElementById("preview")
        preview.src = imagem.get("original")
        console.log("Imagem carregada:", imagem)
    except Exception as e:
        console.log("❌ Erro ao mostrar imagem:", e)


# Carrega imagens do backend
async def carregar_galeria():
    usuario_id = window.sessionStorage.getItem("usuario_id")
    if not usuario_id:
        usuario_id = "123"  # ID padrão para teste
        console.log("❗ Usuário não autenticado")
    try:
        r = await js.fetch(f"{BASE_URL}/usuarios/{usuario_id}/imagens")
        mostrar_imagens(await r.json())
    except Exception as e:
        window.alert(f"Erro ao carregar imagens: {e}")
        console.log("Erro ao carregar imagens:", e)


def mostrar_imagens(js_imagens):
    try:
        imagens = js_imagens.to_py()
        if not imagens:
            console.log("Nenhuma imagem encontrada.")

        galeria = document.getElementById("galeria-imagens")
        galeria.innerHTML = ""

        for img in imagens:
            container = document.createElement("div")
            container.className = "relative mb-4"

            imagem = document.createElement("img")
            imagem.src = img.get("original")  # caminho base64 ou URL da imagem
            imagem.className = "rounded border w-full"

            botao = document.createElement("button")
            botao.innerText = "X"
            botao.className = (
                "absolute top-1 right-1 bg-red-500 text-white px-2 py-1 rounded"
            )

            id = img.get("id")
            botao.onclick = lambda _: asyncio.get_event_loop().run_until_complete(
                deletar_imagem(id)
            )
            container.appendChild(imagem)
            container.appendChild(botao)
            galeria.appendChild(container)
            console.log("Imagens carregadas:", img)

    except Exception as e:
        window.alert(f"Erro ao mostrar imagens: {e}")
        console.log("Erro ao mostrar imagens:", e)


# Deletar imagem do backend
async def deletar_imagem(id):
    try:
        await fetch(f"{BASE_URL}/imagens/{id}", to_js({"method": "DELETE"}))
        await carregar_galeria()
    except Exception as e:
        window.alert(f"Erro ao deletar imagem: {e}")
        console.log("Erro ao deletar imagem:", e)


@when("click", "#logout-btn")
def sair(_):
    window.sessionStorage.clear()
    window.location.href = "index.html"


asyncio.get_event_loop().run_until_complete(carregar_galeria())
