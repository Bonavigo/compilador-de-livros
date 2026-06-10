import os
import re
import threading

import customtkinter as ctk
from tkinter import filedialog

from PyPDF2 import PdfReader, PdfWriter


def criar_aba(tabview):
    aba_juntador = tabview.add("Juntar PDFs")
    frame = ctk.CTkScrollableFrame(aba_juntador, width=560, height=460)
    frame.pack(padx=5, pady=5, fill="both", expand=True)

    def escolher_pasta(entry_widget):
        pasta = filedialog.askdirectory()
        if pasta:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, pasta)

    def extrair_numero(nome):
        numeros = re.findall(r"\d+", nome)
        return int(numeros[0]) if numeros else float("inf")

    def atualizar_status(texto):
        status_label.after(0, lambda: status_label.configure(text=texto))

    def limpar_campos():
        entry_entrada.delete(0, "end")
        entry_saida.delete(0, "end")
        entry_nome_saida.delete(0, "end")
        entry_filtro.delete(0, "end")
        entry_nome_saida.insert(0, "")
        entry_nome_saida.configure(placeholder_text="documento_final")
        entry_filtro.configure(placeholder_text="Prefixo opcional")

    def executar_juncao():
        pasta_entrada = entry_entrada.get().strip()
        pasta_saida = entry_saida.get().strip()
        nome_saida = entry_nome_saida.get().strip()
        filtro = entry_filtro.get().strip()

        if not pasta_entrada:
            atualizar_status("Escolha a pasta de entrada.")
            return

        if not os.path.isdir(pasta_entrada):
            atualizar_status("A pasta de entrada é inválida.")
            return

        if not pasta_saida:
            atualizar_status("Escolha a pasta de saída.")
            return

        if not nome_saida:
            atualizar_status("Informe o nome do arquivo de saída.")
            return

        try:
            os.makedirs(pasta_saida, exist_ok=True)
        except Exception as erro:
            atualizar_status(f"Erro ao criar a pasta de saída: {erro}")
            return

        try:
            arquivos = [
                arquivo
                for arquivo in os.listdir(pasta_entrada)
                if arquivo.lower().endswith(".pdf")
                and (not filtro or os.path.basename(arquivo).startswith(filtro))
            ]
        except Exception as erro:
            atualizar_status(f"Erro ao listar os PDFs da pasta: {erro}")
            return

        if not arquivos:
            atualizar_status("Nenhum arquivo PDF encontrado na pasta.")
            return

        arquivos = sorted(arquivos, key=lambda nome: (extrair_numero(nome), nome.lower()))
        atualizar_status(f"{len(arquivos)} arquivos encontrados. Iniciando junção...")

        writer = PdfWriter()
        arquivos_ignorados = []
        total_paginas = 0

        for indice, nome_arquivo in enumerate(arquivos, start=1):
            caminho_arquivo = os.path.join(pasta_entrada, nome_arquivo)
            atualizar_status(f"Processando: {nome_arquivo} ({indice} de {len(arquivos)})...")

            try:
                reader = PdfReader(caminho_arquivo)
                try:
                    paginas = reader.pages
                except Exception as erro:
                    raise RuntimeError(f"arquivo corrompido: {erro}") from erro

                for pagina in paginas:
                    writer.add_page(pagina)
                    total_paginas += 1

            except Exception as erro:
                arquivos_ignorados.append(nome_arquivo)
                atualizar_status(f"Aviso: {nome_arquivo} ignorado por erro: {erro}")

        if total_paginas == 0:
            atualizar_status("Nenhuma página válida foi encontrada para juntar.")
            return

        caminho_saida = os.path.join(pasta_saida, f"{nome_saida}.pdf")

        try:
            if os.path.exists(caminho_saida):
                atualizar_status("Arquivo já existe. Sobrescrevendo...")

            with open(caminho_saida, "wb") as arquivo_saida:
                writer.write(arquivo_saida)

            tamanho_mb = os.path.getsize(caminho_saida) / (1024 * 1024)

        except Exception as erro:
            atualizar_status(f"Erro ao salvar o PDF final: {erro}")
            return

        if arquivos_ignorados:
            arquivos_juntos = len(arquivos) - len(arquivos_ignorados)
            atualizar_status(
                f"Concluído com avisos. {len(arquivos_ignorados)} arquivo(s) ignorado(s) por erro. "
                f"Verifique os arquivos: {', '.join(arquivos_ignorados)}. "
                f"{arquivos_juntos} arquivos juntos. Total: {total_paginas} páginas. "
                f"Tamanho: {tamanho_mb:.2f} MB. Salvo em: {caminho_saida}"
            )
        else:
            atualizar_status(
                f"Concluído. {len(arquivos)} arquivos juntos. Total: {total_paginas} páginas. "
                f"Tamanho: {tamanho_mb:.2f} MB. Salvo em: {caminho_saida}"
            )

        status_label.after(0, limpar_campos)

    def iniciar_juncao():
        thread = threading.Thread(target=executar_juncao, daemon=True)
        thread.start()

    ctk.CTkLabel(frame, text="Pasta de entrada").pack(pady=10)
    entry_entrada = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=280)
    entry_entrada.pack()
    ctk.CTkButton(frame, text="Escolher Pasta", command=lambda: escolher_pasta(entry_entrada)).pack(pady=10)

    ctk.CTkLabel(frame, text="Pasta de saída").pack(pady=10)
    entry_saida = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=280)
    entry_saida.pack()
    ctk.CTkButton(frame, text="Escolher Pasta", command=lambda: escolher_pasta(entry_saida)).pack(pady=10)

    ctk.CTkLabel(frame, text="Nome do arquivo de saída").pack(pady=10)
    entry_nome_saida = ctk.CTkEntry(frame, placeholder_text="documento_final", width=280)
    entry_nome_saida.pack()

    ctk.CTkLabel(frame, text="Filtro de arquivos").pack(pady=10)
    entry_filtro = ctk.CTkEntry(frame, placeholder_text="Prefixo opcional", width=280)
    entry_filtro.pack()
    ctk.CTkLabel(frame, text="Deixe em branco para incluir todos os PDFs da pasta.", text_color="#aaaaaa").pack(pady=5)

    status_label = ctk.CTkLabel(frame, text="", wraplength=400)
    status_label.pack(pady=10)

    ctk.CTkButton(frame, text="Juntar PDFs", command=iniciar_juncao).pack(pady=10)
