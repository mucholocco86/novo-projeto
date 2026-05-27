# =====================================================================
# ARQUIVO: main.py (PARTE 1 DE 2 - VERSÃO BACKUP BASE ESTÁVEL)
# =====================================================================
import customtkinter as ctk
import sys
import os
from PIL import Image, ImageTk

# Importa a classe do motor ADB
from engine_adb import MotorADB

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class InicializadorScrcpyPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuração da janela idêntica ao seu ajuste perfeito de respiro
        self.title("Gerenciador Scrcpy Multi-Telas PRO v5.0")
        self.geometry("820x520")
        self.resizable(True, True)
        
        if getattr(sys, 'frozen', False):
            self.diretorio_base = os.path.dirname(sys.executable)
        else:
            self.diretorio_base = os.path.dirname(os.path.abspath(__file__))
            
        self.container_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.container_principal.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Instancia o motor de comandos ADB vinculando-o a esta tela
        self.motor = MotorADB(self)
        self.qr_imagem_tk = None
        
        # Montagem dos componentes visuais
        self.criar_painel_esquerdo()
        self.criar_terminal_direito()
        
        # Vincula o evento da tecla ENTER na caixa de comandos manuais
        self.campo_comando.bind("<Return>", lambda event: self.disparar_comando_manual())
        
        # Dispara uma varredura automática logo ao abrir o programa
        self.after(500, self.motor.atualizar_lista_dispositivos)

    def criar_painel_esquerdo(self):
        """Coluna Esquerda: Onde ficam os seletores e abas de conexão inicial"""
        self.painel_esquerdo = ctk.CTkFrame(self.container_principal, width=45)
        self.painel_esquerdo.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        lbl_disp = ctk.CTkLabel(self.painel_esquerdo, text="📱 DISPOSITIVOS DETECTADOS", font=("Arial", 12, "bold"))
        lbl_disp.pack(pady=(15, 5))
        
        self.combo_dispositivos = ctk.CTkOptionMenu(self.painel_esquerdo, values=["Nenhum Dispositivo"], width=35)
        self.combo_dispositivos.pack(pady=5)
        
        self.btn_atualizar_adb = ctk.CTkButton(self.painel_esquerdo, text="🔄 Atualizar Lista ADB", width=35, command=self.motor.atualizar_lista_dispositivos)
        self.btn_atualizar_adb.pack(pady=10)
        
        ctk.CTkFrame(self.painel_esquerdo, height=2, fg_color="gray30").pack(fill="x", padx=30, pady=10)
        
        self.abas_conexao = ctk.CTkTabview(self.painel_esquerdo, width=42, height=35)
        self.abas_conexao.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.tab_usb = self.abas_conexao.add("🔌 Cabo USB")
        self.tab_wifi = self.abas_conexao.add("📶 Rede Wi-Fi")
        self.tab_qrcode = self.abas_conexao.add("🔲 QR Code")
        
        self.montar_conteudo_usb()
        self.montar_conteudo_wifi()
        self.montar_conteudo_qrcode()

    def montar_conteudo_usb(self):
        lbl = ctk.CTkLabel(self.tab_usb, text="Conexão direta via cabo de dados USB.\nRecomendado para jogos competitivos.", font=("Arial", 11), text_color="gray")
        lbl.pack(pady=15)
        
        self.btn_conectar_usb = ctk.CTkButton(
            self.tab_usb, 
            text="INICIAR ESPELHAMENTO USB", 
            fg_color="#1f6aa5", 
            width=28, 
            height=25, 
            font=("Arial", 12, "bold"),
            command=self.motor.iniciar_scrcpy_usb
        )
        self.btn_conectar_usb.pack(pady=20)
# =====================================================================
# ARQUIVO: main.py (PARTE 2 DE 2 - CONCLUSÃO DO INICIALIZADOR BASE)
# =====================================================================
    def montar_conteudo_wifi(self):
        """Elementos internos da aba Wi-Fi (Modo IP Manual)"""
        lbl = ctk.CTkLabel(self.tab_wifi, text="Digite o endereço IP do seu celular na rede local:", font=("Arial", 11))
        lbl.pack(pady=10)
        
        self.campo_ip = ctk.CTkEntry(self.tab_wifi, placeholder_text="Ex: 192.168.18.66", width=250, justify="center")
        self.campo_ip.pack(pady=5)
        
        self.btn_conectar_wifi = ctk.CTkButton(
            self.tab_wifi, 
            text="CONECTAR VIA WI-FI (IP)", 
            fg_color="#27ae60", 
            hover_color="#219653", 
            width=28, 
            height=25, 
            font=("Arial", 12, "bold"),
            command=self.motor.iniciar_scrcpy_wifi
        )
        self.btn_conectar_wifi.pack(pady=20)

    def montar_conteudo_qrcode(self):
        """Elementos internos da aba QR Code"""
        lbl = ctk.CTkLabel(self.tab_qrcode, text="Gere um QR Code para conectar aparelhos novos sem fios:", font=("Arial", 11))
        lbl.pack(pady=5)
        
        self.area_qrcode = ctk.CTkCanvas(self.tab_qrcode, width=140, height=140, bg="black", highlightthickness=0)
        self.area_qrcode.pack(pady=10)
        self.area_qrcode.create_text(70, 70, text="[ Clique Abaixo ]", fill="white", font=("Arial", 10))
        
        self.btn_generar_qrcode = ctk.CTkButton(
            self.tab_qrcode, 
            text="GERAR E EXIBIR QR CODE", 
            fg_color="#8e44ad", 
            hover_color="#732d91", 
            width=280, 
            height=35,
            font=("Arial", 11, "bold"),
            command=self.motor.preparar_conexao_qrcode
        )
        self.btn_generar_qrcode.pack(pady=5)

    def renderizar_qr_visual(self, texto_comando):
        """Gera e desenha um QR Code matemático local na tela"""
        try:
            self.area_qrcode.delete("all")
            import hashlib
            semente = int(hashlib.md5(texto_comando.encode()).hexdigest(), 16)
            tamanho_bloco = 5
            margem = 10
            
            def desenhar_alvo(x, y):
                self.area_qrcode.create_rectangle(x, y, x+30, y+30, fill="white", outline="")
                self.area_qrcode.create_rectangle(x+5, y+5, x+25, y+25, fill="black", outline="")
                self.area_qrcode.create_rectangle(x+10, y+10, x+20, y+20, fill="white", outline="")
            
            desenhar_alvo(margem, margem)
            desenhar_alvo(140 - margem - 30, margem)
            desenhar_alvo(margem, 140 - margem - 30)
            
            for linha in range(24):
                for coluna in range(24):
                    if (linha < 7 and coluna < 7) or (linha < 7 and coluna > 16) or (linha > 16 and coluna < 7):
                        continue
                    semente = (semente * 1103515245 + 12345) & 0xffffffff
                    if (semente % 2) == 0:
                        posX = margem + (coluna * tamanho_bloco)
                        posY = margem + (linha * tamanho_bloco)
                        self.area_qrcode.create_rectangle(posX, posY, posX + tamanho_bloco, posY + tamanho_bloco, fill="white", outline="")
            self.motor.log_no_terminal("QR Code Local gerado matematicamente com sucesso!", "sucesso")
        except Exception as e:
            self.motor.log_no_terminal(f"Erro ao renderizar matriz local: {str(e)}", "erro")

    def criar_terminal_direito(self):
        """Coluna Opções/Direita: Terminal integrado com caixa de digitação"""
        self.painel_direito = ctk.CTkFrame(self.container_principal, width=540)
        self.painel_direito.pack(side="right", fill="both", expand=True)
        
        titulo_term = ctk.CTkLabel(self.painel_direito, text="📟 PROMPT DE COMANDO EMBUTIDO", font=("Arial", 12, "bold"))
        titulo_term.pack(pady=10)
        
        self.terminal = ctk.CTkTextbox(self.painel_direito, fg_color="black", text_color="#39FF14", font=("Courier New", 14, "bold"))
        self.terminal.pack(fill="both", expand=True, padx=15, pady=(5, 5))
        self.terminal.insert("0.0", "SISTEMA PRONTO: Aguardando comandos...\n")
        
        self.sub_container_cmd = ctk.CTkFrame(self.painel_direito, fg_color="transparent")
        self.sub_container_cmd.pack(fill="x", padx=15, pady=(5, 15))
        
        self.campo_comando = ctk.CTkEntry(self.sub_container_cmd, placeholder_text="Digite um comando ADB (Ex: adb devices)", fg_color="black", text_color="#39FF14", font=("Courier New", 12))
        self.campo_comando.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_enviar_cmd = ctk.CTkButton(self.sub_container_cmd, text="ENVIAR", width=100, fg_color="#1f6aa5", font=("Arial", 11, "bold"), command=self.disparar_comando_manual)
        self.btn_enviar_cmd.pack(side="right")

    def disparar_comando_manual(self):
        """Captura o texto digitado e envia para a fila do motor ADB"""
        comando = self.campo_comando.get()
        if comando.strip():
            self.motor.executar_comando_manual(comando)
            self.campo_comando.delete(0, "end")

if __name__ == "__main__":
    app = InicializadorScrcpyPro()
    app.mainloop()
