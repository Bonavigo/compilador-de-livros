import io
import os

import customtkinter as ctk
from tkinter import filedialog

from PyPDF2 import PdfReader, PdfWriter


def criar_aba(tabview):
    aba_divisor = tabview.add("Divisor de PDF")
    frame = ctk.CTkScrollableFrame(aba_divisor, width=560, height=460)
    frame.pack(padx=5, pady=5, fill="both", expand=True)

    def escolher_arquivo(entry_widget):
        arquivo = filedialog.askopenfilename(filetypes=[("Arquivos PDF", "*.pdf")])
        if arquivo:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, arquivo)

    def escolher_pasta(entry_widget):
        pasta = filedialog.askdirectory()
        if pasta:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, pasta)

    def limpar_campos():
        entry_pdf.delete(0, "end")
        entry_saida.delete(0, "end")
        entry_tamanho.delete(0, "end")
        entry_tamanho.insert(0, "10")

    def pdf_para_bytes(pages):
        writer = PdfWriter()
        for page in pages:
            writer.add_page(page)

        buffer = io.BytesIO()
        writer.write(buffer)
        return buffer.getvalue()

    def salvar_parte(pages, caminho_saida, nome_base, indice_parte, digitos):
        conteudo = pdf_para_bytes(pages)
        nome_arquivo = f"{nome_base}_parte_{indice_parte:0{digitos}d}.pdf"
        caminho_arquivo = os.path.join(caminho_saida, nome_arquivo)

        with open(caminho_arquivo, "wb") as arquivo_saida:
            arquivo_saida.write(conteudo)

        return caminho_arquivo

    def dividir_pdf():
        caminho_pdf = entry_pdf.get().strip()
        diretorio_saida = entry_saida.get().strip()
        tamanho_mb = entry_tamanho.get().strip()

        if not caminho_pdf or not diretorio_saida:
            status_label.configure(text="Faltam arquivo PDF ou pasta de saída.")
            status_label.update_idletasks()
            return

        if not os.path.isfile(caminho_pdf) or not caminho_pdf.lower().endswith(".pdf"):
            status_label.configure(text="O arquivo selecionado precisa ser um PDF válido.")
            status_label.update_idletasks()
            return

        try:
            limite_mb = float(tamanho_mb)
        except ValueError:
            status_label.configure(text="Tamanho máximo inválido.")
            status_label.update_idletasks()
            return

        if limite_mb <= 0:
            status_label.configure(text="O tamanho máximo precisa ser maior que zero.")
            status_label.update_idletasks()
            return

        limite_bytes = int(limite_mb * 1024 * 1024)

        try:
            reader = PdfReader(caminho_pdf)
        except Exception as erro:
            status_label.configure(text=f"Erro ao abrir o PDF: {erro}")
            status_label.update_idletasks()
            return

        os.makedirs(diretorio_saida, exist_ok=True)

        total_paginas = len(reader.pages)
        digitos = 4 if total_paginas > 999 else 3
        nome_base = os.path.splitext(os.path.basename(caminho_pdf))[0]

        paginas_atuais = []
        partes_geradas = 0

        try:
            for indice_pagina, pagina in enumerate(reader.pages, start=1):
                status_label.configure(text=f"Processando página {indice_pagina} de {total_paginas}...")
                status_label.update_idletasks()

                paginas_atuais.append(pagina)
                tamanho_atual = len(pdf_para_bytes(paginas_atuais))

                if tamanho_atual > limite_bytes:
                    ultima_pagina = paginas_atuais.pop()

                    if paginas_atuais:
                        partes_geradas += 1
                        salvar_parte(paginas_atuais, diretorio_saida, nome_base, partes_geradas, digitos)

                    paginas_atuais = [ultima_pagina]

            if paginas_atuais:
                partes_geradas += 1
                salvar_parte(paginas_atuais, diretorio_saida, nome_base, partes_geradas, digitos)

            limpar_campos()
            status_label.configure(
                text=f"Concluído. {partes_geradas} partes geradas em {diretorio_saida}."
            )
            status_label.update_idletasks()

        except Exception as erro:
            status_label.configure(text=f"Erro ao dividir o PDF: {erro}")
            status_label.update_idletasks()

    ctk.CTkLabel(frame, text="Arquivo PDF de entrada").pack(pady=10)
    entry_pdf = ctk.CTkEntry(frame, placeholder_text="Insira o arquivo PDF...", width=280)
    entry_pdf.pack()
    ctk.CTkButton(frame, text="Escolher Arquivo", command=lambda: escolher_arquivo(entry_pdf)).pack(pady=10)

    ctk.CTkLabel(frame, text="Pasta de saída").pack(pady=10)
    entry_saida = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=280)
    entry_saida.pack()
    ctk.CTkButton(frame, text="Escolher Pasta", command=lambda: escolher_pasta(entry_saida)).pack(pady=10)

    ctk.CTkLabel(frame, text="Tamanho máximo por parte (MB)").pack(pady=10)
    entry_tamanho = ctk.CTkEntry(frame, width=100)
    entry_tamanho.insert(0, "10")
    entry_tamanho.pack()

    status_label = ctk.CTkLabel(frame, text="", wraplength=400)
    status_label.pack(pady=10)

    ctk.CTkButton(frame, text="Dividir PDF", command=dividir_pdf).pack(pady=10)
