from js import document, window, console, fetch
from pyodide.ffi import to_js
from pyscript import when
import base64
import json

video = document.getElementById("webcam")
canvas = document.createElement("canvas")

# Ativar câmera
@when("click", "#abrir-camera")
async def abrir_camera(event):
    try:
        stream = await window.navigator.mediaDevices.getUserMedia(to_js({"video": True}))
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
    document.getElementById("download").classList.remove("hidden")
    document.getElementById("analise").classList.remove("hidden")

    # Desligar câmera
    stream = video.srcObject
    if stream:
        stream.getTracks()[0].stop()
    video.classList.add("hidden")
    document.getElementById("capturar-foto").classList.add("hidden")

# Download local
@when("click", "#download")
def baixar_imagem(event):
    data = window.localStorage.getItem("captura")
    link = document.createElement("a")
    link.href = data
    link.download = "imagem_capturada.jpg"
    link.click()

# Submeter para análise (Flask)
@when("click", "#analise")
async def submeter_para_analise(event):
    try:
        image_data = window.localStorage.getItem("captura")
        if not image_data:
            window.alert("Nenhuma imagem capturada.")
            return

        # Converte base64 para blob (file-like object)
        base64_data = image_data.split(",")[1]
        blob = window.atob(base64_data)
        array = to_js([ord(c) for c in blob], dict_converter=window.Uint8Array)
        file = window.Blob.new([array], { "type": "image/jpeg" })

        form = window.FormData.new()
        form.append("file", file, "imagem.jpg")

        response = await fetch("http://localhost:5000/predict", {
            "method": "POST",
            "body": form
        })

        if response.ok:
            result = await response.json()

            # Atualiza galeria
            document.getElementById("resultado").classList.remove("hidden")
            document.getElementById("resultado-texto").innerText = (
                f"Diagnóstico: {result['prediction']['class'].capitalize()} "
                f"({round(result['prediction']['probability']*100, 2)}%)"
            )

            document.getElementById("saliency-img").src = f"data:image/jpeg;base64,{result['saliency_image']}"
            document.getElementById("preprocess-img").src = f"data:image/jpeg;base64,{result['preprocess_steps_image']}"

            # Salva temporariamente no localStorage
            window.localStorage.setItem("saliency_image", f"data:image/jpeg;base64,{result['saliency_image']}")
            window.localStorage.setItem("preprocess_image", f"data:image/jpeg;base64,{result['preprocess_steps_image']}")
            window.localStorage.setItem("diagnostico", result['prediction']['class'])
            window.localStorage.setItem("probabilidade", result['prediction']['probability'])

        else:
            window.alert("Erro na análise.")
            console.log(await response.text())

    except Exception as e:
        window.alert(f"Erro ao enviar para análise: {e}")
        console.log(e)

# Salvar no banco de dados (FastAPI)
@when("click", "#salvar-resultado")
async def salvar_resultado(event):
    try:
        usuario_id = window.sessionStorage.getItem("usuario_id") or "123"
        original = window.localStorage.getItem("captura")
        resultado_final = window.localStorage.getItem("saliency_image")
        metadados = window.localStorage.getItem("preprocess_image")
        diagnostico = window.localStorage.getItem("diagnostico")
        probabilidade = float(window.localStorage.getItem("probabilidade"))

        payload = {
            "usuario_id": usuario_id,
            "original": original,
            "resultado_final": resultado_final,
            "metadados": metadados,
            "diagnostico": diagnostico,
            "probabilidade": probabilidade,
            "resize": None,
            "normalize": None,
            "gaussian": None,
            "clahe": None,
            "otsu": None,
            "histogram": None,
            "morphological": None,
            "edgedetection": None
        }

        response = await fetch(
            "http://localhost:8000/imagens",
            method="POST",
            body=json.dumps(payload),
            headers=to_js({"Content-Type": "application/json"})
        )

        if response.ok:
            window.alert("Resultado salvo com sucesso!")
            console.log("Salvo:", await response.json())
        else:
            window.alert("Erro ao salvar resultado.")
            console.log(await response.text())

    except Exception as e:
        window.alert(f"Erro ao salvar no banco: {e}")
        console.log(e)
