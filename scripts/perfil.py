from js import document, navigator, console
from pyscript import when

# Simulação de dados de usuário
usuario_logado = {
    "nome": "Xavier Batista Fernandes",
    "email": "xavier.batista@medivisao.com",
    "perfil": "médico",
}

# Preencher os campos com os dados existentes
def carregar_dados():
    document.getElementById("user-nome").innerText = usuario_logado["nome"]
    document.getElementById("user-perfil").innerText = usuario_logado["perfil"]
    document.getElementById("nome").value = usuario_logado["nome"]
    document.getElementById("email").value = usuario_logado["email"]
    document.getElementById("perfil").value = usuario_logado["perfil"]

carregar_dados()

# Salvar alterações no formulário
@when("submit", "#form-perfil")
def salvar_dados(event):
    event.preventDefault()
    usuario_logado["nome"] = document.getElementById("nome").value
    usuario_logado["email"] = document.getElementById("email").value
    usuario_logado["perfil"] = document.getElementById("perfil").value

    carregar_dados()
    console.log("Dados atualizados:", usuario_logado)
    alert("Informações atualizadas com sucesso!")

# Tirar foto da webcam e atualizar imagem de perfil
@when("click", "#capturar-foto")
def capturar_foto(event):
    video = document.getElementById("webcam")
    foto = document.getElementById("foto-perfil")

    async def start_camera():
        try:
            stream = await navigator.mediaDevices.getUserMedia({"video": True})
            video.srcObject = stream
            video.classList.remove("hidden")
            await video.play()

            canvas = document.createElement("canvas")
            canvas.width = video.videoWidth
            canvas.height = video.videoHeight
            ctx = canvas.getContext("2d")
            ctx.drawImage(video, 0, 0)

            foto.src = canvas.toDataURL("image/png")
            stream.getTracks()[0].stop()
            video.classList.add("hidden")
        except Exception as e:
            alert("Erro ao acessar a câmera: " + str(e))

    start_camera()
