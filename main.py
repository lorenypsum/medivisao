from js import Blob, URL, document, alert
from pyscript import when, display
import json

def log_in_box(msg: str):
    log_box = document.getElementById("log-output")
    log_box.value += msg + "\n"
    log_box.scrollTop = log_box.scrollHeight

@when("click", "#run-algorithm")
def run_algorithm(event):
    global G
    print("Imagem Capturada")
    log_in_box("Execução concluída com sucesso.")