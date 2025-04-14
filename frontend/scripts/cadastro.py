from js import document, window
from pyscript import when
from pyodide.ffi import to_js


@when("click", "#cadastro-btn")
async def fazer_cadastro(event):
    usuario = document.getElementById("usuario").value
    senha = document.getElementById("senha").value

    if not usuario:
        window.alert("Preencha o campo usuário.")
        return

    if not senha:
        window.alert("Preencha o campo senha.")
        return

    try:
        response = await window.fetch(
            "http://127.0.0.1:8000/cadastro",
            to_js(
                {
                    "method": "POST",
                    "headers": {"Content-Type": "application/x-www-form-urlencoded"},
                    "body": f"username={usuario}&password={senha}",
                }
            ),
        )

        if response.status == 200:
            data = (await response.json()).to_py()
            window.sessionStorage.setItem("usuario", data["usuario"])
            window.sessionStorage.setItem("name", data["name"])
            window.sessionStorage.setItem("usuario_id", data["id"])
            window.location.href = "home.html"
        elif response.status == 400:
            window.alert("Preencha todos os campos corretamente.")
        elif response.status == 401:
            window.alert("Usuário ou senha incorretos.")
        else:
            window.alert("Erro desconhecido. Tente novamente mais tarde.")

    except Exception as e:
        window.alert(f"Erro ao conectar ao servidor: {e}")
