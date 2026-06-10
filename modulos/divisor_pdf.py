import io
import os
import threading

import customtkinter as ctk
from tkinter import filedialog

from PyPDF2 import PdfReader, PdfWriter


def criar_aba(tabview):
    aba_divisor = tabview.add("Fragmentador")
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

    def atualizar_status(texto):
        status_label.after(0, lambda: status_label.configure(text=texto))

    def salvar_writer(writer, caminho_saida, nome_base, indice_parte, digitos, metadados_pdf=None):
        if metadados_pdf:
            metadados_formatados = {}
            for chave, valor in dict(metadados_pdf).items():
                if valor is not None:
                    metadados_formatados[str(chave)] = str(valor)
            if metadados_formatados:
                writer.add_metadata(metadados_formatados)

        buffer_saida = io.BytesIO()
        writer.write(buffer_saida)
        tamanho_bytes = buffer_saida.tell()
        nome_arquivo = f"{nome_base}_parte_{indice_parte:0{digitos}d}.pdf"
        caminho_arquivo = os.path.join(caminho_saida, nome_arquivo)

        with open(caminho_arquivo, "wb") as arquivo_saida:
            arquivo_saida.write(buffer_saida.getvalue())

        return caminho_arquivo, tamanho_bytes

    def executar_divisao():
        caminho_pdf = entry_pdf.get().strip()
        diretorio_saida = entry_saida.get().strip()
        tamanho_mb = entry_tamanho.get().strip()

        if not caminho_pdf or not diretorio_saida:
            atualizar_status("Faltam arquivo PDF ou pasta de saída.")
            return

        if not os.path.isfile(caminho_pdf) or not caminho_pdf.lower().endswith(".pdf"):
            atualizar_status("O arquivo selecionado precisa ser um PDF válido.")
            return

        try:
            limite_mb = float(tamanho_mb)
        except ValueError:
            atualizar_status("Tamanho máximo inválido.")
            return

        if limite_mb <= 0:
            atualizar_status("O tamanho máximo precisa ser maior que zero.")
            return

        limite_bytes = int(limite_mb * 1024 * 1024)

        try:
            reader = PdfReader(caminho_pdf)
        except Exception as erro:
            atualizar_status(f"Erro ao abrir o PDF: {erro}")
            return

        try:
            os.makedirs(diretorio_saida, exist_ok=True)
        except Exception as erro:
            atualizar_status(f"Erro ao criar a pasta de saída: {erro}")
            return

        total_paginas = len(reader.pages)
        nome_base = os.path.splitext(os.path.basename(caminho_pdf))[0]

        if total_paginas == 0:
            atualizar_status("O PDF de entrada não tem páginas.")
            return

        writer_atual = PdfWriter()
        partes_geradas = 0
        partes_salvas = []
        tamanho_ultimo_buffer = 0
        metadados_pdf = reader.metadata

        try:
            for indice_pagina, pagina in enumerate(reader.pages, start=1):
                atualizar_status(f"Processando página {indice_pagina} de {total_paginas}...")

                escritor_teste = PdfWriter()
                for pagina_existente in writer_atual.pages:
                    escritor_teste.add_page(pagina_existente)
                escritor_teste.add_page(pagina)

                buffer_teste = io.BytesIO()
                escritor_teste.write(buffer_teste)
                tamanho_teste = buffer_teste.tell()

                if tamanho_teste <= limite_bytes:
                    writer_atual = escritor_teste
                    tamanho_ultimo_buffer = tamanho_teste
                    continue

                if len(writer_atual.pages) > 0:
                    partes_geradas += 1
                    digitos = max(3, len(str(total_paginas)))
                    atualizar_status(
                        f"Salvando parte {partes_geradas}... ({tamanho_ultimo_buffer / (1024 * 1024):.2f} MB)"
                    )

                    caminho_arquivo, tamanho_bytes = salvar_writer(
                        writer_atual,
                        diretorio_saida,
                        nome_base,
                        partes_geradas,
                        digitos,
                        metadados_pdf,
                    )
                    partes_salvas.append((caminho_arquivo, tamanho_bytes))

                    writer_novo = PdfWriter()
                    writer_novo.add_page(pagina)
                    buffer_novo = io.BytesIO()
                    writer_novo.write(buffer_novo)
                    tamanho_novo = buffer_novo.tell()

                    if tamanho_novo > limite_bytes:
                        partes_geradas += 1
                        digitos = max(3, len(str(total_paginas)))
                        atualizar_status(
                            f"Aviso: página {indice_pagina} excede o limite sozinha e será salva em arquivo próprio."
                        )
                        atualizar_status(
                            f"Salvando parte {partes_geradas}... ({tamanho_novo / (1024 * 1024):.2f} MB)"
                        )

                        caminho_arquivo, tamanho_bytes = salvar_writer(
                            writer_atual,
                            diretorio_saida,
                            nome_base,
                            partes_geradas,
                            digitos,
                            metadados_pdf,
                        )
                        partes_salvas.append((caminho_arquivo, tamanho_bytes))
                        writer_atual = PdfWriter()
                        tamanho_ultimo_buffer = 0
                    else:
                        writer_atual = writer_novo
                        tamanho_ultimo_buffer = tamanho_novo
                else:
                    partes_geradas += 1
                    digitos = max(3, len(str(total_paginas)))
                    atualizar_status(
                        f"Aviso: página {indice_pagina} excede o limite sozinha e será salva em arquivo próprio."
                    )
                    atualizar_status(
                        f"Salvando parte {partes_geradas}... ({tamanho_teste / (1024 * 1024):.2f} MB)"
                    )

                    writer_sozinho = PdfWriter()
                    writer_sozinho.add_page(pagina)
                    caminho_arquivo, tamanho_bytes = salvar_writer(
                        writer_sozinho,
                        diretorio_saida,
                        nome_base,
                        partes_geradas,
                        digitos,
                        metadados_pdf,
                    )
                    partes_salvas.append((caminho_arquivo, tamanho_bytes))
                    writer_atual = PdfWriter()
                    tamanho_ultimo_buffer = 0

        except Exception as erro:
            atualizar_status(f"Erro ao dividir o PDF: {erro}")
            return

        if len(writer_atual.pages) > 0:
            partes_geradas += 1
            digitos = max(3, len(str(total_paginas)))
            try:
                atualizar_status(
                    f"Salvando parte {partes_geradas}... ({tamanho_ultimo_buffer / (1024 * 1024):.2f} MB)"
                )
                caminho_arquivo, tamanho_bytes = salvar_writer(
                    writer_atual,
                    diretorio_saida,
                    nome_base,
                    partes_geradas,
                    digitos,
                    metadados_pdf,
                )
                partes_salvas.append((caminho_arquivo, tamanho_bytes))
            except Exception as erro:
                atualizar_status(f"Erro ao salvar a última parte: {erro}")
                return

        if partes_salvas:
            tamanhos_mb = [tamanho / (1024 * 1024) for _, tamanho in partes_salvas]
            maior_parte = max(tamanhos_mb)
            menor_parte = min(tamanhos_mb)
            atualizar_status(
                f"Concluído. {len(partes_salvas)} partes geradas em {diretorio_saida}. "
                f"Maior parte: {maior_parte:.2f} MB. Menor parte: {menor_parte:.2f} MB."
            )
        else:
            atualizar_status("Nenhuma parte foi gerada.")
            return

        status_label.after(0, limpar_campos)

    def dividir_pdf():
        thread = threading.Thread(target=executar_divisao, daemon=True)
        thread.start()

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
