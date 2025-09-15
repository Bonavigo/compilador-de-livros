import customtkinter as ctk
from tkinter import filedialog
import os
import shutil
import re

def criar_aba(tabview):
    aba_renomeador = tabview.add("Renomeador")
    frame = ctk.CTkScrollableFrame(aba_renomeador, width=560, height=460)
    frame.pack(padx=5, pady=5, fill="both", expand=True)

    def escolher_pasta(entry_widget):
        pasta = filedialog.askdirectory()
        if pasta:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, pasta)
            
    def toggle_mesmo_diretorio():
        if (chk_mesmo_dir.get() == 1):
            pasta_entrada = entry_entrada.get()
            entry_saida.delete(0, "end")
            entry_saida.insert(0, pasta_entrada)
            entry_saida.configure(state="disabled")
            button_saida.configure(state="disabled")
            aviso_mesmodir_label.configure(text="ATENÇÃO: Caso o número fornecido no campo abaixo seja menor que o número de arquivos, o programa não conseguirá renomeá-los, pois dois arquivos ficarão com o mesmo nome.")
        else:
            entry_saida.configure(state="normal")
            button_saida.configure(state="normal")
            entry_saida.delete(0, "end")
            aviso_mesmodir_label.configure(text="")

    def extrair_numero(nome):
        numeros = re.findall(r'\d+', nome)
        return int(numeros[0]) if numeros else float('inf')
    
    def limpar_campos():
        entry_entrada.delete(0, "end")
        entry_saida.delete(0, "end")
        chk_mesmo_dir.delete(0, "end")
        aviso_mesmodir_label.configure(text="")
        entry_ultimo_num.delete(0, "end")

    def renomear_arquivos():
        pasta_entrada = entry_entrada.get()
        pasta_saida = entry_saida.get()

        if not pasta_entrada:
            status_label.configure(text="Escolha uma pasta de entrada!")
            status_label.update_idletasks()
            return

        if not pasta_saida:
            status_label.configure(text="Escolha uma pasta de saída!")
            status_label.update_idletasks()
            return

        os.makedirs(pasta_saida, exist_ok=True)

        try:
            last_number = int(entry_ultimo_num.get())
        except ValueError:
            status_label.configure(text="Último número usado inválido!")
            status_label.update_idletasks()
            return

        arquivos = [f for f in os.listdir(pasta_entrada) if os.path.isfile(os.path.join(pasta_entrada, f))]
        arquivos = sorted(arquivos, key=extrair_numero)

        current_number = last_number + 1
        renomeados = 0

        for old_name in arquivos:
            old_path = os.path.join(pasta_entrada, old_name)
            _, ext = os.path.splitext(old_name)

            if extrair_numero(old_name) == float("inf"):
                continue

            new_name = f"{current_number}{ext.lower()}"
            new_path = os.path.join(pasta_saida, new_name)

            if (chk_mesmo_dir.get() == 1):
                try:
                    if extrair_numero(old_name) == float("inf"):
                        continue

                    new_name = f"{current_number}{ext.lower()}"
                    new_path = os.path.join(pasta_saida, new_name)

                    os.rename(old_path, new_path)
                    current_number += 1
                    renomeados += 1
                    
                    status_label.configure(text=f"Copiando... {renomeados} feito(s)")
                    status_label.update_idletasks()
                    
                except Exception as e:
                    status_label.configure(text=f"Erro ao copiar {old_name}: {e}")
                    status_label.update_idletasks()
            
            else:
                try:
                    shutil.copy2(old_path, new_path)
                    renomeados += 1
                    current_number += 1

                    status_label.configure(text=f"Copiando... {renomeados} feito(s)")
                    status_label.update_idletasks()

                except Exception as e:
                    status_label.configure(text=f"Erro ao copiar {old_name}: {e}")
                    status_label.update_idletasks()

        limpar_campos()
        status_label.configure(text=f"{renomeados} arquivos renomeados.")

    # --- Interface ---
    ctk.CTkLabel(frame, text="Pasta com as imagens").pack(pady=10)
    entry_entrada = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=250)
    entry_entrada.pack()
    ctk.CTkButton(frame, text="Escolher Pasta", command=lambda: escolher_pasta(entry_entrada)).pack(pady=10)

    ctk.CTkLabel(frame, text="Pasta de saída").pack(pady=10)
    entry_saida = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=250)
    entry_saida.pack()
    button_saida = ctk.CTkButton(frame, text="Escolher Pasta", command=lambda: escolher_pasta(entry_saida))
    button_saida.pack(pady=10)
    
    chk_mesmo_dir = ctk.CTkCheckBox(frame, text="Usar a mesma pasta de entrada", command=toggle_mesmo_diretorio)
    chk_mesmo_dir.pack(pady=5)
    
    aviso_mesmodir_label = ctk.CTkLabel(frame, text="", wraplength=400)
    aviso_mesmodir_label.pack(pady=0)

    ctk.CTkLabel(frame, text="Número que deseja iniciar a contagem").pack(pady=10)
    entry_ultimo_num = ctk.CTkEntry(frame, width=100)
    entry_ultimo_num.pack()

    status_label = ctk.CTkLabel(frame, text="", wraplength=400)
    status_label.pack(pady=10)

    ctk.CTkButton(frame, text="Renomear", command=renomear_arquivos).pack(pady=10)
