import os, sys
import customtkinter as ctk
from modulos import compilador, redimensionador, renomeador

# Configuração da aparência
ctk.set_appearance_mode('dark')

# Criação da janela principal
app = ctk.CTk()

# Colocar altura e largura, e fazer com que a janela abra centralizada
largura_janela = 600
altura_janela = 500
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
pos_x = int((screen_width - largura_janela) / 2)
pos_y = int((screen_height - altura_janela) / 2)

app.title("Compilador de livros")
app.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

# Código seguro para o ícone, arrumando o diretório, e evitando que o programa pare se não encontrá-lo
try:
    icon_path = os.path.join(getattr(sys, '_MEIPASS', '.'), "assets/icon.ico")
    if os.path.exists(icon_path):
        app.iconbitmap(icon_path)
except:
    pass

# Criar área das abas
tabview = ctk.CTkTabview(app, width=580, height=480)
tabview.pack(padx=10, pady=10, fill="both", expand=True)

# Criar abas, usando o arquivo de cada programinha
compilador.criar_aba(tabview)
redimensionador.criar_aba(tabview)
renomeador.criar_aba(tabview)

# Inicia o loop da aplicação
app.mainloop()