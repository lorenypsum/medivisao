import os
from js import document, window
from pyscript import when

# Update base URL dynamically based on environment
BASE_URL = (
    "https://73d4-2804-1b3-a781-4b29-8d0d-3782-26c9-6ad4.ngrok-free.app"
    if "https" in window.location.href
    else "http://localhost:8000"
)

if not window.sessionStorage.getItem("usuario_id"):
    window.location.href = "index.html"
# Mostra dados do usuário armazenados no login
usuario = window.sessionStorage.getItem("usuario_id")
name = window.sessionStorage.getItem("name")

document.getElementById("user-name").innerText = name


@when("click", "#logout-btn")
def sair(_):
    window.sessionStorage.clear()
    window.location.href = "index.html"
