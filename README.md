# Compilador de Livros
O **Compilador de Livros** é um aplicativo em Python com interface gráfica, desenvolvido para compilar, redimensionar e renomear arquivos de forma automática. É uma ferramenta útil aos que escaneiam e compilam livros para publicá-los na internet.

---

## Funcionalidades

- **Compilação de arquivos**:
  Compila várias imagens, em qualquer formato, usando de ordem numérica, em um pdf com metadados.

- **Redimensionamento de arquivos**:
  Redimensiona os arquivos, convertendo-os para o formato .jpeg, usando os parâmetros dados pelo usuário. É útil para diminuir o peso das imagens, e, portanto, do pdf final.

- **Renomeação automática de arquivos**:
  Renomeia arquivos numericamente, respeitando a sequência e extensões originais.

---

## Estrutura do Projeto
```
compilador-de-livros/
│
├─ app.py # Script principal que inicializa a interface e chama os módulos
├─ modulos/
│ ├─ init.py # Inicializa o pacote de módulos
│ ├─ compilador.py # Lógica de compilação dos arquivos
│ ├─ redimensionador.py # Lógica de redimensionamento de arquivos/imagens
│ └─ renomeador.py # Lógica de renomeação de arquivos
└─ README.md
```