# Compilador de Livros

O **Compilador de Livros** é um aplicativo desktop em Python com interface gráfica, criado para automatizar tarefas comuns no fluxo de trabalho de quem organiza páginas digitalizadas, arquivos de imagem e PDFs de livros.

O programa reúne várias utilidades em uma única janela com abas independentes:

- `Compilador`
- `Redimensionador`
- `Renomeador`
- `Fragmentador`
- `Juntador`
- `Divisor`

![Python](https://img.shields.io/badge/python-3.10+-blue)

---

## Visão Geral

O objetivo do projeto é reduzir trabalho manual e evitar erros de organização ao lidar com:

- imagens de páginas digitalizadas;
- PDFs grandes que precisam ser quebrados em partes menores;
- partes de PDF que precisam ser reunidas depois;
- imagens de página dupla que precisam ser separadas em páginas individuais;
- renomeação sequencial de arquivos.

Cada aba resolve uma tarefa específica e mantém a interface simples, com foco em operação rápida.

---

## Funcionalidades

### Compilador
Compila várias imagens em um único PDF final, respeitando a ordem numérica dos arquivos e permitindo adicionar metadados.

### Redimensionador
Redimensiona imagens em lote, convertendo-as para JPEG e permitindo escolher redução e qualidade.

### Renomeador
Renomeia ou copia arquivos numericamente, preservando a sequência de nomes e extensões.

### Fragmentador
Divide um PDF em partes menores com limite configurável de tamanho por arquivo.

### Juntador
Junta vários PDFs de uma pasta em um único PDF final, ordenando os arquivos corretamente.

### Divisor
Separa imagens de páginas duplas ou PDFs em duas páginas por folha, com suporte a ordem de leitura e modo lossless para saída em PDF.

---

## Como Usar

### Compilador
1. Escolha a pasta de entrada com imagens.
2. Escolha a pasta de saída.
3. Preencha os metadados se quiser.
4. Clique em `Compilar`.

### Redimensionador
1. Escolha a pasta de entrada com imagens.
2. Escolha a pasta de saída.
3. Defina redução e qualidade.
4. Clique em `Redimensionar`.

### Renomeador
1. Escolha a pasta de entrada.
2. Escolha a pasta de saída.
3. Informe o número inicial.
4. Clique em `Renomear`.

### Fragmentador
1. Escolha o PDF de entrada.
2. Escolha a pasta de saída.
3. Defina o tamanho máximo por parte.
4. Clique em `Dividir PDF`.

### Juntador
1. Escolha a pasta contendo os PDFs parciais.
2. Escolha a pasta de saída.
3. Informe o nome do arquivo final.
4. Se quiser, use um filtro por prefixo.
5. Clique em `Juntar PDFs`.

### Divisor
1. Escolha a origem: pasta com imagens ou arquivo PDF.
2. Escolha o formato de saída: imagens ou PDF.
3. Se desejar PDF sem recompressão, marque a opção `Saída PDF sem recompressão (lossless)`.
4. Escolha a pasta de saída.
5. Defina o corte e a ordem de leitura.
6. Clique em `Separar Folhas`.

---

## Capturas de Tela

### Compilador
![Compilador - diretórios](https://i.imgur.com/K7iWzUA.png)
![Compilador - metadados](https://i.imgur.com/4ZYxJeD.png)
![Compilador - execução](https://i.imgur.com/wKnarjW.png)

### Redimensionador
![Redimensionador - diretórios](https://i.imgur.com/L2LpVPF.png)
![Redimensionador - parâmetros](https://i.imgur.com/AtLG0d1.png)
![Redimensionador - execução](https://i.imgur.com/JlpSCqi.png)

### Renomeador
![Renomeador - diretórios](https://i.imgur.com/Zgem1DA.png)
![Renomeador - aviso](https://i.imgur.com/Cvu9Btu.png)
![Renomeador - número inicial](https://i.imgur.com/zK5wfbW.png)
![Renomeador - execução](https://i.imgur.com/xT1IxL6.png)

As abas `Fragmentador`, `Juntador` e `Divisor` seguem o mesmo padrão visual das demais.

---

## Explicação Detalhada das Funções

Esta seção documenta as funções principais e os auxiliares internos de cada módulo.

### `modulos/compilador.py`

- `criar_aba(tabview)`
  - Cria a aba `Compilador` na interface principal.
  - Monta todos os campos de entrada, botões, labels e o botão de execução.
  - Define as funções auxiliares internas usadas pela aba.

- `escolher_pasta(entry_widget)`
  - Abre um seletor de pasta do sistema.
  - Escreve o caminho escolhido no campo de entrada recebido como parâmetro.

- `extrair_numero(nome)`
  - Extrai o primeiro número encontrado em um nome de arquivo.
  - É usado para ordenar as imagens numericamente antes da compilação.
  - Se não houver número, retorna `float('inf')` para empurrar o arquivo para o fim da ordenação.

- `limpar_campos()`
  - Apaga os campos da interface depois de uma compilação bem-sucedida.
  - Deixa a aba pronta para uma nova execução.

- `compilar_imagens()`
  - Valida os diretórios informados.
  - Lê os arquivos `.jpg`, `.jpeg` e `.png` da pasta de entrada.
  - Ordena os arquivos por número.
  - Converte as imagens em PDF temporário.
  - Reabre o PDF temporário com `PyPDF2`, copia as páginas e adiciona metadados.
  - Salva o resultado como `livro_final.pdf`.

### `modulos/redimensionador.py`

- `criar_aba(tabview)`
  - Cria a aba `Redimensionador`.
  - Monta a interface para seleção de pastas, redução e qualidade.

- `escolher_pasta(entry_widget)`
  - Abre o seletor de pasta e preenche o campo recebido.

- `limpar_campos()`
  - Limpa os campos de entrada após o processamento.
  - Restaura os valores padrão de redução e qualidade.

- `redimensionar_imagens()`
  - Valida os caminhos informados.
  - Lista as imagens válidas da pasta de entrada.
  - Aplica o redimensionamento com `Image.LANCZOS`.
  - Salva as imagens em JPEG na pasta de saída.
  - Atualiza o status com o progresso do lote.

### `modulos/renomeador.py`

- `criar_aba(tabview)`
  - Cria a aba `Renomeador`.
  - Monta os campos de entrada, a opção de usar a mesma pasta e o botão de execução.

- `escolher_pasta(entry_widget)`
  - Abre o seletor de pasta e insere o caminho no campo indicado.

- `toggle_mesmo_diretorio()`
  - Ativa ou desativa o uso da mesma pasta como entrada e saída.
  - Ajusta o estado dos campos e exibe o aviso de risco de conflito de nomes.

- `extrair_numero(nome)`
  - Extrai o primeiro número de um nome de arquivo para ordenar corretamente a sequência.

- `limpar_campos()`
  - Limpa os campos após a execução.
  - Remove o aviso de mesma pasta e apaga o número inicial.

- `renomear_arquivos()`
  - Valida as pastas e o número inicial.
  - Lista os arquivos da pasta de entrada.
  - Ordena os arquivos numericamente.
  - Renomeia ou copia os arquivos com numeração sequencial.
  - Atualiza o status com progresso e erros individuais.

### `modulos/divisor_pdf.py` - `Fragmentador`

- `criar_aba(tabview)`
  - Cria a aba `Fragmentador`.
  - Monta os campos para PDF de entrada, pasta de saída e limite de tamanho.
  - Inicia a divisão em thread separada.

- `escolher_arquivo(entry_widget)`
  - Abre um seletor de arquivo filtrado para PDF.
  - Insere o caminho do arquivo no campo informado.

- `escolher_pasta(entry_widget)`
  - Abre um seletor de pasta.
  - Preenche o campo de pasta de saída.

- `limpar_campos()`
  - Restaura os campos para o estado inicial após a execução.

- `atualizar_status(texto)`
  - Atualiza o label de status usando `after()`.
  - Evita acesso direto à interface a partir da thread.

- `salvar_writer(writer, caminho_saida, nome_base, indice_parte, digitos, metadados_pdf=None)`
  - Escreve um `PdfWriter` em memória.
  - Salva o conteúdo em disco com o nome de parte correto.
  - Adiciona metadados ao arquivo se eles existirem.
  - Retorna o caminho salvo e o tamanho real em bytes.

- `executar_divisao()`
  - Faz toda a lógica de separação página a página.
  - Medições são feitas incrementalmente com `BytesIO`.
  - Decide quando salvar uma parte e quando iniciar a próxima.
  - Emite aviso quando uma página sozinha excede o limite.
  - Gera um relatório final com maior e menor parte.

- `dividir_pdf()`
  - Cria e inicia a thread de execução.
  - Mantém a interface responsiva durante o processamento.

### `modulos/juntador_pdf.py` - `Juntador`

- `criar_aba(tabview)`
  - Cria a aba `Juntador`.
  - Monta os campos de pasta de entrada, pasta de saída, nome final e filtro.

- `escolher_pasta(entry_widget)`
  - Abre o seletor de pasta e escreve o caminho no campo recebido.

- `extrair_numero(nome)`
  - Extrai o primeiro número do nome do arquivo para ordenar os PDFs na sequência correta.

- `atualizar_status(texto)`
  - Atualiza o label de status via `after()`.
  - Evita travamento ou acesso direto à UI a partir da thread.

- `limpar_campos()`
  - Limpa os campos após a conclusão da junção.

- `executar_juncao()`
  - Valida a entrada e a saída.
  - Lista os PDFs da pasta, aplicando o filtro opcional por prefixo.
  - Ordena os arquivos por número e desempate alfabético.
  - Abre cada PDF com `PdfReader`.
  - Adiciona todas as páginas a um `PdfWriter`.
  - Ignora arquivos corrompidos e registra os avisos.
  - Salva o PDF final e calcula seu tamanho.

- `iniciar_juncao()`
  - Inicia a execução em uma thread separada.

### `modulos/separador_folhas.py` - `Divisor`

- `criar_aba(tabview)`
  - Cria a aba `Divisor`.
  - Monta a interface com seleção de origem, saída, corte, ordem de leitura e modo lossless.

- `escolher_pasta(entry_widget)`
  - Abre o seletor de pasta e preenche o campo correspondente.

- `escolher_arquivo_pdf(entry_widget)`
  - Abre um seletor de arquivos PDF.
  - Preenche o campo com o caminho do PDF escolhido.

- `extrair_numero(nome)`
  - Extrai o primeiro número do nome do arquivo para ordenar imagens numericamente.

- `atualizar_interface_entrada(valor_selecionado=None)`
  - Altera o rótulo, o placeholder e o botão conforme o tipo de entrada escolhido.
  - Faz a interface se adaptar entre pasta de imagens e arquivo PDF.

- `atualizar_interface_saida(valor_selecionado=None)`
  - Ajusta o texto do rótulo da saída.
  - Habilita ou desabilita a opção lossless conforme o formato escolhido.

- `atualizar_opcao_lossless()`
  - Controla o estado da caixa de seleção lossless.
  - Só permite marcar quando a saída é PDF.

- `atualizar_opcao_corte(valor_selecionado=None)`
  - Mostra ou oculta o campo de percentual quando a opção `Personalizado` é escolhida.

- `limpar_campos()`
  - Restaura os valores padrão da aba após a execução.

- `salvar_imagem(imagem, caminho_saida)`
  - Salva uma imagem recortada em JPEG com qualidade e otimização.

- `carregar_imagens_da_pasta(pasta_entrada)`
  - Lista imagens válidas da pasta.
  - Ordena os arquivos por número no nome.

- `renderizar_pdf_em_imagens(caminho_pdf)`
  - Converte páginas de PDF em imagens para permitir o corte.
  - Usa `fitz` quando disponível e tenta fallback compatível quando possível.

- `abrir_origem()`
  - Valida a origem escolhida.
  - Diferencia PDF e pasta de imagens.

- `preparar_paginas()`
  - Reúne os dados necessários para o processamento.
  - Valida percentual, origem e metadados do PDF quando aplicável.

- `cortar_imagem(imagem, modo_corte, percentual, ordem)`
  - Divide uma imagem em metade esquerda e direita.
  - Aplica a ordem de leitura escolhida.

- `escrever_pdf_com_metadados(imagens, caminho_saida_final, metadados_pdf)`
  - Escreve um PDF a partir de imagens e inclui metadados.

- `normalizar_metadados(metadados_pdf)`
  - Converte metadados para o formato esperado pelo `PdfWriter`.

- `cortar_pagina_pdf_lossless(pagina_original, modo_corte, percentual, ordem)`
  - Divide uma página PDF sem rasterizar.
  - Ajusta `mediabox` e `cropbox` para preservar melhor a qualidade.

- `escrever_pdf_lossless(reader, caminho_saida_final, metadados_pdf, modo_corte, percentual, ordem)`
  - Gera o PDF final em modo lossless a partir das páginas originais.

- `separar_folhas()`
  - Executa o fluxo completo da aba.
  - Processa imagens ou PDF de entrada.
  - Gera saída em imagens ou PDF.
  - Trata erros por arquivo quando necessário.

---

## Estrutura do Projeto

```text
compilador-de-livros/
├─ app.py
├─ assets/
│  ├─ icon.ico
│  └─ icone.png
├─ modulos/
│  ├─ __init__.py
│  ├─ compilador.py
│  ├─ redimensionador.py
│  ├─ renomeador.py
│  ├─ divisor_pdf.py
│  ├─ juntador_pdf.py
│  └─ separador_folhas.py
├─ texts/
└─ README.md
```

---

## Dependências

Bibliotecas usadas pelo projeto:

- `customtkinter`
  - Interface gráfica.
- `Pillow`
  - Manipulação de imagens.
- `PyPDF2`
  - Leitura e escrita de PDFs.
- `fitz` / `PyMuPDF`
  - Renderização de PDF para imagem no módulo `Divisor`, quando disponível.

Bibliotecas padrão:

- `os`
- `re`
- `io`
- `sys`
- `threading`
- `shutil`
- `tkinter.filedialog`

---

## Compilação

O projeto pode ser empacotado com PyInstaller.

1. Instale o PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Acesse a pasta do projeto:
   ```bash
   cd seu-caminho/compilador-de-livros/
   ```

3. Gere o executável:
   ```bash
   pyinstaller --onefile --windowed --icon=assets/icon.ico --add-data "assets;assets" --name="Compilador-de-Livros" app.py
   ```

O executável será criado com o nome `Compilador-de-Livros.exe`.

---

## Observações

- O projeto foi pensado para uso prático em desktop.
- O `Fragmentador` trabalha com PDFs grandes em thread separada.
- O `Juntador` ignora PDFs corrompidos, mas mantém relatório dos arquivos afetados.
- O `Divisor` permite saída em PDF ou imagens e tem opção lossless para saída em PDF quando a origem também é PDF.
