import os
import sys
import re
import subprocess
import threading
import customtkinter as ctk

# Configurações visuais (Estilo escuro e moderno)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# PORTABILIDADE PURA E ORIGINAL RESTAURADA:
if getattr(sys, 'frozen', False):
    PASTA_ATUAL = os.path.dirname(os.path.realpath(sys.executable))
else:
    PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))

CAMINHO_ADB = os.path.join(PASTA_ATUAL, "adb.exe")
CAMINHO_SCRCPY = os.path.join(PASTA_ATUAL, "scrcpy.exe")

class GerenciadorMultiJanelas(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gerenciador scrcpy Multi-Telas + Console Pro")
        self.geometry("900x520")  # Espaço confortável para os controles e o terminal grande
        self.resizable(False, False)

        self.mapeamento_dispositivos = {}

        # ------------------ PAINEL ESQUERDO (Controles do Celular) ------------------
        self.frame_esquerdo = ctk.CTkFrame(self, width=380, fg_color="transparent")
        self.frame_esquerdo.pack(side="left", fill="both", expand=True, padx=20, pady=15)

        self.titulo = ctk.CTkLabel(self.frame_esquerdo, text="Selecione o celular:", font=("Arial", 16, "bold"))
        self.titulo.pack(pady=15)

        self.lista_dispositivos = ctk.CTkOptionMenu(self.frame_esquerdo, values=["Buscando aparelhos..."], width=300)
        self.lista_dispositivos.pack(pady=5)

        self.btn_atualizar = ctk.CTkButton(self.frame_esquerdo, text="🔄 Atualizar Lista", font=("Arial", 12, "bold"), command=self.buscar_dispositivos, width=300)
        self.btn_atualizar.pack(pady=10)

        # MODO DE CONEXÃO (USB OU WI-FI)
        self.frame_modo = ctk.CTkFrame(self.frame_esquerdo, fg_color="transparent")
        self.frame_modo.pack(pady=5)
        
        self.var_modo = ctk.StringVar(value="usb")
        
        self.radio_usb = ctk.CTkRadioButton(self.frame_modo, text="Cabo USB", font=("Arial", 12, "bold"), variable=self.var_modo, value="usb")
        self.radio_usb.pack(side="left", padx=15)
        
        self.radio_wifi = ctk.CTkRadioButton(self.frame_modo, text="Rede Wi-Fi", font=("Arial", 12, "bold"), variable=self.var_modo, value="wifi")
        self.radio_wifi.pack(side="left", padx=15)

        # DESEMPENHO DO VÍDEO
        self.lbl_perf = ctk.CTkLabel(self.frame_esquerdo, text="Qualidade do Vídeo (Performance para Jogos):", font=("Arial", 12, "bold"), text_color="#3b8ed0")
        self.lbl_perf.pack(pady=(10, 5))

        self.frame_perf = ctk.CTkFrame(self.frame_esquerdo, fg_color="transparent")
        self.frame_perf.pack(pady=5)

        self.var_perf = ctk.StringVar(value="media")

        self.radio_baixa = ctk.CTkRadioButton(self.frame_perf, text="Baixa (FPS)", font=("Arial", 12, "bold"), variable=self.var_perf, value="baixa")
        self.radio_baixa.pack(side="left", padx=10)

        self.radio_media = ctk.CTkRadioButton(self.frame_perf, text="Média (Equilíbrio)", font=("Arial", 12, "bold"), variable=self.var_perf, value="media")
        self.radio_media.pack(side="left", padx=10)

        self.radio_alta = ctk.CTkRadioButton(self.frame_perf, text="Alta (Visual)", font=("Arial", 12, "bold"), variable=self.var_perf, value="alta")
        self.radio_alta.pack(side="left", padx=10)

        # SEÇÃO: SOM
        self.frame_opcoes_extras = ctk.CTkFrame(self.frame_esquerdo, fg_color="transparent")
        self.frame_opcoes_extras.pack(pady=10)

        self.var_audio = ctk.BooleanVar(value=False)
        self.chk_audio = ctk.CTkCheckBox(self.frame_opcoes_extras, text="🔊 Ativar som", font=("Arial", 14, "bold"), variable=self.var_audio)
        self.chk_audio.pack(side="left", padx=10)

        # Botão Principal de Abertura
        self.btn_abrir = ctk.CTkButton(
            self.frame_esquerdo, 
            text="📺 Abrir Celular", 
            font=("Arial", 14, "bold"), 
            command=self.abrir_janela_celular, 
            fg_color="green", 
            hover_color="darkgreen", 
            width=300,
            height=40
        )
        self.btn_abrir.pack(pady=15)

        self.status = ctk.CTkLabel(self.frame_esquerdo, text="Status: Pronto", font=("Arial", 11, "italic"), wraplength=350)
        self.status.pack(side="bottom", pady=10)
        # ------------------ PAINEL DIREITO (Prompt de Comando Embutido) ------------------
        self.frame_direito = ctk.CTkFrame(self, width=480, fg_color="#121212", corner_radius=10)
        self.frame_direito.pack(side="right", fill="both", expand=True, padx=20, pady=15)

        self.titulo_console = ctk.CTkLabel(self.frame_direito, text="💻 Prompt de Comando Embutido (Digite help para ajuda)", font=("Arial", 13, "bold"), text_color="#3b8ed0")
        self.titulo_console.pack(pady=10)

        # Caixa de exibição do Terminal (Apenas leitura)
        self.txt_console = ctk.CTkTextbox(self.frame_direito, width=440, height=300, font=("Consolas", 14, "bold"), fg_color="#000000")
        self.txt_console.pack(padx=15, pady=5)
        
        self.txt_console.tag_config("sucesso", foreground="#39ff14")  
        self.txt_console.tag_config("erro", foreground="#ff3333")     
        self.txt_console.tag_config("info", foreground="#ffffff")     
        
        self.txt_console.insert("end", "--- Terminal Portatil Iniciado ---\nDigite help ou ajuda para ver os comandos de emergencia!\n\n", "sucesso")
        self.txt_console.configure(state="disabled")

        # Campo para digitar os comandos
        self.frame_input_cmd = ctk.CTkFrame(self.frame_direito, fg_color="transparent")
        self.frame_input_cmd.pack(fill="x", padx=15, pady=10)

        self.entry_comando = ctk.CTkEntry(self.frame_input_cmd, placeholder_text="Digite o comando aqui...", font=("Consolas", 13, "bold"), width=320)
        self.entry_comando.pack(side="left", padx=(0, 10), fill="x", expand=True)
        self.entry_comando.bind("<Return>", lambda event: self.executar_comando_prompt())

        self.btn_enviar_cmd = ctk.CTkButton(self.frame_input_cmd, text="Enviar", font=("Arial", 12, "bold"), width=80, command=self.executar_comando_prompt)
        self.btn_enviar_cmd.pack(side="right")

        self.buscar_dispositivos()

    def buscar_dispositivos(self):
        try:
            info_inicializacao = subprocess.STARTUPINFO()
            info_inicializacao.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info_inicializacao.wShowWindow = subprocess.SW_HIDE

            resultado = subprocess.run(
                [CAMINHO_ADB, "devices"], 
                capture_output=True, 
                text=True, 
                startupinfo=info_inicializacao,
                creationflags=subprocess.CREATE_NO_WINDOW,
                check=True
            )
            linhas = resultado.stdout.strip().split("\n")
            self.mapeamento_dispositivos.clear()
            opcoes = []
            
            for linha in linhas[1:]:
                if "device" in linha:
                    partes = linha.split("\t")
                    if partes:
                        serial = partes[0].strip()
                        
                        cmd_mod = [CAMINHO_ADB, "-s", serial, "shell", "getprop", "ro.product.model"]
                        res_mod = subprocess.run(
                            cmd_mod, 
                            capture_output=True, 
                            text=True, 
                            timeout=2,
                            startupinfo=info_inicializacao,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        modelo = res_mod.stdout.strip().replace(" ", "_") or "Android"
                        
                        exibicao = f"{modelo} : {serial}"
                        self.mapeamento_dispositivos[exibicao] = serial
                        opcoes.append(exibicao)

            if opcoes:
                self.lista_dispositivos.configure(values=opcoes)
                self.lista_dispositivos.set(opcoes[0])
                self.status.configure(text=f"Status: {len(opcoes)} aparelho(s) encontrado(s).")
            else:
                self.lista_dispositivos.configure(values=["Nenhum dispositivo encontrado"])
                self.lista_dispositivos.set("Nenhum dispositivo encontrado")
                self.status.configure(text="Status: Conecte os celulares via USB.")
        except Exception as e:
            self.status.configure(text=f"Erro: {str(e)}")

    def obter_ip_celular(self, serial):
        try:
            info_inicializacao = subprocess.STARTUPINFO()
            info_inicializacao.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info_inicializacao.wShowWindow = subprocess.SW_HIDE

            cmd_ip = [CAMINHO_ADB, "-s", serial, "shell", "ip", "route"]
            res_ip = subprocess.run(cmd_ip, capture_output=True, text=True, timeout=2, startupinfo=info_inicializacao, creationflags=subprocess.CREATE_NO_WINDOW)
            ips = re.findall(r'src\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', res_ip.stdout)
            for ip in ips:
                if ip.startswith("192.168.") or ip.startswith("10."):
                    return ip
            
            cmd_addr = [CAMINHO_ADB, "-s", serial, "shell", "ip", "addr", "show"]
            res_addr = subprocess.run(cmd_addr, capture_output=True, text=True, timeout=2, startupinfo=info_inicializacao, creationflags=subprocess.CREATE_NO_WINDOW)
            ips_addr = re.findall(r'inet\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', res_addr.stdout)
            for ip in ips_addr:
                if ip != "127.0.0.1" and (ip.startswith("192.168.") or ip.startswith("10.")):
                    return ip
            return None
        except Exception:
            return None
    def abrir_janela_celular(self):
        selecionado = self.lista_dispositivos.get()
        if "Nenhum" in selecionado or "Buscando" in selecionado:
            self.status.configure(text="Aviso: Selecione um aparelho válido!")
            return

        serial = self.mapeamento_dispositivos[selecionado]
        nome_exibicao = selecionado.split(' : ')
        modo = self.var_modo.get()
        performance = self.var_perf.get()
        transmitir_audio = self.var_audio.get()

        parametros_scrcpy = []

        # Desempenho do vídeo baseado na sua escolha
        if performance == "baixa":
            parametros_scrcpy.extend(["-m", "800", "-b", "2M", "--video-codec=h264", "--max-fps", "30"])
        elif performance == "media":
            parametros_scrcpy.extend(["-m", "1024", "-b", "4M", "--video-codec=h264", "--max-fps", "60"])
        elif performance == "alta":
            pass

        # Controle independente do som
        if not transmitir_audio:
            parametros_scrcpy.append("--no-audio")

        info_inicializacao = subprocess.STARTUPINFO()
        info_inicializacao.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info_inicializacao.wShowWindow = subprocess.SW_HIDE

        if modo == "usb":
            self.status.configure(text=f"Abrindo {nome_exibicao} via Cabo USB...")
            comando_final = [CAMINHO_SCRCPY, "-s", serial] + parametros_scrcpy
            subprocess.Popen(comando_final, startupinfo=info_inicializacao, creationflags=subprocess.CREATE_NO_WINDOW)
        
        elif modo == "wifi":
            self.status.configure(text="Buscando IP do celular... Aguarde.")
            self.update()
            ip_celular = self.obter_ip_celular(serial)
            
            if not ip_celular:
                self.status.configure(text="Erro: Não foi possível obter o IP automaticamente.")
                return
                
            self.status.configure(text=f"IP Identificado: {ip_celular}. Ativando porta sem fio...")
            self.update()
            
            subprocess.run([CAMINHO_ADB, "-s", serial, "tcpip", "5555"], startupinfo=info_inicializacao, creationflags=subprocess.CREATE_NO_WINDOW)
            ip_completo = f"{ip_celular}:5555"
            subprocess.run([CAMINHO_ADB, "connect", ip_completo], startupinfo=info_inicializacao, creationflags=subprocess.CREATE_NO_WINDOW)
            
            self.status.configure(text=f"Abrindo {nome_exibicao} via Wi-Fi ({ip_celular})...")
            comando_final = [CAMINHO_SCRCPY, "-s", ip_completo, "--window-title", f"{nome_exibicao} (Sem Fio)"] + parametros_scrcpy
            subprocess.Popen(comando_final, startupinfo=info_inicializacao, creationflags=subprocess.CREATE_NO_WINDOW)

    def executar_comando_prompt(self):
        comando_cru = self.entry_comando.get().strip()
        if not comando_cru:
            return

        self.entry_comando.delete(0, "end")
        threading.Thread(target=self._thread_processar_comando, args=(comando_cru,), daemon=True).start()

    def _thread_processar_comando(self, comando_cru):
        # MENU DE AJUDA EXPANDIDO COM A DICA DO IP (Seu novo recurso)
        if comando_cru.lower() in ["help", "ajuda"]:
            texto_ajuda = (
                "\n=== MENU DE AJUDA DOS COMANDOS ===\n"
                "1. adb devices\n"
                "   -> Lista e acorda os celulares conectados.\n\n"
                "2. adb shell ip route\n"
                "   -> Descobre o IP do celular para o Wi-Fi (olhar src)\n\n"
                "3. adb tcpip 5555\n"
                "   -> Ativa a antena de rede do celular via cabo.\n\n"
                "4. adb connect IP_DO_CELULAR:5555\n"
                "   -> Forca a conexao Wi-Fi (Ex: adb connect 192.168.18.66:5555)\n"
                "==================================\n"
            )
            self._escrever_no_console(texto_ajuda, "sucesso")
            return

        partes = comando_cru.split(" ")
        gatilho = partes[0].lower()

        if gatilho == "adb":
            partes[0] = CAMINHO_ADB
            usando_sistema = False
        elif gatilho == "scrcpy":
            partes[0] = CAMINHO_SCRCPY
            usando_sistema = False
        else:
            usando_sistema = True

        self._escrever_no_console(f"> {comando_cru}\n", "info")

        try:
            info_inicializacao = subprocess.STARTUPINFO()
            info_inicializacao.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info_inicializacao.wShowWindow = subprocess.SW_HIDE

            resposta = subprocess.run(
                comando_cru if usando_sistema else partes,
                capture_output=True,
                text=True,
                shell=usando_sistema,
                startupinfo=info_inicializacao,
                creationflags=subprocess.CREATE_NO_WINDOW,
                cwd=PASTA_ATUAL,
                timeout=5
            )
            
            if resposta.returncode == 0:
                if resposta.stdout:
                    if "error" in resposta.stdout.lower() or "failed" in resposta.stdout.lower():
                        self._escrever_no_console(resposta.stdout, "erro")
                    else:
                        self._escrever_no_console(resposta.stdout, "sucesso")
                if resposta.stderr:
                    if "error" in resposta.stderr.lower():
                        self._escrever_no_console(resposta.stderr, "erro")
                    else:
                        self._escrever_no_console(resposta.stderr, "sucesso")
            else:
                saida_erro = resposta.stderr if resposta.stderr else resposta.stdout
                if not saida_erro:
                    saida_erro = f"Comando invalido ou falha na execucao (Codigo: {resposta.returncode})\n"
                self._escrever_no_console(saida_erro, "erro")
                
        except subprocess.TimeoutExpired:
            self._escrever_no_console("Erro: O comando demorou para responder (Timeout).\n", "erro")
        except Exception as e:
            self._escrever_no_console(f"Falha critica ao executar: {str(e)}\n", "erro")
        
        self._escrever_no_console("\n", "info")

    def _escrever_no_console(self, texto, tipo_tag):
        self.txt_console.configure(state="normal")
        self.txt_console.insert("end", texto, tipo_tag)
        self.txt_console.see("end")
        self.txt_console.configure(state="disabled")

if __name__ == "__main__":
    app = GerenciadorMultiJanelas()
    app.mainloop()
