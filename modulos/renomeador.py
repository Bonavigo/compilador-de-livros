import customtkinter as ctk
from tkinter import filedialog
import os

def criar_aba(tabview):
    aba_renomeador = tabview.add("Renomeador")
    frame = ctk.CTkScrollableFrame(aba_renomeador, width=560, height=460)
    frame.pack(padx=5, pady=5, fill="both", expand=True)
    
    def escolher_pasta_entrada():
        pasta = filedialog.askdirectory()
        if pasta:
            entry_entrada.delete(0, "end")
            entry_entrada.insert(0, pasta)

    def escolher_pasta_saida():
        pasta = filedialog.askdirectory()
        if pasta:
            entry_saida.delete(0, "end")
            entry_saida.insert(0, pasta)
            
    def pegar_numero_de_arquivos(filename):
        name, _ = os.path.splitext(filename)
        try:
            return int(name)
        except ValueError:
            return float('inf')
            
    def renomear_arquivos():
        pasta_entrada = entry_entrada.get()
        pasta_saida = entry_saida.get()

        if not os.path.exists(pasta_saida):
            os.makedirs(pasta_saida)
        
        try:
            last_number = int(entry_ultimo_num.get())
        except ValueError:
            status_label.configure(text="Número inválido!")
            status_label.update_idletasks()
            return

        if not pasta_entrada:
            status_label.configure(text="Escolha uma pasta!")
            status_label.update_idletasks()
            return

        arquivos = [f for f in os.listdir(pasta_entrada) if os.path.isfile(os.path.join(pasta_entrada, f))]
        arquivos = sorted(arquivos, key=pegar_numero_de_arquivos)

        current_number = last_number + 1
        renomeados = 0

        for old_name in arquivos:
            old_path = os.path.join(pasta_entrada, old_name)
            name, ext = os.path.splitext(old_name)

            try:
                int(name)  # só arquivos com nome numérico
            except ValueError:
                continue

            new_name = f"{current_number}{ext}"
            new_path = os.path.join(pasta_saida, new_name)

            os.rename(old_path, new_path)
            current_number += 1
            renomeados += 1

        status_label.configure(text=f"Renomeados {renomeados} arquivos.")
    
    ctk.CTkLabel(frame, text="Pasta com as imagens").pack(pady=10)
    entry_entrada = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=250)
    entry_entrada.pack()
    ctk.CTkButton(frame, text="Escolher Pasta", command=escolher_pasta_entrada).pack(pady=10)

    ctk.CTkLabel(frame, text="Pasta de saída").pack(pady=10)
    entry_saida = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=250)
    entry_saida.pack()
    ctk.CTkButton(frame, text="Escolher Pasta", command=escolher_pasta_saida).pack(pady=10)
    
    ctk.CTkLabel(frame, text="Último número já usado").pack(pady=10)
    entry_ultimo_num = ctk.CTkEntry(frame, width=100)
    entry_ultimo_num.pack()
    
    status_label = ctk.CTkLabel(frame, text="", wraplength=400)
    status_label.pack(pady=10)

    ctk.CTkButton(frame, text="Renomear", command=renomear_arquivos).pack(pady=10)