import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import os
import re

# Configuração da aparência
ctk.set_appearance_mode('dark')

# Criação da janela principal
app = ctk.CTk()
app.title("Compilador de livros")
app.geometry('350x500')

# Criar frame rolável
frame_compilador = ctk.CTkScrollableFrame(app, width=330, height=480)
frame_compilador.pack(padx=10, pady=10, fill="both", expand=True)

# Criação das funcionalidades
# Escolher pasta de entrada
def escolher_pasta_entrada():
    pasta = filedialog.askdirectory()
    if pasta:
        entry_entrada.delete(0, "end")
        entry_entrada.insert(0, pasta)

# Escolher pasta de saída
def escolher_pasta_saida():
    pasta = filedialog.askdirectory()
    if pasta:
        entry_saida.delete(0, "end")
        entry_saida.insert(0, pasta)

def extrair_numero(nome):
    numeros = re.findall(r'\d+', nome)
    return int(numeros[0]) if numeros else float('inf')

def limpar_campos():
    # Diretórios
    entry_entrada.delete(0, "end")
    entry_saida.delete(0, "end")
    
    # Metadados
    entry_metadado_titulo.delete(0, "end")
    entry_metadado_autor.delete(0, "end")
    entry_metadado_assunto.delete(0, "end")
    entry_metadado_palavraschave.delete(0, "end")

# Compilar imagens
def compilar_imagens():
    status_label.configure(text="⏳ Iniciando compilação...")
    app.update()
    diretorio_entrada = entry_entrada.get()
    diretorio_saida = entry_saida.get()
    
    if not diretorio_entrada or not diretorio_saida:
        status_label.configure(text=f"Faltam diretórios.")
        return
    
    nome_pdf = 'livro_final.pdf'
    
    status_label.configure(text=f"Colhendo metatados...")
    app.update()
    
    metadado_titulo = entry_metadado_titulo.get()
    metatado_autor = entry_metadado_autor.get()
    metatado_assunto = entry_metadado_assunto.get()
    metadado_palavraschave = entry_metadado_palavraschave.get()
    
    metadados = {
        '/Title': metadado_titulo,
        '/Author': metatado_autor,
        '/Subject': metatado_assunto,
        '/Keywords': metadado_palavraschave,
    }
    
    status_label.configure(text=f"Confirmando diretório de saída...")
    app.update()
    os.makedirs(diretorio_saida, exist_ok=True)
    imagens = []
    
    status_label.configure(text=f"Contando imagens...")
    app.update()
    nomes_arquivos = sorted(
        [f for f in os.listdir(diretorio_entrada) if f.lower().endswith(('.jpg', '.jpeg', '.png'))],
        key=extrair_numero
    )
    
    for nome_arquivo in nomes_arquivos:
        caminho = os.path.join(diretorio_entrada, nome_arquivo)
        img = Image.open(caminho).convert("RGB")
        imagens.append(img)
        
    if not imagens:
        status_label.configure(text=f"Nenhuma imagem encontrada.")
        return
    
    status_label.configure(text=f"Criando pdf temporário...")
    app.update()
    caminho_pdf_temp = os.path.join(diretorio_saida, 'temp_sem_metadados.pdf')
    imagens[0].save(
        caminho_pdf_temp,
        save_all=True,
        append_images=imagens[1:]
    )
    
    reader = PdfReader(caminho_pdf_temp)
    writer = PdfWriter()
    
    status_label.configure(text=f"Adicionando páginas...")
    app.update()
    for pagina in reader.pages:
        writer.add_page(pagina)
    
    status_label.configure(text=f"Adicionando metatados...")
    app.update()
    writer.add_metadata(metadados)
    
    caminho_pdf_final = os.path.join(diretorio_saida, nome_pdf)
    with open(caminho_pdf_final, 'wb') as f_out:
        writer.write(f_out)
        
    os.remove(caminho_pdf_temp)
    
    status_label.configure(text=f"✅ PDF criado com sucesso em: {caminho_pdf_final}")
    app.update()
    limpar_campos()
    
# Criação dos campos

# Diretório das imagens
campo_diretorio_entrada = ctk.CTkLabel(frame_compilador, text='Diretório das imagens')
campo_diretorio_entrada.pack(pady=10)

entry_entrada = ctk.CTkEntry(frame_compilador, placeholder_text='Insira o diretório...', width=250)
entry_entrada.pack()

btn_entrada = ctk.CTkButton(frame_compilador, text="Escolher Pasta", command=escolher_pasta_entrada)
btn_entrada.pack(pady=10)

# Pasta de saída
campo_diretorio_saida = ctk.CTkLabel(frame_compilador, text='Pasta de saída')
campo_diretorio_saida.pack(pady=10)

entry_saida = ctk.CTkEntry(frame_compilador, placeholder_text='Insira o diretório...', width=250)
entry_saida.pack()

btn_saida = ctk.CTkButton(frame_compilador, text="Escolher Pasta", command=escolher_pasta_saida)
btn_saida.pack(pady=10)

# Metadados
campo_metadado_titulo = ctk.CTkLabel(frame_compilador, text='Título do livro')
campo_metadado_titulo.pack(pady=10)

entry_metadado_titulo = ctk.CTkEntry(frame_compilador, placeholder_text='Insira o título para os metadados...', width=250)
entry_metadado_titulo.pack()

campo_metadado_autor = ctk.CTkLabel(frame_compilador, text='Autor do livro')
campo_metadado_autor.pack(pady=10)

entry_metadado_autor = ctk.CTkEntry(frame_compilador, placeholder_text='Insira o autor para os metadados...', width=250)
entry_metadado_autor.pack()

campo_metadado_assunto = ctk.CTkLabel(frame_compilador, text='Assunto do livro')
campo_metadado_assunto.pack(pady=10)

entry_metadado_assunto = ctk.CTkEntry(frame_compilador, placeholder_text='Insira o assunto para os metadados...', width=250)
entry_metadado_assunto.pack()

campo_metadado_palavraschave = ctk.CTkLabel(frame_compilador, text='Palavras-chave do livro')
campo_metadado_palavraschave.pack(pady=10)

entry_metadado_palavraschave = ctk.CTkEntry(frame_compilador, placeholder_text='Insira, separado por vírgulas, as palavras-chave para os metadados...', width=250)
entry_metadado_palavraschave.pack()

# Status da compilação
status_label = ctk.CTkLabel(frame_compilador, text="", wraplength=250)
status_label.pack(pady=10)

# Compilar
btn_compilar = ctk.CTkButton(frame_compilador, text="Compilar", command=compilar_imagens)
btn_compilar.pack(pady=0)

# Inicia o loop da aplicação
app.mainloop()