from js import document, window
from pyscript import when

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
