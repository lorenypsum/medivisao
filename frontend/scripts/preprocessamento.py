from js import document, window, console, fetch
from pyscript import when
from pyodide.ffi import to_js
import json

# Estado: imagem original + processadas
image_original = None
imagem_processada = None
processadas = {}  # chave: filtro, valor: base64

# Previsualização da imagem ao fazer upload
@when("change", "#upload")
def carregar_imagem(event):
    file = document.getElementById("upload").files[0]
    reader = window.FileReader.new()
    
    def onload(e):
        global image_original
        image_original = reader.result
        document.getElementById("preview-original").src = image_original
        window.localStorage.setItem("img_original", image_original)
        console.log("Imagem original carregada.")

    reader.onload = onload
    reader.readAsDataURL(file)

# Função genérica para aplicar filtros
async def aplicar_filtro(filtro):
    global imagem_processada
    if not image_original:
        window.alert("Selecione ou carregue uma imagem primeiro.")
        return
    
    try:
        payload = json.dumps({
            "image_base64": image_original,
            "method": filtro
        })

        response = await fetch(
            "http://localhost:8000/processar",
            method="POST",
            body=payload,
            headers=to_js({"Content-Type": "application/json"})
        )

        if response.ok:
            res = await response.json()
            imagem_processada = res["processed_image"]
            document.getElementById("preview-result").src = imagem_processada

            # Atualiza histórico de imagens processadas
            processadas[filtro] = imagem_processada
            window.localStorage.setItem(f"img_{filtro}", imagem_processada)

            # Atualiza seção dinâmica
            atualizar_galeria_processadas()

        else:
            window.alert(f"Erro ao aplicar {filtro}")
            console.log(await response.text())

    except Exception as e:
        window.alert(f"Erro ao processar imagem: {e}")
        console.log(e)

# Ações por filtro
@when("click", "#btn-resize")
def resize(e): asyncio.ensure_future(aplicar_filtro("resize"))

@when("click", "#btn-normalize")
def normalize(e): asyncio.ensure_future(aplicar_filtro("normalize"))

@when("click", "#btn-blur")
def blur(e): asyncio.ensure_future(aplicar_filtro("gaussian"))

@when("click", "#btn-clahe")
def clahe(e): asyncio.ensure_future(aplicar_filtro("clahe"))

@when("click", "#btn-otsu")
def otsu(e): asyncio.ensure_future(aplicar_filtro("otsu"))

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
        download.className = "bg-[#7DA584] text-white px-3 py-1 rounded mr-2 hover:bg-[#5b8f79]"
        download.onclick = lambda e, data=img, f=filtro: baixar_imagem(data, f)
        card.appendChild(download)

        # Botão de salvar na lista
        salvar = document.createElement("button")
        salvar.innerText = "💾 Salvar"
        salvar.className = "bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
        salvar.onclick = lambda e, f=filtro: salvar_imagem_local(f)
        card.appendChild(salvar)

        galeria.appendChild(card)

# Faz download
def baixar_imagem(data_url, nome):
    link = document.createElement("a")
    link.href = data_url
    link.download = f"{nome}.png"
    link.click()
    console.log("Imagem baixada:", nome)

# Salva a imagem no localStorage
def salvar_imagem_local(filtro):
    if filtro in processadas:
        window.localStorage.setItem(f"img_{filtro}", processadas[filtro])
        window.alert(f"Imagem '{filtro}' salva localmente!")
        console.log(f"Imagem '{filtro}' salva no localStorage.")
