import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import os, re

def criar_aba(tabview):
    aba_compilador = tabview.add("Compilador")
    frame = ctk.CTkScrollableFrame(aba_compilador, width=560, height=460)
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

    def extrair_numero(nome):
        numeros = re.findall(r'\d+', nome)
        return int(numeros[0]) if numeros else float('inf')
    
    def limpar_campos():
        entry_entrada.delete(0, "end")
        entry_saida.delete(0, "end")
        entry_metadado_titulo.delete(0, "end")
        entry_metadado_autor.delete(0, "end")
        entry_metadado_assunto.delete(0, "end")
        entry_metadado_palavraschave.delete(0, "end")

    def compilar_imagens():
        status_label.configure(text="Iniciando compilação...")
        status_label.update_idletasks()
        diretorio_entrada = entry_entrada.get()
        diretorio_saida = entry_saida.get()
        if not diretorio_entrada or not diretorio_saida:
            status_label.configure(text="Faltam diretórios.")
            status_label.update_idletasks()
            return

        nome_pdf = "livro_final.pdf"
        
        status_label.configure(text="Colhendo metadados...")
        status_label.update_idletasks()
        metadados = {
            "/Title": entry_metadado_titulo.get(),
            "/Author": entry_metadado_autor.get(),
            "/Subject": entry_metadado_assunto.get(),
            "/Keywords": entry_metadado_palavraschave.get(),
        }

        os.makedirs(diretorio_saida, exist_ok=True)
        nomes_arquivos = sorted(
            [f for f in os.listdir(diretorio_entrada) if f.lower().endswith(('.jpg', '.jpeg', '.png'))],
            key=extrair_numero
        )
        imagens = [Image.open(os.path.join(diretorio_entrada, f)).convert("RGB") for f in nomes_arquivos]

        if not imagens:
            status_label.configure(text="Nenhuma imagem encontrada.")
            status_label.update_idletasks()
            return

        status_label.configure(text="Criando arquivo temporário...")
        status_label.update_idletasks()
        caminho_pdf_temp = os.path.join(diretorio_saida, "temp.pdf")
        
        status_label.configure(text="Adicionando páginas...")
        status_label.update_idletasks()
        imagens[0].save(caminho_pdf_temp, save_all=True, append_images=imagens[1:])
        reader = PdfReader(caminho_pdf_temp)
        writer = PdfWriter()
        
        status_label.configure(text="Adicionando metadados...")
        status_label.update_idletasks()
        for pagina in reader.pages:
            writer.add_page(pagina)
        writer.add_metadata(metadados)

        caminho_pdf_final = os.path.join(diretorio_saida, nome_pdf)
        with open(caminho_pdf_final, "wb") as f_out:
            writer.write(f_out)
        os.remove(caminho_pdf_temp)

        limpar_campos()
        status_label.configure(text=f"PDF criado em: {caminho_pdf_final}")
        status_label.update_idletasks()

    # Campos
    ctk.CTkLabel(frame, text="Pasta com as imagens").pack(pady=10)
    entry_entrada = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=250)
    entry_entrada.pack()
    ctk.CTkButton(frame, text="Escolher Pasta", command=escolher_pasta_entrada).pack(pady=10)

    ctk.CTkLabel(frame, text="Pasta de saída").pack(pady=10)
    entry_saida = ctk.CTkEntry(frame, placeholder_text="Insira o diretório...", width=250)
    entry_saida.pack()
    ctk.CTkButton(frame, text="Escolher Pasta", command=escolher_pasta_saida).pack(pady=10)

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

    status_label = ctk.CTkLabel(frame, text="", wraplength=250)
    status_label.pack(pady=10)

    ctk.CTkButton(frame, text="Compilar", command=compilar_imagens).pack(pady=0)