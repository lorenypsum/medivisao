from js import document, window

def logout_user(event=None):
    window.localStorage.clear()  # ou limpe apenas a chave que usar
    window.location.href = "index.html"  # ou "login.html"

document.getElementById("logout-btn").addEventListener("click", logout_user)
