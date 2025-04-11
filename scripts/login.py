from js import document, window
from pyscript import when

usuarios = {
    "medico": {"senha": "111", "perfil": "médico", "nome": "Dra. Helena"},
    "a": {"senha": "a", "perfil": "médico", "nome": "Dr. Xavier"},
    "enfermeiro": {"senha": "111", "perfil": "enfermeiro", "nome": "Maria"},
    "paciente": {"senha": "111", "perfil": "paciente", "nome": "Carlos"},
    "admin": {"senha": "111", "perfil": "administrador", "nome": "Ana"},
}

@when("click", "#login-btn")
def fazer_login(event):
    usuario = document.getElementById("usuario").value
    senha = document.getElementById("senha").value

    # Verifica se o usuário e senha estão corretos
    if usuario in usuarios and usuarios[usuario]["senha"] == senha:
        perfil = usuarios[usuario]["perfil"]
        nome = usuarios[usuario]["nome"]
        window.sessionStorage.setItem("usuario", usuario)
        window.sessionStorage.setItem("perfil", perfil)
        window.sessionStorage.setItem("nome", nome)
        window.location.href = "home.html"
        window.alert(f"Login realizado com sucesso como: {perfil}.")
    elif not usuario:
        window.alert("Preencha o campo usuário.")
    elif not senha:
        window.alert("Preencha o campo senha.")    
    else:
        window.alert("Usuário ou senha incorretos.")
