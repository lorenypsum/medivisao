from js import document, navigator, console, window, fetch
from pyodide.ffi import to_js
from pyscript import when
import asyncio
import json
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

        if not usuario_id or not imagem:
            window.alert("Usuário não autenticado ou imagem não capturada!")
            return

        payload = to_js({
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
        })

        response = await fetch(
            "http://localhost:8000/imagens",
            method="POST",
            body=to_js(json.dumps(payload)),
            headers=to_js({"Content-Type": "application/json"})
        )
        
        if response.ok:
                result = await response.json()
                window.alert("Imagem salva com sucesso!")
                console.log("Imagem salva:", result)
                carregar_galeria()
        else:
                window.alert("Erro ao salvar imagem")
                console.log("Erro:", response.status)        

        js.fetch("/api/imagens", {
            "method": "POST",
            "body": window.JSON.stringify(payload),
            "headers": to_js({"Content-Type": "application/json"})
        }).then(lambda r: carregar_galeria())

    except Exception as e:
        window.alert(f"Erro ao salvar imagem: {e}")
        console.log("Erro ao salvar imagem:", e)    

# Carrega imagens do backend
def carregar_galeria():
    try: 
        js.fetch(f"/api/imagens?usuario={usuario}")\
            .then(lambda r: r.json())\
            .then(mostrar_imagens)
    except Exception as e:
        window.alert(f"Erro ao carregar imagens: {e}")
        console.log("Erro ao carregar imagens:", e)    

def mostrar_imagens(imagens):
    try:    
        galeria = document.getElementById("galeria-imagens")
        galeria.innerHTML = ""

        for img in imagens:
            container = document.createElement("div")
            container.className = "relative mb-4"

            imagem = document.createElement("img")
            imagem.src = img["imagem"]  # caminho base64 ou URL da imagem
            imagem.className = "rounded border w-full"

            botao = document.createElement("button")
            botao.innerText = "🗑"
            botao.className = "absolute top-1 right-1 bg-red-500 text-white px-2 py-1 rounded"
            botao.onclick = lambda e, id=img["id"]: deletar_imagem(id)

            container.appendChild(imagem)
            container.appendChild(botao)
            galeria.appendChild(container)  
            window.alert("Imagens carregadas com sucesso!")
            console.log("Imagens carregadas:", img)

    except Exception as e:
        window.alert(f"Erro ao mostrar imagens: {e}")
        console.log("Erro ao mostrar imagens:", e)        


# Deletar imagem do backend
def deletar_imagem(id):
    try:
        js.fetch(f"/api/imagens/{id}", {
            "method": "DELETE"
        }).then(lambda r: carregar_galeria())  
    except Exception as e:
        window.alert(f"Erro ao deletar imagem: {e}")
        console.log("Erro ao deletar imagem:", e)      

@when("click", "#logout-btn")
def sair(_):
    window.sessionStorage.clear()
    window.location.href = "index.html"

# Carrega imagens ao abrir página
carregar_galeria()