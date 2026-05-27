# =====================================================================
# ARQUIVO: barra_lateral.py (PARTE 1 DE 2 - ACERTO CIRÚRGICO DE NOME)
# =====================================================================
import customtkinter as ctk
import sys
import os

class JanelaGameplayEmbutida(ctk.CTkToplevel):
    def __init__(self, app_principal, serial_dispositivo, pid_scrcpy):
        super().__init__()
        
        self.app = app_principal
        self.serial = serial_dispositivo
        self.pid_alvo = pid_scrcpy
        
        # Interface vertical fina e sem bordas (Estilo painel comercial)
        self.title("Painel Gamer Pro")
        self.geometry("60x400")
        self.overrideredirect(True) # Remove fechar, minimizar e título do Windows
        
        # Container de fundo escuro gamer
        self.fundo = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        self.fundo.pack(fill="both", expand=True)
        
        self.janela_scrcpy_hwnd = None
        
        # Constrói os botões e inicia a busca pelo visor do celular
        self.criar_botoes_painel()
        self.iniciar_rastreamento_magnetico()

    def criar_botoes_painel(self):
        """Cria os botões de atalho fixados verticalmente na barra com comandos vinculados"""
        # Botão 1: Ativar/Editar o Mapeador de Teclas
        self.btn_mapa = ctk.CTkButton(self.fundo, text="🎮", width=45, height=45, fg_color="#2b2b2b", hover_color="#3a3a3a", font=("Arial", 16))
        self.btn_mapa.pack(pady=10, padx=5)
        
        # Botão 2: Ativar Modo Teclado HID (Chama a função de reinicialização no motor ADB)
        self.btn_hid = ctk.CTkButton(
            self.fundo, 
            text="⌨️", 
            width=45, 
            height=45, 
            fg_color="#2b2b2b", 
            hover_color="#27ae60", # Muda para verde ao passar o mouse para indicar ativação
            font=("Arial", 16),
            command=lambda: self.app.motor.reiniciar_scrcpy_modo_hid(self.serial, self.pid_alvo)
        )
        self.btn_hid.pack(pady=10, padx=5)
        
        # Botão 3: Engrenagem para abrir os Ajustes do Motor
        self.btn_config = ctk.CTkButton(self.fundo, text="⚙️", width=45, height=45, fg_color="#2b2b2b", hover_color="#3a3a3a", font=("Arial", 16))
        self.btn_config.pack(pady=10, padx=5)
        
        ctk.CTkFrame(self.fundo, height=2, width=40, fg_color="gray30").pack(pady=15)
        
        # Botão 4: Apagar a tela física do celular mantendo ativa no PC
        self.btn_tela_off = ctk.CTkButton(self.fundo, text="👁️❌", width=45, height=45, fg_color="#2b2b2b", hover_color="#8e44ad", font=("Arial", 12))
        self.btn_tela_off.pack(pady=10, padx=5)

# =====================================================================
# ARQUIVO: barra_lateral.py (PARTE 2 DE 2 - CONCLUSÃO DO IMÃ ESTÁVEL)
# =====================================================================
    def iniciar_rastreamento_magnetico(self):
        """Inicia o ciclo de checagem focado exclusivamente no PID do processo do Scrcpy"""
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        
        def buscar_janela_por_pid(hwnd, lParam):
            if user32.IsWindowVisible(hwnd):
                lpdw_process_id = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(lpdw_process_id))
                
                if lpdw_process_id.value == self.pid_alvo:
                    nome_classe = ctypes.create_unicode_buffer(256)
                    user32.GetClassNameW(hwnd, nome_classe, 256)
                    
                    if nome_classe.value == "SDL_app":
                        self.janela_scrcpy_hwnd = hwnd
                        return False
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        callback_pid = WNDENUMPROC(buscar_janela_por_pid)

        def atualizar_posicao():
            if not self.janela_scrcpy_hwnd or not user32.IsWindow(self.janela_scrcpy_hwnd):
                self.janela_scrcpy_hwnd = None
                user32.EnumWindows(callback_pid, 0)
            
            if self.janela_scrcpy_hwnd and user32.IsWindow(self.janela_scrcpy_hwnd):
                if user32.IsIconic(self.janela_scrcpy_hwnd):
                    self.withdraw()
                    self.after(15, atualizar_posicao)
                    return
                
                if user32.IsWindowVisible(self.janela_scrcpy_hwnd):
                    rect = wintypes.RECT()
                    if user32.GetWindowRect(self.janela_scrcpy_hwnd, ctypes.byref(rect)):
                        if rect.left > -10000:
                            self.deiconify()
                            
                            hwnd_ativo = user32.GetForegroundWindow()
                            self.update_idletasks()
                            meu_hwnd = user32.FindWindowW(None, "Painel Gamer Pro")
                            
                            if hwnd_ativo == self.janela_scrcpy_hwnd or hwnd_ativo == meu_hwnd:
                                self.attributes("-topmost", True)
                            else:
                                self.attributes("-topmost", False)
                            
                            largura_jogo = rect.right - rect.left
                            altura_jogo = rect.bottom - rect.top
                            
                            nova_pos_x = rect.right + 1
                            nova_pos_y = rect.top + (altura_jogo // 2) - 200
                            
                            self.geometry(f"60x400+{nova_pos_x}+{nova_pos_y}")
                else:
                    self.withdraw()
            else:
                if self.janela_scrcpy_hwnd:
                    self.destroy()
                    return
            
            self.after(15, atualizar_posicao)

        atualizar_posicao()
