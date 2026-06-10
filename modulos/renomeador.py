from __future__ import annotations

import os
import shutil
from tkinter import filedialog, messagebox

import customtkinter as ctk

from modulos.servicos import (
    abrir_pasta_no_explorador,
    extrair_numero,
    registrar_excecao,
    registrar_evento,
    registrar_no_historico,
    obter_historico,
)

CHAVE_HISTORICO_ENTRADA = "renomeador_entrada"
CHAVE_HISTORICO_SAIDA = "renomeador_saida"


def _atualizar_texto_previa(textbox: ctk.CTkTextbox, diretorio: str, arquivos: list[str]) -> None:
    textbox.configure(state="normal")
    textbox.delete("1.0", "end")

    if not diretorio or not arquivos:
        textbox.insert("end", "Nenhum arquivo numerado encontrado.\n")
    else:
        textbox.insert("end", f"Diretório: {diretorio}\nTotal numerado: {len(arquivos)}\n\n")
        limite = 120
        for nome in arquivos[:limite]:
            textbox.insert("end", f"- {nome}\n")
        if len(arquivos) > limite:
            textbox.insert("end", f"\n... e mais {len(arquivos) - limite} arquivo(s)\n")

    textbox.configure(state="disabled")


def renomear_arquivos_pasta(
    pasta_entrada: str,
    pasta_saida: str,
    ultimo_numero: int,
    usar_mesmo_diretorio: bool = False,
    confirmar_sobrescrita=None,
) -> dict[str, int]:
    if not pasta_entrada:
        raise ValueError("Escolha uma pasta de entrada.")
    if not pasta_saida:
        raise ValueError("Escolha uma pasta de saída.")

    arquivos = [
        nome
        for nome in os.listdir(pasta_entrada)
        if os.path.isfile(os.path.join(pasta_entrada, nome))
    ]
    arquivos = sorted(arquivos, key=extrair_numero)
    arquivos_validos = [nome for nome in arquivos if extrair_numero(nome) != float("inf")]
    arquivos_ignorados = len(arquivos) - len(arquivos_validos)

    if not arquivos_validos:
        raise FileNotFoundError("Nenhum arquivo com número no nome foi encontrado.")

    os.makedirs(pasta_saida, exist_ok=True)
    current_number = ultimo_numero + 1
    destinos = []
    for nome in arquivos_validos:
        _, ext = os.path.splitext(nome)
        destinos.append(f"{current_number}{ext.lower()}")
        current_number += 1

    nomes_origem = set(arquivos_validos)
    conflitos = []
    for destino in destinos:
        caminho_destino = os.path.join(pasta_saida, destino)
        if os.path.exists(caminho_destino):
            if usar_mesmo_diretorio:
                if os.path.basename(caminho_destino) not in nomes_origem:
                    conflitos.append(caminho_destino)
            else:
                conflitos.append(caminho_destino)

    if conflitos and confirmar_sobrescrita is not None:
        if not confirmar_sobrescrita(conflitos):
            raise FileExistsError("Operação cancelada para evitar sobrescrita de arquivos existentes.")
    elif conflitos:
        raise FileExistsError(
            "Um ou mais arquivos de destino já existem. Escolha outra pasta de saída ou confirme a substituição."
        )

    registrar_evento(
        f"Renomeação iniciada. Entrada={pasta_entrada} Saída={pasta_saida} Arquivos={len(arquivos_validos)}"
    )

    renomeados = 0
    if usar_mesmo_diretorio:
        temporarios = []
        for indice, nome_original in enumerate(arquivos_validos):
            caminho_original = os.path.join(pasta_entrada, nome_original)
            _, ext = os.path.splitext(nome_original)
            nome_temp = f".__tmp_renomeador__{indice}__{nome_original}"
            caminho_temp = os.path.join(pasta_saida, nome_temp)
            os.rename(caminho_original, caminho_temp)
            temporarios.append((caminho_temp, f"{ultimo_numero + 1 + indice}{ext.lower()}"))

        for caminho_temp, nome_final in temporarios:
            caminho_final = os.path.join(pasta_saida, nome_final)
            os.replace(caminho_temp, caminho_final)
            renomeados += 1
    else:
        for indice, nome_original in enumerate(arquivos_validos):
            caminho_original = os.path.join(pasta_entrada, nome_original)
            _, ext = os.path.splitext(nome_original)
            caminho_final = os.path.join(pasta_saida, f"{ultimo_numero + 1 + indice}{ext.lower()}")
            shutil.copy2(caminho_original, caminho_final)
            renomeados += 1

    registrar_evento(
        f"Renomeação concluída. Saída={pasta_saida} Arquivos={renomeados} Ignorados={arquivos_ignorados}"
    )
    return {
        "renomeados": renomeados,
        "ignorados": arquivos_ignorados,
    }


def criar_aba(tabview):
    aba_renomeador = tabview.add("Renomeador")
    frame = ctk.CTkScrollableFrame(aba_renomeador, width=560, height=460)
    frame.pack(padx=5, pady=5, fill="both", expand=True)

    def escolher_pasta(entry_widget, chave_historico: str):
        pasta = filedialog.askdirectory()
        if pasta:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, pasta)
            registrar_no_historico(chave_historico, pasta)
            if entry_widget is entry_entrada and chk_mesmo_dir.get() == 1:
                atualizar_saida_mesmo_dir()
            atualizar_previa()

    def atualizar_previa():
        diretorio = entry_entrada.get()
        arquivos = []
        if diretorio and os.path.isdir(diretorio):
            arquivos = [
                nome
                for nome in os.listdir(diretorio)
                if os.path.isfile(os.path.join(diretorio, nome))
                and extrair_numero(nome) != float("inf")
            ]
            arquivos = sorted(arquivos, key=extrair_numero)
        _atualizar_texto_previa(preview_box, diretorio, arquivos)

    def preencher_com_historico():
        historico_entrada = obter_historico(CHAVE_HISTORICO_ENTRADA)
        historico_saida = obter_historico(CHAVE_HISTORICO_SAIDA)
        if historico_entrada and not entry_entrada.get():
            entry_entrada.insert(0, historico_entrada[0])
        if historico_saida and not entry_saida.get():
            entry_saida.insert(0, historico_saida[0])

    def atualizar_saida_mesmo_dir():
        if chk_mesmo_dir.get() == 1:
            pasta_entrada = entry_entrada.get().strip()
            if pasta_entrada:
                entry_saida.configure(state="normal")
                entry_saida.delete(0, "end")
                entry_saida.insert(0, pasta_entrada)
                entry_saida.configure(state="disabled")
                button_saida.configure(state="disabled")
                aviso_mesmodir_label.configure(
                    text="Ao usar a mesma pasta, os arquivos serão renomeados em dois passos para evitar conflito interno."
                )
            else:
                aviso_mesmodir_label.configure(
                    text="Escolha a pasta de entrada antes de ativar o uso da mesma pasta."
                )
                chk_mesmo_dir.deselect()
        else:
            entry_saida.configure(state="normal")
            button_saida.configure(state="normal")
            entry_saida.delete(0, "end")
            aviso_mesmodir_label.configure(text="")

    def abrir_saida():
        if abrir_pasta_no_explorador(entry_saida.get()):
            status_label.configure(text="Pasta de saída aberta no explorador.")
        else:
            status_label.configure(text="Não foi possível abrir a pasta de saída.")

    def confirmar_sobrescrita(conflitos: list[str]) -> bool:
        nomes = "\n".join(os.path.basename(caminho) for caminho in conflitos[:8])
        retorno = messagebox.askyesno(
            "Confirmar sobrescrita",
            "Alguns arquivos já existem na pasta de saída.\n\n"
            f"{nomes}\n\nDeseja substituir esses arquivos?",
        )
        return bool(retorno)

    def renomear_arquivos():
        pasta_entrada = entry_entrada.get().strip()
        pasta_saida = entry_saida.get().strip()

        if not pasta_entrada:
            status_label.configure(text="Escolha uma pasta de entrada.")
            return

        if not pasta_saida:
            status_label.configure(text="Escolha uma pasta de saída.")
            return

        try:
            last_number = int(entry_ultimo_num.get())
        except ValueError:
            status_label.configure(text="O número inicial informado é inválido.")
            return

        try:
            resultado = renomear_arquivos_pasta(
                pasta_entrada=pasta_entrada,
                pasta_saida=pasta_saida,
                ultimo_numero=last_number,
                usar_mesmo_diretorio=bool(chk_mesmo_dir.get()),
                confirmar_sobrescrita=confirmar_sobrescrita,
            )
            registrar_no_historico(CHAVE_HISTORICO_ENTRADA, pasta_entrada)
            registrar_no_historico(CHAVE_HISTORICO_SAIDA, pasta_saida)
            status_label.configure(
                text=(
                    f"{resultado['renomeados']} arquivos renomeados. "
                    f"{resultado['ignorados']} arquivo(s) foram ignorados por não terem número no nome."
                )
            )
            atualizar_previa()
        except FileExistsError as exc:
            status_label.configure(text=str(exc))
        except FileNotFoundError as exc:
            status_label.configure(text=str(exc))
        except ValueError as exc:
            status_label.configure(text=str(exc))
        except Exception as exc:
            registrar_excecao("Falha ao renomear arquivos")
            status_label.configure(
                text="Não foi possível renomear os arquivos. Verifique se a pasta de entrada é válida."
            )

    ctk.CTkLabel(frame, text="Pasta com os arquivos").pack(pady=10)
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
    button_saida = ctk.CTkButton(
        frame,
        text="Escolher Pasta",
        command=lambda: escolher_pasta(entry_saida, CHAVE_HISTORICO_SAIDA),
    )
    button_saida.pack(pady=10)

    chk_mesmo_dir = ctk.CTkCheckBox(
        frame,
        text="Usar a mesma pasta de entrada",
        command=atualizar_saida_mesmo_dir,
    )
    chk_mesmo_dir.pack(pady=5)

    aviso_mesmodir_label = ctk.CTkLabel(frame, text="", wraplength=400)
    aviso_mesmodir_label.pack(pady=0)

    ctk.CTkLabel(frame, text="Número que deseja iniciar a contagem").pack(pady=10)
    entry_ultimo_num = ctk.CTkEntry(frame, width=100)
    entry_ultimo_num.pack()

    ctk.CTkLabel(frame, text="Prévia dos arquivos que serão processados").pack(pady=10)
    preview_box = ctk.CTkTextbox(frame, width=500, height=140)
    preview_box.pack(pady=5)
    preview_box.configure(state="disabled")

    status_label = ctk.CTkLabel(frame, text="", wraplength=400)
    status_label.pack(pady=10)

    botoes_frame = ctk.CTkFrame(frame)
    botoes_frame.pack(pady=5)
    ctk.CTkButton(botoes_frame, text="Renomear", command=renomear_arquivos).pack(side="left", padx=5)
    ctk.CTkButton(botoes_frame, text="Abrir pasta de saída", command=abrir_saida).pack(side="left", padx=5)

    preencher_com_historico()
    atualizar_previa()
