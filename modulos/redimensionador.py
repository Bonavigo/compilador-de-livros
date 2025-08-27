import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import os

def criar_aba(tabview):
    aba_redimensionador = tabview.add("Redimensionador")
    frame = ctk.CTkScrollableFrame(aba_redimensionador, width=560, height=460)
    frame.pack(padx=5, pady=5, fill="both", expand=True)
    
    # --- Funções internas específicas da aba ---
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
    
    def redimensionar_imagens():
        status_label.configure(text=f"Verificando diretórios...")
        status_label.update_idletasks()
        diretorio_entrada = entry_entrada.get()
        diretorio_saida = entry_saida.get()
        
        os.makedirs(diretorio_saida, exist_ok=True)
        
        status_label.configure(text=f"Configurando tamanhos e a qualidade...")
        status_label.update_idletasks()
        
        tamanho_desejado = tamanho.get()
        if tamanho_desejado == "50%":
            tamanho_desejado = 2
        elif tamanho_desejado == "33%":
            tamanho_desejado = 3
        elif tamanho_desejado == "25%":
            tamanho_desejado = 4
        else:
            tamanho_desejado = 5

        qualidade_desejada = int(qualidade.get())
        
        arquivos = [f for f in os.listdir(diretorio_entrada) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        total = len(arquivos)

        for i, nome_arquivo in enumerate(arquivos, start=1):
            caminho_original = os.path.join(diretorio_entrada, nome_arquivo)
            caminho_novo = os.path.join(diretorio_saida, nome_arquivo)

            with Image.open(caminho_original) as img:
                largura, altura = img.size
                nova_img = img.resize((largura // tamanho_desejado, altura // tamanho_desejado), Image.LANCZOS)
                nova_img.convert("RGB").save(caminho_novo, quality=qualidade_desejada, optimize=True)

            status_label.configure(text=f"Processando {i} de {total} imagens...")
            status_label.update_idletasks()
            
        status_label.configure(text=f"Imagens redimensionadas com sucesso em: {diretorio_saida}")
        status_label.update_idletasks()
    
    ctk.CTkLabel(frame, text="Pasta com as imagens").pack(pady=10)
    entry_entrada = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=250)
    entry_entrada.pack()
    ctk.CTkButton(frame, text="Escolher Pasta", command=escolher_pasta_entrada).pack(pady=10)

    ctk.CTkLabel(frame, text="Pasta de saída").pack(pady=10)
    entry_saida = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=250)
    entry_saida.pack()
    ctk.CTkButton(frame, text="Escolher Pasta", command=escolher_pasta_saida).pack(pady=10)

    ctk.CTkLabel(frame, text="Valor da redução").pack(pady=10)
    opcoes = ["50%", "33%", "25%", "20%"]
    tamanho = ctk.CTkComboBox(frame, values=opcoes, state="readonly")
    tamanho.set("50%")
    tamanho.pack(pady=0)
    
    ctk.CTkLabel(frame, text="Qualidade da imagem").pack(pady=10)
    opcoes = ["100", "95", "90", "85", "80", "75", "70"]
    qualidade = ctk.CTkComboBox(frame, values=opcoes, state="readonly")
    qualidade.set("90")
    qualidade.pack(pady=0)
    
    status_label = ctk.CTkLabel(frame, text="", wraplength=250)
    status_label.pack(pady=10)
    
    ctk.CTkButton(frame, text="Redimensionar", command=redimensionar_imagens).pack(pady=0)