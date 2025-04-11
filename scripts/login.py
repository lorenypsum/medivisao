from js import document, window
from pyscript import when

usuarios = {
    "medico": {"senha": "111", "perfil": "médico"},
    "a": {"senha": "a", "perfil": "médico"},
    "enfermeiro": {"senha": "111", "perfil": "enfermeiro"},
    "paciente": {"senha": "111", "perfil": "paciente"},
    "admin": {"senha": "111", "perfil": "administrador"},
}

@when("click", "#login-btn")
def fazer_login(event):
    usuario = document.getElementById("usuario").value
    senha = document.getElementById("senha").value

    if usuario in usuarios and usuarios[usuario]["senha"] == senha:
        perfil = usuarios[usuario]["perfil"]
        window.sessionStorage.setItem("usuario", usuario)
        window.sessionStorage.setItem("perfil", perfil)
        window.location.href = "home.html"
        window.alert(f"Login realizado com sucesso como: {perfil}.")
    elif not usuario:
        window.alert("Preencha o campo usuário.")
    elif not senha:
        window.alert("Preencha o campo senha.")    
    else:
        window.alert("Usuário ou senha incorretos.")
