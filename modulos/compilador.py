from __future__ import annotations

from io import BytesIO
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter

from modulos.servicos import (
    abrir_pasta_no_explorador,
    listar_arquivos_por_extensao,
    registrar_excecao,
    registrar_evento,
    registrar_no_historico,
    obter_historico,
)

EXTENSOES_COMPILADOR = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")
CHAVE_HISTORICO_ENTRADA = "compilador_entrada"
CHAVE_HISTORICO_SAIDA = "compilador_saida"
ARQUIVO_PADRAO_SAIDA = "livro_final.pdf"


def _atualizar_texto_previa(textbox: ctk.CTkTextbox, diretorio: str, arquivos: list[str], titulo: str) -> None:
    textbox.configure(state="normal")
    textbox.delete("1.0", "end")

    if not diretorio or not arquivos:
        textbox.insert("end", f"{titulo}\nNenhum arquivo encontrado.\n")
    else:
        textbox.insert("end", f"{titulo}\nDiretório: {diretorio}\nTotal: {len(arquivos)}\n\n")
        limite = 120
        for nome in arquivos[:limite]:
            textbox.insert("end", f"- {nome}\n")
        if len(arquivos) > limite:
            textbox.insert("end", f"\n... e mais {len(arquivos) - limite} arquivo(s)\n")

    textbox.configure(state="disabled")


def _ler_arquivos_compativeis(diretorio: str, incluir_pdfs: bool) -> list[str]:
    arquivos = listar_arquivos_por_extensao(
        diretorio,
        extensoes=EXTENSOES_COMPILADOR,
        incluir_pdf=incluir_pdfs,
    )
    return arquivos


def _adicionar_arquivo_ao_writer(writer: PdfWriter, caminho_arquivo: str) -> int:
    extensao = caminho_arquivo.lower().rsplit(".", 1)[-1]
    if extensao == "pdf":
        reader = PdfReader(caminho_arquivo)
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception as exc:
                raise ValueError(f"PDF criptografado: {caminho_arquivo}") from exc
        paginas = 0
        for pagina in reader.pages:
            writer.add_page(pagina)
            paginas += 1
        return paginas

    with Image.open(caminho_arquivo) as imagem:
        buffer = BytesIO()
        imagem.convert("RGB").save(buffer, format="PDF")
        buffer.seek(0)
        reader = PdfReader(buffer)
        paginas = 0
        for pagina in reader.pages:
            writer.add_page(pagina)
            paginas += 1
        return paginas


def compilar_documentos(
    diretorio_entrada: str,
    diretorio_saida: str,
    nome_pdf: str,
    metadados: dict[str, str],
    incluir_pdfs: bool = True,
) -> dict[str, object]:
    if not diretorio_entrada or not diretorio_saida:
        raise ValueError("Os diretórios de entrada e saída são obrigatórios.")

    arquivos = _ler_arquivos_compativeis(diretorio_entrada, incluir_pdfs=incluir_pdfs)
    if not arquivos:
        raise FileNotFoundError(
            "Nenhuma imagem ou PDF compatível foi encontrada na pasta de entrada."
        )

    registrar_evento(
        f"Compilação iniciada. Entrada={diretorio_entrada} Saída={diretorio_saida} Arquivos={len(arquivos)}"
    )

    from os import makedirs, path

    makedirs(diretorio_saida, exist_ok=True)
    nome_pdf = nome_pdf.strip() or ARQUIVO_PADRAO_SAIDA
    if not nome_pdf.lower().endswith(".pdf"):
        nome_pdf += ".pdf"

    caminho_pdf_final = path.join(diretorio_saida, nome_pdf)
    if path.exists(caminho_pdf_final):
        confirmar = messagebox.askyesno(
            "Substituir arquivo",
            f"Já existe um arquivo chamado '{nome_pdf}' na pasta de saída.\n\nDeseja substituir esse arquivo?",
        )
        if not confirmar:
            raise FileExistsError(caminho_pdf_final)

    writer = PdfWriter()
    total_paginas = 0
    arquivos_ignorados: list[str] = []
    for nome_arquivo in arquivos:
        caminho_arquivo = path.join(diretorio_entrada, nome_arquivo)
        try:
            total_paginas += _adicionar_arquivo_ao_writer(writer, caminho_arquivo)
        except Exception as exc:
            arquivos_ignorados.append(nome_arquivo)
            registrar_excecao(f"Falha ao adicionar arquivo ao PDF: {caminho_arquivo}")
            registrar_evento(
                f"Arquivo ignorado na compilação: {caminho_arquivo}",
                nivel="warning",
            )
            continue

    if total_paginas == 0:
        raise RuntimeError("Nenhum arquivo pôde ser convertido para PDF.")

    metadados_limpos = {chave: valor for chave, valor in metadados.items() if valor}
    if metadados_limpos:
        writer.add_metadata(metadados_limpos)

    with open(caminho_pdf_final, "wb") as saida:
        writer.write(saida)

    registrar_evento(
        f"Compilação concluída. Saída={caminho_pdf_final} Páginas={total_paginas} Ignorados={len(arquivos_ignorados)}"
    )
    return {
        "caminho": caminho_pdf_final,
        "paginas": total_paginas,
        "ignorados": arquivos_ignorados,
    }


def criar_aba(tabview):
    aba_compilador = tabview.add("Compilador")
    frame = ctk.CTkScrollableFrame(aba_compilador, width=560, height=460)
    frame.pack(padx=5, pady=5, fill="both", expand=True)

    def escolher_pasta(entry_widget, chave_historico: str):
        pasta = filedialog.askdirectory()
        if pasta:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, pasta)
            registrar_no_historico(chave_historico, pasta)
            atualizar_previa()

    def atualizar_previa():
        diretorio = entry_entrada.get()
        arquivos = _ler_arquivos_compativeis(diretorio, incluir_pdfs=bool(var_incluir_pdfs.get()))
        texto = "Prévia dos arquivos de entrada"
        if arquivos:
            texto += f" ({len(arquivos)})"
        _atualizar_texto_previa(preview_box, diretorio, arquivos, texto)

    def preencher_com_historico():
        historico_entrada = obter_historico(CHAVE_HISTORICO_ENTRADA)
        historico_saida = obter_historico(CHAVE_HISTORICO_SAIDA)
        if historico_entrada and not entry_entrada.get():
            entry_entrada.insert(0, historico_entrada[0])
        if historico_saida and not entry_saida.get():
            entry_saida.insert(0, historico_saida[0])

    def abrir_saida():
        if abrir_pasta_no_explorador(entry_saida.get()):
            status_label.configure(text="Pasta de saída aberta no explorador.")
        else:
            status_label.configure(text="Não foi possível abrir a pasta de saída.")

    def compilar_imagens():
        diretorio_entrada = entry_entrada.get().strip()
        diretorio_saida = entry_saida.get().strip()
        nome_pdf = entry_nome_pdf.get().strip()
        status_label.configure(text="Iniciando compilação...")
        status_label.update_idletasks()

        if not diretorio_entrada or not diretorio_saida:
            status_label.configure(
                text="Escolha as pastas de entrada e saída antes de compilar."
            )
            return

        metadados = {
            "/Title": entry_metadado_titulo.get().strip(),
            "/Author": entry_metadado_autor.get().strip(),
            "/Subject": entry_metadado_assunto.get().strip(),
            "/Keywords": entry_metadado_palavraschave.get().strip(),
        }

        try:
            resultado = compilar_documentos(
                diretorio_entrada=diretorio_entrada,
                diretorio_saida=diretorio_saida,
                nome_pdf=nome_pdf,
                metadados=metadados,
                incluir_pdfs=bool(var_incluir_pdfs.get()),
            )
            registrar_no_historico(CHAVE_HISTORICO_ENTRADA, diretorio_entrada)
            registrar_no_historico(CHAVE_HISTORICO_SAIDA, diretorio_saida)
            mensagem = f"PDF criado em: {resultado['caminho']} ({resultado['paginas']} página(s))"
            if resultado["ignorados"]:
                mensagem += f" | {len(resultado['ignorados'])} arquivo(s) foram ignorados"
            status_label.configure(text=mensagem)
            atualizar_previa()
        except FileExistsError:
            status_label.configure(
                text="A geração foi cancelada para não substituir o PDF existente."
            )
        except FileNotFoundError as exc:
            status_label.configure(text=str(exc))
        except ValueError as exc:
            status_label.configure(text=str(exc))
        except Exception as exc:
            registrar_excecao("Falha ao compilar documentos")
            status_label.configure(
                text="Não foi possível compilar os arquivos. Verifique se há arquivos válidos na pasta de entrada."
            )

    ctk.CTkLabel(frame, text="Pasta com as imagens e/ou PDFs").pack(pady=10)
    entry_entrada = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=250)
    entry_entrada.pack()
    ctk.CTkButton(
        frame,
        text="Escolher Pasta",
        command=lambda: escolher_pasta(entry_entrada, CHAVE_HISTORICO_ENTRADA),
    ).pack(pady=10)

    ctk.CTkLabel(frame, text="Pasta de saída").pack(pady=10)
    entry_saida = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=250)
    entry_saida.pack()
    ctk.CTkButton(
        frame,
        text="Escolher Pasta",
        command=lambda: escolher_pasta(entry_saida, CHAVE_HISTORICO_SAIDA),
    ).pack(pady=10)

    ctk.CTkLabel(frame, text="Nome do PDF final").pack(pady=10)
    entry_nome_pdf = ctk.CTkEntry(frame, placeholder_text="livro_final.pdf", width=250)
    entry_nome_pdf.insert(0, ARQUIVO_PADRAO_SAIDA)
    entry_nome_pdf.pack()

    var_incluir_pdfs = ctk.BooleanVar(value=True)
    ctk.CTkCheckBox(
        frame,
        text="Incluir PDFs encontrados na pasta",
        variable=var_incluir_pdfs,
        command=atualizar_previa,
    ).pack(pady=10)

    ctk.CTkLabel(frame, text="Título do livro").pack(pady=10)
    entry_metadado_titulo = ctk.CTkEntry(frame, placeholder_text="Insira o título para os metadados...", width=250)
    entry_metadado_titulo.pack()

    ctk.CTkLabel(frame, text="Autor do livro").pack(pady=10)
    entry_metadado_autor = ctk.CTkEntry(frame, placeholder_text="Insira o autor para os metadados...", width=250)
    entry_metadado_autor.pack()

    ctk.CTkLabel(frame, text="Assunto do livro").pack(pady=10)
    entry_metadado_assunto = ctk.CTkEntry(frame, placeholder_text="Insira o assunto para os metadados...", width=250)
    entry_metadado_assunto.pack()

    ctk.CTkLabel(frame, text="Palavras-chave").pack(pady=10)
    entry_metadado_palavraschave = ctk.CTkEntry(frame, placeholder_text="Insira as palavras-chave para os metadados...", width=250)
    entry_metadado_palavraschave.pack()

    ctk.CTkLabel(frame, text="Prévia dos arquivos que serão processados").pack(pady=10)
    preview_box = ctk.CTkTextbox(frame, width=500, height=140)
    preview_box.pack(pady=5)
    preview_box.configure(state="disabled")

    status_label = ctk.CTkLabel(frame, text="", wraplength=320)
    status_label.pack(pady=10)

    botoes_frame = ctk.CTkFrame(frame)
    botoes_frame.pack(pady=5)
    ctk.CTkButton(botoes_frame, text="Compilar", command=compilar_imagens).pack(side="left", padx=5)
    ctk.CTkButton(botoes_frame, text="Abrir pasta de saída", command=abrir_saida).pack(side="left", padx=5)

    preencher_com_historico()
    atualizar_previa()
