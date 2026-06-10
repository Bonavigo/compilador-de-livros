import os
import re
from copy import deepcopy

import customtkinter as ctk
from tkinter import filedialog

from PIL import Image, ImageSequence
from PyPDF2 import PdfReader, PdfWriter, Transformation

try:
    import fitz
except ImportError:  # pragma: no cover - dependência opcional de renderização de PDF
    fitz = None


def criar_aba(tabview):
    aba_separador = tabview.add("Divisor")
    frame = ctk.CTkScrollableFrame(aba_separador, width=560, height=460)
    frame.pack(padx=5, pady=5, fill="both", expand=True)

    def escolher_pasta(entry_widget):
        pasta = filedialog.askdirectory()
        if pasta:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, pasta)

    def escolher_arquivo_pdf(entry_widget):
        arquivo = filedialog.askopenfilename(filetypes=[("Arquivos PDF", "*.pdf")])
        if arquivo:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, arquivo)

    def extrair_numero(nome):
        numeros = re.findall(r"\d+", nome)
        return int(numeros[0]) if numeros else float("inf")

    def atualizar_interface_entrada(valor_selecionado=None):
        if tipo_entrada.get() == "Arquivo PDF":
            label_entrada.configure(text="Arquivo PDF de entrada")
            entry_entrada.delete(0, "end")
            entry_entrada.configure(placeholder_text="Insira o arquivo PDF...")
            button_entrada.configure(text="Escolher Arquivo")
            button_entrada.configure(command=lambda: escolher_arquivo_pdf(entry_entrada))
        else:
            label_entrada.configure(text="Pasta com as imagens")
            entry_entrada.delete(0, "end")
            entry_entrada.configure(placeholder_text="Insira o diretório...")
            button_entrada.configure(text="Escolher Pasta")
            button_entrada.configure(command=lambda: escolher_pasta(entry_entrada))

    def atualizar_interface_saida(valor_selecionado=None):
        if tipo_saida.get() == "PDF":
            label_saida.configure(text="Pasta de saída do PDF")
        else:
            label_saida.configure(text="Pasta de saída das imagens")
        atualizar_opcao_lossless()

    def atualizar_opcao_lossless():
        if tipo_saida.get() == "PDF":
            chk_lossless.configure(state="normal")
        else:
            chk_lossless.deselect()
            chk_lossless.configure(state="disabled")

    def atualizar_opcao_corte(valor_selecionado=None):
        if opcao_corte.get() == "Personalizado":
            frame_personalizado.pack(pady=5)
        else:
            frame_personalizado.pack_forget()

    def limpar_campos():
        tipo_entrada.set("Pasta com imagens")
        tipo_saida.set("Imagens")
        entry_entrada.delete(0, "end")
        entry_saida.delete(0, "end")
        opcao_corte.set("Centro exato")
        entry_percentual.delete(0, "end")
        entry_percentual.insert(0, "50")
        ordem_leitura.set("Esquerda para direita")
        chk_lossless.deselect()
        atualizar_interface_entrada()
        atualizar_interface_saida()
        atualizar_opcao_lossless()
        atualizar_opcao_corte()

    def salvar_imagem(imagem, caminho_saida):
        imagem.convert("RGB").save(caminho_saida, quality=95, optimize=True)

    def carregar_imagens_da_pasta(pasta_entrada):
        arquivos = [
            arquivo
            for arquivo in os.listdir(pasta_entrada)
            if arquivo.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        arquivos = sorted(arquivos, key=extrair_numero)
        return [os.path.join(pasta_entrada, arquivo) for arquivo in arquivos]

    def renderizar_pdf_em_imagens(caminho_pdf):
        if fitz is None:
            try:
                with Image.open(caminho_pdf) as documento_pil:
                    return [pagina.convert("RGB") for pagina in ImageSequence.Iterator(documento_pil)]
            except Exception as erro:
                raise RuntimeError(
                    "Leitura de PDF como imagem indisponível. Instale o PyMuPDF (fitz) ou uma dependência de renderização compatível."
                ) from erro

        documento = fitz.open(caminho_pdf)
        imagens = []

        try:
            for indice_pagina in range(len(documento)):
                pagina = documento.load_page(indice_pagina)
                matriz = fitz.Matrix(2, 2)
                pixmap = pagina.get_pixmap(matrix=matriz, alpha=False)
                modo = "RGB" if pixmap.n < 4 else "RGBA"
                imagem = Image.frombytes(modo, [pixmap.width, pixmap.height], pixmap.samples)
                imagens.append(imagem.convert("RGB"))
        finally:
            documento.close()

        return imagens

    def abrir_origem():
        caminho = entry_entrada.get().strip()
        if not caminho:
            raise ValueError("Escolha a origem antes de continuar.")

        if tipo_entrada.get() == "Arquivo PDF":
            if not os.path.isfile(caminho) or not caminho.lower().endswith(".pdf"):
                raise ValueError("O arquivo selecionado precisa ser um PDF válido.")
            return "pdf", caminho

        if not os.path.isdir(caminho):
            raise ValueError("A pasta de entrada é inválida.")
        return "pasta", caminho

    def preparar_paginas():
        tipo_origem, caminho_origem = abrir_origem()
        modo_corte = opcao_corte.get()
        ordem = ordem_leitura.get()

        try:
            percentual = float(entry_percentual.get().strip() or "50")
        except ValueError as erro:
            raise ValueError("Percentual de corte inválido.") from erro

        if modo_corte == "Personalizado" and not (0 < percentual < 100):
            raise ValueError("O percentual de corte precisa ficar entre 0 e 100.")

        itens_origem = []
        metadados_pdf = None
        nome_base_saida = "folhas_separadas"

        if tipo_origem == "pdf":
            try:
                reader = PdfReader(caminho_origem)
            except Exception as erro:
                raise RuntimeError(f"Erro ao abrir o PDF: {erro}") from erro

            metadados_pdf = reader.metadata
            nome_base_saida = os.path.splitext(os.path.basename(caminho_origem))[0]

            try:
                paginas = renderizar_pdf_em_imagens(caminho_origem)
            except Exception as erro:
                raise RuntimeError(f"Erro ao converter o PDF em imagens: {erro}") from erro

            for indice, imagem in enumerate(paginas, start=1):
                itens_origem.append((f"página {indice}", imagem))
        else:
            caminhos_imagens = carregar_imagens_da_pasta(caminho_origem)
            if not caminhos_imagens:
                raise ValueError("Nenhuma imagem válida encontrada na pasta de entrada.")

            nome_base_saida = os.path.basename(os.path.normpath(caminho_origem)) or "folhas_separadas"

            for caminho_imagem in caminhos_imagens:
                itens_origem.append((os.path.basename(caminho_imagem), caminho_imagem))

        if not itens_origem:
            raise ValueError("Não foi possível localizar páginas válidas na origem selecionada.")

        return itens_origem, tipo_origem, modo_corte, percentual, ordem, metadados_pdf, nome_base_saida

    def cortar_imagem(imagem, modo_corte, percentual, ordem):
        imagem_rgb = imagem.convert("RGB")
        largura, altura = imagem_rgb.size

        if modo_corte == "Centro exato":
            ponto_corte = largura // 2
        else:
            ponto_corte = int(largura * (percentual / 100))

        if ponto_corte <= 0 or ponto_corte >= largura:
            raise ValueError("Ponto de corte inválido para a imagem atual.")

        parte_esquerda = imagem_rgb.crop((0, 0, ponto_corte, altura))
        parte_direita = imagem_rgb.crop((ponto_corte, 0, largura, altura))

        if ordem == "Esquerda para direita":
            return [parte_esquerda, parte_direita]
        return [parte_direita, parte_esquerda]

    def escrever_pdf_com_metadados(imagens, caminho_saida_final, metadados_pdf):
        if not imagens:
            raise ValueError("Não há páginas para gerar o PDF.")

        caminho_temp = os.path.join(os.path.dirname(caminho_saida_final), "_temp_separador_folhas.pdf")
        try:
            imagens[0].save(caminho_temp, save_all=True, append_images=imagens[1:])
            reader = PdfReader(caminho_temp)
            writer = PdfWriter()

            for pagina in reader.pages:
                writer.add_page(pagina)

            if metadados_pdf:
                metadados_formatados = {}
                for chave, valor in dict(metadados_pdf).items():
                    if valor is not None:
                        metadados_formatados[str(chave)] = str(valor)
                if metadados_formatados:
                    writer.add_metadata(metadados_formatados)

            with open(caminho_saida_final, "wb") as arquivo_saida:
                writer.write(arquivo_saida)
        finally:
            if os.path.exists(caminho_temp):
                try:
                    os.remove(caminho_temp)
                except OSError:
                    pass

    def normalizar_metadados(metadados_pdf):
        if not metadados_pdf:
            return {}

        metadados_formatados = {}
        for chave, valor in dict(metadados_pdf).items():
            if valor is not None:
                metadados_formatados[str(chave)] = str(valor)
        return metadados_formatados

    def cortar_pagina_pdf_lossless(pagina_original, modo_corte, percentual, ordem):
        largura = float(pagina_original.mediabox.width)
        altura = float(pagina_original.mediabox.height)

        if modo_corte == "Centro exato":
            ponto_corte = largura / 2
        else:
            ponto_corte = largura * (percentual / 100)

        if ponto_corte <= 0 or ponto_corte >= largura:
            raise ValueError("Ponto de corte inválido para a página atual.")

        def preparar_pagina(copia_pagina, deslocamento_x, largura_saida):
            if deslocamento_x:
                copia_pagina.add_transformation(Transformation().translate(-deslocamento_x, 0))

            copia_pagina.mediabox.lower_left = (0, 0)
            copia_pagina.mediabox.upper_right = (largura_saida, altura)
            copia_pagina.cropbox.lower_left = (0, 0)
            copia_pagina.cropbox.upper_right = (largura_saida, altura)
            return copia_pagina

        pagina_esquerda = preparar_pagina(deepcopy(pagina_original), 0, ponto_corte)
        pagina_direita = preparar_pagina(deepcopy(pagina_original), ponto_corte, largura - ponto_corte)

        if ordem == "Esquerda para direita":
            return [pagina_esquerda, pagina_direita]
        return [pagina_direita, pagina_esquerda]

    def escrever_pdf_lossless(reader, caminho_saida_final, metadados_pdf, modo_corte, percentual, ordem):
        writer = PdfWriter()

        for pagina_original in reader.pages:
            for pagina_partida in cortar_pagina_pdf_lossless(pagina_original, modo_corte, percentual, ordem):
                writer.add_page(pagina_partida)

        metadados_formatados = normalizar_metadados(metadados_pdf)
        if metadados_formatados:
            writer.add_metadata(metadados_formatados)

        with open(caminho_saida_final, "wb") as arquivo_saida:
            writer.write(arquivo_saida)

    def separar_folhas():
        pasta_saida = entry_saida.get().strip()
        if not pasta_saida:
            status_label.configure(text="Falta a pasta de saída.")
            status_label.update_idletasks()
            return

        try:
            os.makedirs(pasta_saida, exist_ok=True)
        except Exception as erro:
            status_label.configure(text=f"Erro ao criar a pasta de saída: {erro}")
            status_label.update_idletasks()
            return

        try:
            itens_origem, tipo_origem, modo_corte, percentual, ordem, metadados_pdf, nome_base_saida = preparar_paginas()
        except Exception as erro:
            status_label.configure(text=str(erro))
            status_label.update_idletasks()
            return

        saida_em_pdf = tipo_saida.get() == "PDF"
        usar_lossless = saida_em_pdf and chk_lossless.get() == 1
        paginas_processadas = []
        total_itens = len(itens_origem)
        total_paginas_esperadas = total_itens * 2
        digitos = 4 if total_paginas_esperadas > 999 else 3
        numero_saida = 1
        sucesso = 0
        falhas = 0

        for indice_item, (nome_item, item) in enumerate(itens_origem, start=1):
            status_label.configure(text=f"Processando imagem {indice_item} de {total_itens}...")
            status_label.update_idletasks()

            try:
                if tipo_origem == "pdf":
                    imagem_base = item
                else:
                    with Image.open(item) as imagem_original:
                        imagem_base = imagem_original.copy()

                paginas = cortar_imagem(imagem_base, modo_corte, percentual, ordem)

                for pagina in paginas:
                    if saida_em_pdf:
                        paginas_processadas.append(pagina)
                    else:
                        nome_saida = f"{numero_saida:0{digitos}d}.jpg"
                        caminho_saida = os.path.join(pasta_saida, nome_saida)
                        salvar_imagem(pagina, caminho_saida)
                    numero_saida += 1

                sucesso += 1

            except Exception as erro:
                falhas += 1
                status_label.configure(text=f"Erro em {nome_item}: {erro}")
                status_label.update_idletasks()

        try:
            if saida_em_pdf:
                nome_saida_pdf = f"{nome_base_saida}_separado.pdf"
                caminho_saida_pdf = os.path.join(pasta_saida, nome_saida_pdf)
                if usar_lossless and tipo_origem == "pdf":
                    try:
                        reader = PdfReader(entry_entrada.get().strip())
                    except Exception as erro:
                        raise RuntimeError(f"Erro ao reabrir o PDF de entrada para saída lossless: {erro}") from erro

                    escrever_pdf_lossless(reader, caminho_saida_pdf, metadados_pdf, modo_corte, percentual, ordem)
                    status_final = f"Concluído. {len(reader.pages) * 2} arquivos gerados em {pasta_saida}."
                else:
                    if not paginas_processadas:
                        raise ValueError("Nenhuma página foi gerada para o PDF de saída.")

                    escrever_pdf_com_metadados(paginas_processadas, caminho_saida_pdf, metadados_pdf)
                    status_final = f"Concluído. {len(paginas_processadas)} arquivos gerados em {pasta_saida}."
            else:
                status_final = f"Concluído. {numero_saida - 1} arquivos gerados em {pasta_saida}."
        except Exception as erro:
            status_label.configure(text=f"Erro ao finalizar a saída: {erro}")
            status_label.update_idletasks()
            return

        limpar_campos()
        status_label.configure(
            text=(
                f"{status_final} "
                f"Imagens processadas com sucesso: {sucesso}. Falhas: {falhas}."
            )
        )
        status_label.update_idletasks()

    ctk.CTkLabel(frame, text="Tipo de entrada").pack(pady=10)
    tipo_entrada = ctk.CTkComboBox(
        frame,
        values=["Pasta com imagens", "Arquivo PDF"],
        state="readonly",
        command=atualizar_interface_entrada,
    )
    tipo_entrada.set("Pasta com imagens")
    tipo_entrada.pack()

    label_entrada = ctk.CTkLabel(frame, text="Pasta com as imagens")
    label_entrada.pack(pady=10)
    entry_entrada = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=250)
    entry_entrada.pack()
    button_entrada = ctk.CTkButton(frame, text="Escolher Pasta", command=lambda: escolher_pasta(entry_entrada))
    button_entrada.pack(pady=10)

    ctk.CTkLabel(frame, text="Formato de saída").pack(pady=10)
    tipo_saida = ctk.CTkComboBox(
        frame,
        values=["Imagens", "PDF"],
        state="readonly",
        command=atualizar_interface_saida,
    )
    tipo_saida.set("Imagens")
    tipo_saida.pack()

    chk_lossless = ctk.CTkCheckBox(
        frame,
        text="Saída PDF sem recompressão (lossless)",
        command=atualizar_opcao_lossless,
    )
    chk_lossless.pack(pady=5)

    label_saida = ctk.CTkLabel(frame, text="Pasta de saída das imagens")
    label_saida.pack(pady=10)
    entry_saida = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=250)
    entry_saida.pack()
    ctk.CTkButton(frame, text="Escolher Pasta", command=lambda: escolher_pasta(entry_saida)).pack(pady=10)

    ctk.CTkLabel(frame, text="Posição do corte").pack(pady=10)
    opcao_corte = ctk.CTkComboBox(
        frame,
        values=["Centro exato", "Personalizado"],
        state="readonly",
        command=atualizar_opcao_corte,
    )
    opcao_corte.set("Centro exato")
    opcao_corte.pack()

    frame_personalizado = ctk.CTkFrame(frame, fg_color="transparent")
    ctk.CTkLabel(frame_personalizado, text="Percentual da largura do corte").pack(side="left", padx=5)
    entry_percentual = ctk.CTkEntry(frame_personalizado, width=80)
    entry_percentual.insert(0, "50")
    entry_percentual.pack(side="left", padx=5)

    ctk.CTkLabel(frame, text="Ordem de leitura").pack(pady=10)
    ordem_leitura = ctk.CTkComboBox(
        frame,
        values=["Esquerda para direita", "Direita para esquerda"],
        state="readonly",
    )
    ordem_leitura.set("Esquerda para direita")
    ordem_leitura.pack()

    status_label = ctk.CTkLabel(frame, text="", wraplength=400)
    status_label.pack(pady=10)

    ctk.CTkButton(frame, text="Separar Folhas", command=separar_folhas).pack(pady=10)

    atualizar_interface_entrada()
    atualizar_interface_saida()
    atualizar_opcao_lossless()
    atualizar_opcao_corte()
