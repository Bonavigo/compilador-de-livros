import customtkinter as ctk
from tkinter import filedialog

# Configuração da aparência
ctk.set_appearance_mode('dark')

# Criação da janela principal
app = ctk.CTk()
app.title("Compilador de livros")
app.geometry('350x500')

# Criação das funcionalidades
# Escolher pasta de entrada
def escolher_pasta():
    pasta = filedialog.askdirectory()
    if pasta:
        entry_entrada.delete(0, "end")
        entry_entrada.insert(0, pasta)
        
# Escolher pasta de saída
def escolher_pasta():
    pasta = filedialog.askdirectory()
    if pasta:
        entry_saida.delete(0, "end")
        entry_saida.insert(0, pasta)
        
# Compilar imagens
def compilar_imagens():
    diretorio_entrada = campo_diretorio_entrada.get()
    diretorio_saida = campo_diretorio_saida.get()
    
    nome_pdf = 'livro_final.pdf'

# Criação dos campos

# Para escolher a pasta em que os arquivos de imagem vão ser pegos
# Label
campo_diretorio_entrada = ctk.CTkLabel(app, text='Diretório das imagens')
campo_diretorio_entrada.pack(pady=10)

# Texto com o diretório
entry_entrada = ctk.CTkEntry(app, placeholder_text='Insira o diretório...', width=250)
entry_entrada.pack()

# Button
btn_entrada = ctk.CTkButton(app, text="Escolher Pasta", command=escolher_pasta)
btn_entrada.pack(pady=10)

# Para escolher a pasta em que o arquivo .pdf sairá
# Label
campo_diretorio_saida = ctk.CTkLabel(app, text='Pasta de saída')
campo_diretorio_saida.pack(pady=10)

# Texto com o diretório
entry_saida = ctk.CTkEntry(app, placeholder_text='Insira o diretório...', width=250)
entry_saida.pack()

# Button
btn_saida = ctk.CTkButton(app, text="Escolher Pasta", command=escolher_pasta)
btn_saida.pack(pady=10)

# Metadados
# Título
# Label
campo_metadado_titulo = ctk.CTkLabel(app, text='Título do livro')
campo_metadado_titulo.pack(pady=10)

# Texto com o diretório
entry_metadado_titulo = ctk.CTkEntry(app, placeholder_text='Insira o título para os metatados...', width=250)
entry_metadado_titulo.pack()

# Autor
# Label
campo_metadado_livro = ctk.CTkLabel(app, text='Autor do livro')
campo_metadado_livro.pack(pady=10)

# Texto com o diretório
entry_metadado_livro = ctk.CTkEntry(app, placeholder_text='Insira o autor para os metatados...', width=250)
entry_metadado_livro.pack()

# Compilar
# Button
btn_compilar = ctk.CTkButton(app, text="Compilar", command=compilar_imagens)
btn_compilar.pack(pady=30)

# Inicia o loop da aplicação
app.mainloop()