from js import document, window, console, fetch
from pyodide.ffi import to_js
from pyscript import when
import json

video = document.getElementById("webcam")
canvas = document.createElement("canvas")


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
        # Converte a imagem capturada para base64
        image_data = window.localStorage.getItem("captura")
        if not image_data:
            window.alert("Nenhuma imagem capturada.")
            return

        payload = {"image_base64": image_data}

        response = await fetch(
            "http://localhost:8000/analisar-imagem",
            method="POST",
            body=json.dumps(payload),
            headers=to_js({"Content-Type": "application/json"}),
        )

        if response.ok:
            result = (await response.json()).to_py()

            # Atualiza galeria
            document.getElementById("resultado").classList.remove("hidden")
            document.getElementById("resultado-texto").innerText = (
                f"Diagnóstico: {result['diagnostico'].capitalize()} "
                f"({round(result['probabilidade']*100, 2)}%)"
            )

            document.getElementById("saliency-img").src = result["resultado_final"]

            # Salva temporariamente no localStorage
            window.localStorage.setItem("saliency_image", result["resultado_final"])
            window.localStorage.setItem("diagnostico", result["diagnostico"])
            window.localStorage.setItem("probabilidade", result["probabilidade"])
            window.alert("sucesso")

        else:
            window.alert("Erro na análise: " + await response.text())

    except Exception as e:
        print(e)
        window.alert(f"Erro ao enviar para análise: {e}")


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
            "edgedetection": None,
        }

        response = await fetch(
            "http://localhost:8000/imagens",
            method="POST",
            body=json.dumps(payload),
            headers=to_js({"Content-Type": "application/json"}),
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
