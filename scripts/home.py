from js import document, window
from pyscript import when

# Mostra dados do usuário armazenados no login
usuario = window.sessionStorage.getItem("usuario")
perfil = window.sessionStorage.getItem("perfil")

if not usuario or not perfil:
    window.location.href = "login.html"

document.getElementById("user-nome").innerText = usuario
document.getElementById("user-perfil").innerText = perfil.capitalize()

@when("click", "#logout-btn")
def sair(_):
    window.sessionStorage.clear()
    window.location.href = "index.html"
