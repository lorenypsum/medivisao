import os
from js import document, window, console, fetch, FileReader
from pyodide.ffi import to_js
from pyscript import when
import asyncio
import json

# Update base URL dynamically based on environment
BASE_URL = (
    "https://generous-unduly-thrush.ngrok-free.app"
    if "https" in window.location.href
    else "http://localhost:8000"
)

video = document.getElementById("webcam")
canvas = document.createElement("canvas")


@when("click", "#analise")
async def submeter_para_analise(event):
    try:
        file_input = document.getElementById("upload")
        file = file_input.files.to_py().item(0)

        if not file:
            window.alert("Nenhum arquivo selecionado.")
            console.log("Nenhum arquivo selecionado.")
            return

        reader = FileReader.new()

        # Converte a imagem capturada para base64
        async def on_load():
            image_data = reader.result
            document.getElementById("preview").src = image_data
            if not image_data:
                window.alert("Nenhuma imagem submetida")
                return

            payload = {
                "image_base64": image_data,
                "usuario_id": window.sessionStorage.getItem("usuario_id") or "123",
            }

            response = await fetch(
                f"{BASE_URL}/analisar-imagem",
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
                window.alert("Análise finalizada com sucesso!")

            else:
                window.alert("Erro na análise: " + await response.text())
        
        reader.onload = lambda _: asyncio.get_event_loop().run_until_complete(on_load())
        reader.readAsDataURL(file)
                
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
            f"{BASE_URL}/imagens",
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
