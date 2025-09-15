# Compilador de Livros
O **Compilador de Livros** é um aplicativo em Python com interface gráfica, desenvolvido para compilar, redimensionar e renomear arquivos de forma automática. É uma ferramenta útil aos que escaneiam e compilam livros para publicá-los na internet.

![Python](https://img.shields.io/badge/python-3.10+-blue)

---

## Funcionalidades

- **Compilação de arquivos**:
  Compila várias imagens, em qualquer formato, usando de ordem numérica, em um pdf com metadados.

- **Redimensionamento de arquivos**:
  Redimensiona os arquivos, convertendo-os para o formato .jpeg, usando os parâmetros dados pelo usuário. É útil para diminuir o peso das imagens, e, portanto, do pdf final.

- **Renomeação automática de arquivos**:
  Renomeia arquivos numericamente, respeitando a sequência e extensões originais.

---

## Como usar o Compilador

1. **Preencha os campos de diretório, que podem ser iguais**:

    ![Passo 1, coloque os diretórios](https://i.imgur.com/K7iWzUA.png)
    
2. **Preencha os campos de metadados (não obrigatórios)**:

    ![Passo 2, coloque os metadados](https://i.imgur.com/4ZYxJeD.png)

3. **Compile**:

    ![Passo 3, compile](https://i.imgur.com/wKnarjW.png)

---

## Como usar o Redimensionador

1. **Preencha os campos de diretório (diferentes)**:

    ![Passo 1, coloque os diretórios](https://i.imgur.com/L2LpVPF.png)
    
2. **Use os botões laterias para escolher os valores da redução e da qualidade**:

    ![Passo 2, escolha os parâmetros](https://i.imgur.com/AtLG0d1.png)

3. **Redimensione**:

    ![Passo 3, redimensione](https://i.imgur.com/JlpSCqi.png)

---

## Como usar o Renomeador

1. **Preencha os campos de diretório**:

    ![Passo 1, coloque os diretórios](https://i.imgur.com/Zgem1DA.png)
    
2. **Atenção ao aviso, caso queira usar o mesmo diretório de entrada para a saída**:

    ![Passo 2, coloque os metadados](https://i.imgur.com/Cvu9Btu.png)

3. **Coloque o número de onde o programa partirá**:

    ![Passo 3, coloque o número de partida](https://i.imgur.com/zK5wfbW.png)

4. **Renomeie**:

    ![Passo 4, renomeie](https://i.imgur.com/xT1IxL6.png)

---

## Estrutura do Projeto
```
compilador-de-livros/
│
├─ app.py # Script principal que inicializa a interface e chama os módulos
├─ assets/
│ ├─ icon.ico # Ícone em .ico, com vários tamanhos
│ └─ icone.png # Imagem original do ícone
├─ modulos/
│ ├─ init.py # Inicializa o pacote de módulos
│ ├─ compilador.py # Lógica de compilação dos arquivos
│ ├─ redimensionador.py # Lógica de redimensionamento de arquivos/imagens
│ └─ renomeador.py # Lógica de renomeação de arquivos
└─ README.md
```

---

## Compilação
Para compilar, usei o PyInstaller. Os passos foram esses, caso queira compilar por si:

1. **Instalar o PyInstaller**:
    ```
    pip install pyinstaller
    ```
2. **Abrir o terminal, e modificar a pasta onde está o projeto**:
    ```
    cd seu-caminho/compilador-de-livros/
    ```
3. **Compilar**:
    ```
    pyinstaller --onefile --windowed --icon=assets/icon.ico --add-data "assets;assets" --name="Compilador-de-Livros" app.py
    ```

O arquivo executável se chamará "Compilador-de-Livros.exe" e estará na pasta build.

![Views Counter](https://views-counter.vercel.app/badge?pageId=github%2Ecom%2FBonavigo%2Fcompilador-de-livtos&leftColor=000000&rightColor=0000ff&type=total&label=Views&style=none)

![Views Counter](https://views-counter.vercel.app/badge?pageId=github%2Ecom%2FBonavigo%2Fcompilador-de-livtos&leftColor=000000&rightColor=ff0000&type=daily&label=Hoje&style=none)