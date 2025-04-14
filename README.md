# Medivisão

Projeto dedicado à detecção precoce de câncer de pele utilizando técnicas de processamento digital de imagens e interface com foco em interação-humano-computacional.

**Github Pages:** [Web Aplicação Medivisão](https://lorenypsum.github.io/medivisao/)

Para acessar a aplicação realize o cadastro em:

**Tela de Cadastro:** [Web Aplicação Medivisão](https://lorenypsum.github.io/medivisao/)

Alternativamente para fins de teste utilize as credenciais abaixo:

**Usuário:** `b`

**Senha:** `b`

## Identificação:

**Equipe:** 1

**Membros:**

Lorena Silva Sampaio - 11201212025
Samira Haddad - 11201812350
Larissa Rodrigues de Almeida - 11201812076
William Fernandes Dias - 11202020043

**Título:** Medivisão - Auxílio ao Diagnóstico de Câncer de Pele

**Data de Publicação::** 13 de Abril de 2025

## Descrição do Projeto:

Este repositório contém o código e a documentação de um projeto dedicado à detecção precoce de câncer de pele. O projeto explora o uso de técnicas de Processamento Digital de Imagens (PDI) para o tratamento e análise de imagens de lesões cutâneas, com o objetivo de auxiliar na identificação de padrões sugestivos de malignidade.

O avanço da inteligência artificial tem o potencial de transformar a área da saúde, especialmente em um cenário com limitações de acesso a especialistas médicos. A detecção precoce de doenças como o câncer de pele é crucial para aumentar as chances de tratamento bem-sucedido.

Este projeto se concentra no pré-processamento das imagens de pele utilizando os fundamentos do Processamento Digital de Imagens (PDI). O objetivo é preparar as imagens para análises subsequentes, que podem incluir técnicas de aprendizado de máquina, como redes neurais. 

Redes neurais profundas têm demonstrado grande potencial na análise de imagens médicas, sendo capazes de aprender padrões complexos e realizar classificações precisas. No contexto deste projeto, após o pré-processamento das imagens, modelos de redes neurais são treinados para identificar características visuais indicativas de câncer de pele.

As etapas de pré-processamento com PDI visam otimizar a qualidade das imagens e realçar informações relevantes para a detecção, incluindo:

**Tratamento de ruídos:** Redução de artefatos para melhorar a clareza das imagens.

**Filtragem e Convolução:** Aplicação de filtros para destacar bordas e texturas importantes das lesões.

**Realce e Restauração:** Melhoria do contraste e da nitidez para facilitar a visualização de detalhes.

**Ajuste de Histograma:** Otimização da distribuição de cores para melhor análise visual.

**Segmentação:** Isolamento da área da lesão para análise focada.

Embora a implementação de modelos de redes neurais para a classificação final das lesões possa ser um objetivo futuro, o foco inicial deste repositório é demonstrar como as técnicas de processamento digital de imagens podem ser aplicadas para eficazmente em imagens de câncer de pele, preparando-as para uma análise mais aprofundada com inteligência artificial. 

Em resumo, este projeto busca contribuir para o desenvolvimento de ferramentas que auxiliem no diagnóstico precoce, potencialmente melhorando o acesso e a precisão na detecção do câncer de pele.

## Como rodar localmente:

### Clonar o Repositório:
Para clonar o repositório, rode os seguintes comandos no terminal:

```bash 
git clone https://github.com/lorenypsum/medivisao
```

### Instalar os Requerimentos:

```bash
python3 -m venv venv_tf
source venv_tf/bin/activate
pip install -r requirements.txt

```

### Rodar o Servidor:

```bash
main:app --app-dir backend
```

### Visualizar no Browser:

Para visualizar a aplicaçao no browser, você precisa abrir o arquivo `index.html` no seu navegador. Você pode fazer isso de várias maneiras:

1. **Abrir o arquivo diretamente**: Navegue até o diretório onde `index.html` está localizado e clique duas vezes nele. Isso deve abrir o arquivo no seu navegador padrão.
    Alternativamente, você pode clicar com o botão direito do mouse no arquivo e selecionar "Abrir com" e escolher seu navegador preferido.
    
**Nota**: Alguns navegadores podem bloquear o acesso a arquivos locais por motivos de segurança. 
    
Se você encontrar problemas, tente um dos seguintes métodos:
    - Use um navegador diferente (por exemplo, Chrome, Firefox).
    - Use um servidor local (veja abaixo).
    - Desative as configurações de segurança no seu navegador (não recomendado por motivos de segurança).
  
2. **Usar um editor de código**: Se você estiver usando um editor de código como o Visual Studio Code, pode usar a extensão Live Server para abrir o arquivo no seu navegador. Basta clicar com o botão direito do mouse no arquivo `index.html` e selecionar "Abrir com Live Server".

Isso iniciará um servidor local e abrirá o arquivo no seu navegador padrão.
     
**Nota**: Você pode precisar instalar a extensão Live Server se ainda não o fez.
    
Você pode instalá-lo no Marketplace de Extensões do Visual Studio Code.

3. **Usar um servidor local**: Se você tiver o Python instalado, pode usar o servidor HTTP embutido para servir o arquivo. Abra um terminal, navegue até o diretório onde `index.html` está localizado e execute:
   
```bash
python -m http.server
```
   Em seguida, abra seu navegador e vá para `http://localhost:8000/index.html`.

### Acessar a Aplicação:

A aplicação é acessada através do arquivo `index.html`. Você pode abrir esse arquivo diretamente no seu navegador ou usar um servidor local, como mencionado acima.

Dentro do arquivo `index.html`, você encontrará um formulário de login. Para acessar a aplicação, insira as seguintes credenciais:

**Usuário:** `b`

**Senha:** `b`

Após fazer login, você será redirecionado para a página principal da aplicação, onde poderá interagir com as funcionalidades disponíveis.

Uma tela de cadastro também está disponível, onde você pode criar uma nova conta. Para isso, clique no botão "Cadastrar" na tela de login. Você será redirecionado para a página de cadastro, onde poderá inserir suas informações pessoais.

Após preencher o formulário de cadastro, clique no botão "Cadastrar" para criar sua conta. Você será redirecionado para a página de login, onde poderá usar suas novas credenciais para acessar a aplicação.

### Funcionalidades da Aplicação:

1. Página Inicial:
   - A página inicial apresenta uma breve descrição do projeto e suas funcionalidades.
   - Você pode navegar pelas diferentes seções da aplicação a partir do menu de navegação.
  
2. Perfil:
   - A seção de perfil permite que você visualize e edite suas informações pessoais.
   - Você pode atualizar seu nome, e-mail e outras informações relevantes.
  
3. Captura e Upload de Imagens:
   - A seção de captura e upload de imagens permite que você tire fotos diretamente da câmera do seu dispositivo ou faça upload de imagens existentes.
   - Faça upload de imagens da pele para análise, você também pode selecionar uma imagem do seu dispositivo e enviá-la para a aplicação.
  
4. Análise de Imagens:
   - A seção de análise de imagens permite que você visualize os resultados da análise das imagens enviadas.
   - Você pode ver os resultados da detecção de câncer de pele e outras informações relevantes.
  
5. Processamento:
   - A seção de processamento permite que você visualize o processamento das imagens enviadas.
   - Você pode ver os resultados do processamento de imagem, como segmentação e extração de características.
  
6. Histórico:
   - A seção de histórico permite que você visualize o histórico de análises realizadas.
   - Você pode ver as imagens enviadas anteriormente e os resultados correspondentes.  