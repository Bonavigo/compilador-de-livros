from __future__ import annotations

import os
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

from modulos.servicos import (
    abrir_pasta_no_explorador,
    listar_arquivos_por_extensao,
    registrar_excecao,
    registrar_evento,
    registrar_no_historico,
    obter_historico,
)

EXTENSOES_IMAGEM = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")
CHAVE_HISTORICO_ENTRADA = "redimensionador_entrada"
CHAVE_HISTORICO_SAIDA = "redimensionador_saida"


def _atualizar_texto_previa(textbox: ctk.CTkTextbox, diretorio: str, arquivos: list[str]) -> None:
    textbox.configure(state="normal")
    textbox.delete("1.0", "end")

    if not diretorio or not arquivos:
        textbox.insert("end", "Nenhum arquivo de imagem encontrado.\n")
    else:
        textbox.insert("end", f"Diretório: {diretorio}\nTotal: {len(arquivos)}\n\n")
        limite = 120
        for nome in arquivos[:limite]:
            textbox.insert("end", f"- {nome}\n")
        if len(arquivos) > limite:
            textbox.insert("end", f"\n... e mais {len(arquivos) - limite} arquivo(s)\n")

    textbox.configure(state="disabled")


def _divisor_por_reducao(valor: str) -> int:
    mapa = {
        "100%": 1,
        "50%": 2,
        "33%": 3,
        "25%": 4,
        "20%": 5,
    }
    return mapa.get(valor, 2)


def redimensionar_pasta(
    diretorio_entrada: str,
    diretorio_saida: str,
    reducao: str,
    qualidade: int,
    progress_callback=None,
) -> dict[str, object]:
    if not diretorio_entrada or not diretorio_saida:
        raise ValueError("Os diretórios de entrada e saída são obrigatórios.")

    arquivos = listar_arquivos_por_extensao(diretorio_entrada, extensoes=EXTENSOES_IMAGEM)
    if not arquivos:
        raise FileNotFoundError("Nenhuma imagem compatível foi encontrada na pasta de entrada.")

    divisor = _divisor_por_reducao(reducao)
    os.makedirs(diretorio_saida, exist_ok=True)
    registrar_evento(
        f"Redimensionamento iniciado. Entrada={diretorio_entrada} Saída={diretorio_saida} Arquivos={len(arquivos)}"
    )

    arquivos_processados: list[str] = []
    arquivos_falhados: list[str] = []
    for indice, nome_arquivo in enumerate(arquivos, start=1):
        caminho_original = os.path.join(diretorio_entrada, nome_arquivo)
        nome_base, _ = os.path.splitext(nome_arquivo)
        caminho_saida = os.path.join(diretorio_saida, f"{nome_base}.jpg")

        try:
            with Image.open(caminho_original) as img:
                largura, altura = img.size
                nova_largura = max(1, largura // divisor)
                nova_altura = max(1, altura // divisor)
                if nova_largura <= 0 or nova_altura <= 0:
                    raise ValueError(
                        f"A imagem '{nome_arquivo}' ficou pequena demais para a redução selecionada."
                    )

                if img.mode in ("RGBA", "LA") or "transparency" in img.info:
                    registrar_evento(
                        f"Transparência será perdida ao salvar em JPEG: {caminho_original}",
                        nivel="warning",
                    )

                imagem_redimensionada = img.resize((nova_largura, nova_altura), Image.LANCZOS)
                imagem_redimensionada.convert("RGB").save(
                    caminho_saida,
                    format="JPEG",
                    quality=qualidade,
                    optimize=True,
                )
                arquivos_processados.append(caminho_saida)
        except Exception as exc:
            arquivos_falhados.append(nome_arquivo)
            registrar_excecao(f"Falha ao redimensionar {caminho_original}")
            registrar_evento(
                f"Arquivo ignorado no redimensionamento: {caminho_original}",
                nivel="warning",
            )
        finally:
            if progress_callback:
                progress_callback(indice, len(arquivos), nome_arquivo)

    if not arquivos_processados:
        raise RuntimeError("Nenhuma imagem pôde ser redimensionada.")

    registrar_evento(
        f"Redimensionamento concluído. Saída={diretorio_saida} Arquivos={len(arquivos_processados)} Ignorados={len(arquivos_falhados)}"
    )
    return {
        "processados": arquivos_processados,
        "falhados": arquivos_falhados,
    }


def criar_aba(tabview):
    aba_redimensionador = tabview.add("Redimensionador")
    frame = ctk.CTkScrollableFrame(aba_redimensionador, width=560, height=460)
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
        arquivos = listar_arquivos_por_extensao(diretorio, extensoes=EXTENSOES_IMAGEM)
        _atualizar_texto_previa(preview_box, diretorio, arquivos)

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

    def atualizar_progresso(atual: int, total: int, nome_arquivo: str):
        progresso = atual / total if total else 0
        progress_bar.set(progresso)
        status_label.configure(text=f"Processando {atual} de {total}: {nome_arquivo}")
        status_label.update_idletasks()

    def redimensionar_imagens():
        diretorio_entrada = entry_entrada.get().strip()
        diretorio_saida = entry_saida.get().strip()

        status_label.configure(text="Verificando diretórios...")
        status_label.update_idletasks()

        try:
            resultado = redimensionar_pasta(
                diretorio_entrada=diretorio_entrada,
                diretorio_saida=diretorio_saida,
                reducao=tamanho.get(),
                qualidade=int(qualidade.get()),
                progress_callback=atualizar_progresso,
            )
            registrar_no_historico(CHAVE_HISTORICO_ENTRADA, diretorio_entrada)
            registrar_no_historico(CHAVE_HISTORICO_SAIDA, diretorio_saida)
            progress_bar.set(1 if resultado["processados"] else 0)
            mensagem = f"Imagens redimensionadas com sucesso em: {diretorio_saida} ({len(resultado['processados'])} arquivo(s))"
            if resultado["falhados"]:
                mensagem += f" | {len(resultado['falhados'])} arquivo(s) foram ignorados"
            status_label.configure(text=mensagem)
            atualizar_previa()
        except ValueError as exc:
            status_label.configure(text=str(exc))
            progress_bar.set(0)
        except FileNotFoundError as exc:
            status_label.configure(text=str(exc))
            progress_bar.set(0)
        except RuntimeError as exc:
            status_label.configure(text=str(exc))
            progress_bar.set(0)
        except Exception as exc:
            registrar_excecao("Falha ao redimensionar imagens")
            status_label.configure(
                text="Não foi possível redimensionar as imagens. Verifique se a pasta contém arquivos válidos."
            )
            progress_bar.set(0)

    ctk.CTkLabel(frame, text="Pasta com as imagens").pack(pady=10)
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

    ctk.CTkLabel(frame, text="Valor da redução").pack(pady=10)
    opcoes = ["100%", "50%", "33%", "25%", "20%"]
    tamanho = ctk.CTkComboBox(frame, values=opcoes, state="readonly")
    tamanho.set("50%")
    tamanho.pack(pady=0)

    ctk.CTkLabel(frame, text="Qualidade da imagem").pack(pady=10)
    opcoes = ["100", "95", "90", "85", "80", "75", "70"]
    qualidade = ctk.CTkComboBox(frame, values=opcoes, state="readonly")
    qualidade.set("90")
    qualidade.pack(pady=0)

    ctk.CTkLabel(frame, text="Prévia dos arquivos que serão processados").pack(pady=10)
    preview_box = ctk.CTkTextbox(frame, width=500, height=140)
    preview_box.pack(pady=5)
    preview_box.configure(state="disabled")

    progress_bar = ctk.CTkProgressBar(frame, width=420)
    progress_bar.pack(pady=5)
    progress_bar.set(0)

    status_label = ctk.CTkLabel(frame, text="", wraplength=320)
    status_label.pack(pady=10)

    botoes_frame = ctk.CTkFrame(frame)
    botoes_frame.pack(pady=5)
    ctk.CTkButton(botoes_frame, text="Redimensionar", command=redimensionar_imagens).pack(side="left", padx=5)
    ctk.CTkButton(botoes_frame, text="Abrir pasta de saída", command=abrir_saida).pack(side="left", padx=5)

    preencher_com_historico()
    atualizar_previa()
