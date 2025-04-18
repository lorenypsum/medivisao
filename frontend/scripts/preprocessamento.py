from js import document, window, console, fetch, FileReader
from pyscript import when
from pyodide.ffi import to_js
import json
import asyncio
import os

# Update base URL dynamically based on environment
BASE_URL = (
    "https://generous-unduly-thrush.ngrok-free.app"
    if "https" in window.location.href
    else "http://localhost:8000"
)

video = document.getElementById("webcam")
canvas = document.createElement("canvas")

# Estado: imagem original + processadas
processadas = {}  # chave: filtro, valor: base64
image_original = None


# Ativar câmera
@when("click", "#abrir-camera")
async def abrir_camera(event):
    try:
        stream = await window.navigator.mediaDevices.getUserMedia(
            to_js({"video": True})
        )
        video.srcObject = stream
        video.classList.remove("hidden")
        document.getElementById("capturar-foto").classList.remove("hidden")
    except Exception as e:
        window.alert(f"Erro ao acessar a câmera: {e}")
        console.log(e)

# Capturar foto
@when("click", "#capturar-foto")
def capturar_foto(event):
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    ctx = canvas.getContext("2d")
    ctx.drawImage(video, 0, 0)

    image_data = canvas.toDataURL("image/jpeg")
    document.getElementById("preview").src = image_data
    window.localStorage.setItem("captura", image_data)

    # Mostrar botões
    document.getElementById("carregar-imagem").classList.remove("hidden")

    # Desligar câmera
    stream = video.srcObject
    if stream:
        stream.getTracks()[0].stop()
    video.classList.add("hidden")
    document.getElementById("capturar-foto").classList.add("hidden")

# Previsualização da imagem ao fazer upload
@when("click", "#carregar-imagem")
def carregar_imagem2(event):
    asyncio.get_event_loop().run_until_complete(carregar_imagem(event))

async def carregar_imagem(event):
    event.preventDefault()
    global image_original
    try:
        image_data = window.localStorage.getItem("captura")
        if not image_data:
            window.alert("Nenhuma imagem capturada.")
            return

        #async def on_load():
        data_url = image_data
        document.getElementById("preview-original").src = data_url
        image_original = data_url
        console.log("🖼️ Imagem carregada.")

        # Salvar no banco
        usuario_id = window.sessionStorage.getItem("usuario_id") or "123"
        payload = {
            "usuario_id": usuario_id,
            "original": data_url,
            "histogram": None,
            "resize": None,
            "normalize": None,
            "gaussian": None,
            "clahe": None,
            "otsu": None,
            "morphological": None,
            "edgedetection": None,
            "watershed": None,
            "resultado_final": None,
            "diagnostico": None,
            "probabilidade": None,
            "metadados": None,
        }

        body = json.dumps(payload)
        r = await fetch(
            f"{BASE_URL}/imagens",
            to_js(
                {
                    "method": "POST",
                    "body": body,
                    "headers": {"Content-Type": "application/json"},
                }
            ),
        )
        console.log("🗃️ Imagem salva:", await r.json())

        # reader.onload = lambda _: asyncio.get_event_loop().run_until_complete(on_load())
        # reader.readAsDataURL(file)

    except Exception as e:
        window.alert(f"Erro ao carregar imagem: {e}")
        console.log(f"❌ Erro ao carregar e salvar imagem: {e}")


# Função genérica para aplicar filtros
async def aplicar_filtro(filtro, append_after_id):
    global imagem_processada, processadas
    if not image_original:
        window.alert("Carregue uma imagem primeiro.")
        return

    try:
        payload = json.dumps({"image_base64": image_original, "method": filtro})

        response = await fetch(
            f"{BASE_URL}/processar",
            method="POST",
            body=payload,
            headers=to_js({"Content-Type": "application/json"}),
        )

        if response.ok:
            res = (await response.json()).to_py()
            imagem_processada = res["processed_image"]

            # Store the processed image in the global dictionary
            processadas[filtro] = imagem_processada

            # Add the processed image below the corresponding button
            button = document.querySelector(append_after_id)
            if button:
                # Criar container para imagem + botão
                container = document.createElement("div")
                container.className = "mb-6 text-center"

                # Criar imagem
                imagem = document.createElement("img")
                imagem.src = imagem_processada
                imagem.className = "w-full h-40 object-contain border mb-2"
                container.appendChild(imagem)

                # Criar botão
                download = document.createElement("button")
                download.innerText = "📥 Download"
                download.className = (
                    "bg-[#7DA584] text-white px-3 py-1 rounded hover:bg-[#5b8f79]"
                )
                download.onclick = lambda e, data=imagem_processada, f=filtro: baixar_imagem(data, f)
                container.appendChild(download)

                # Inserir bloco após o botão correspondente
                button.parentNode.insertBefore(container, button.nextSibling)

        else:
            window.alert(f"Erro ao aplicar {filtro}")
            console.log(await response.text())

    except Exception as e:
        window.alert(f"Erro ao processar imagem: {e}")
        console.log(e)


# Ações por filtro
@when("click", "#btn-resize")
async def resize(e):
    await aplicar_filtro("resize", "#btn-resize")


# Ações por filtro
@when("click", "#btn-histogram")
async def histogram(e):
    await aplicar_filtro("histogram", "#btn-histogram")


@when("click", "#btn-normalize")
async def normalize(e):
    await aplicar_filtro("normalize", "#btn-normalize")


@when("click", "#btn-blur")
async def blur(e):
    await aplicar_filtro("gaussian", "#btn-blur")


@when("click", "#btn-clahe")
async def clahe(e):
    await aplicar_filtro("clahe", "#btn-clahe")


@when("click", "#btn-otsu")
async def otsu(e):
    await aplicar_filtro("otsu", "#btn-otsu")


@when("click", "#btn-morphological")
async def morphological(e):
    await aplicar_filtro("morphological", "#btn-morphological")


@when("click", "#btn-edge")
async def edge(e):
    await aplicar_filtro("edge", "#btn-edge")


@when("click", "#btn-watershed")
async def watershed(e):
    await aplicar_filtro("watershed", "#btn-watershed")


# Gera galeria de imagens processadas com botão de download e salvar
def atualizar_galeria_processadas():
    galeria = document.getElementById("processadas")
    galeria.innerHTML = ""

    for filtro, img in processadas.items():
        card = document.createElement("div")
        card.className = "border rounded p-2 shadow w-64 text-center bg-white"

        titulo = document.createElement("h4")
        titulo.innerText = filtro.capitalize()
        titulo.className = "text-lg font-semibold mb-2 text-[#5b8f79]"
        card.appendChild(titulo)

        imagem = document.createElement("img")
        imagem.src = img
        imagem.className = "w-full h-40 object-contain mb-2 border"
        card.appendChild(imagem)

        # Botão de download
        download = document.createElement("button")
        download.innerText = "📥 Download"
        download.className = (
            "bg-[#7DA584] text-white px-3 py-1 rounded mr-2 hover:bg-[#5b8f79]"
        )
        download.onclick = lambda e, data=img, f=filtro: baixar_imagem(data, f)
        card.appendChild(download)

        # Botão de salvar na lista
        salvar = document.createElement("button")
        salvar.innerText = "💾 Salvar"
        salvar.className = "bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
        card.appendChild(salvar)

        galeria.appendChild(card)


# Faz download
def baixar_imagem(data_url, name):
    link = document.createElement("a")
    link.href = data_url
    link.download = f"{name}.png"
    link.click()
    console.log("Imagem baixada:", name)


@when("click", "#btn-salvar-tudo")
async def salvar_todas_no_banco(event):
    try:
        if not image_original:
            window.alert("Você precisa carregar uma imagem primeiro.")
            return

        usuario_id = window.sessionStorage.getItem("usuario_id") or "123"

        payload = {
            "usuario_id": usuario_id,
            "original": image_original,
            "resize": processadas.get("resize"),
            "histogram": processadas.get("histogram"),
            "normalize": processadas.get("normalize"),
            "gaussian": processadas.get("gaussian"),
            "clahe": processadas.get("clahe"),
            "otsu": processadas.get("otsu"),
            "morphological": processadas.get("morphological"),
            "edgedetection": processadas.get("edge"),
            "watershed": processadas.get("watershed"),
            "resultado_final": None,
            "diagnostico": None,
            "probabilidade": None,
            "metadados": None,
        }

        response = await fetch(
            f"{BASE_URL}/imagens",
            method="POST",
            body=json.dumps(payload),
            headers=to_js({"Content-Type": "application/json"}),
        )

        if response.ok:
            window.alert("Imagens salvas no banco com sucesso!")
            console.log("🧠 Imagens salvas:", await response.json())
            await atualizar_galeria_processadas_backend()
        else:
            console.log("❌ Erro ao salvar:", await response.text())
            window.alert("Erro ao salvar imagens no banco.")
    except Exception as e:
        console.log("❌ Exceção ao salvar todas:", e)
        window.alert(f"Erro ao salvar imagens: {e}")


async def atualizar_galeria_processadas_backend():
    try:
        usuario_id = window.sessionStorage.getItem("usuario_id") or "123"
        response = await fetch(f"{BASE_URL}/usuarios/{usuario_id}/imagem")
        if response.ok:
            imagem_obj = await response.json()
            mostrar_resultado_backend(imagem_obj)
        else:
            console.log("❌ Erro ao buscar imagem:", await response.text())
    except Exception as e:
        console.log("❌ Erro ao buscar imagem do banco:", e)


def mostrar_resultado_backend(imagem_obj):
    galeria = document.getElementById("processadas")
    galeria.innerHTML = ""

    filtros = [
        "original",
        "resize",
        "histogram",
        "normalize",
        "gaussian",
        "clahe",
        "otsu",
        "morphological",
        "edgedetection",
    ]

    for filtro in filtros:
        base64img = imagem_obj.get(filtro)
        if base64img:
            card = document.createElement("div")
            card.className = "border rounded p-2 shadow w-64 text-center bg-white"

            titulo = document.createElement("h4")
            titulo.innerText = filtro.capitalize()
            titulo.className = "text-lg font-semibold mb-2 text-[#5b8f79]"
            card.appendChild(titulo)

            imagem = document.createElement("img")
            imagem.src = base64img
            imagem.className = "w-full h-40 object-contain mb-2 border"
            card.appendChild(imagem)

            galeria.appendChild(card)
    console.log("🖼️ Galeria atualizada com imagens do banco.")
