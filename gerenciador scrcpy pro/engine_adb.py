# =====================================================================
# ARQUIVO: engine_adb.py (PARTE 1 DE 2 - VERSÃO ESTÁVEL REVISADA)
# =====================================================================
import subprocess
import threading
import sys
import os

class MotorADB:
    def __init__(self, app_principal):
        """Vincula o motor ADB com a interface gráfica principal"""
        self.app = app_principal
        self.pasta_scrcpy = r"C:\scrcpy-win64-v4.0"
        self.adb_path = os.path.join(self.pasta_scrcpy, "adb.exe")

    def log_no_terminal(self, texto, tipo="info"):
        """Insere mensagens coloridas no terminal do main.py de forma limpa"""
        prefixo = ">>> " if tipo == "info" else "[OK] " if tipo == "sucesso" else "[ERRO] "
        mensagem_completa = f"\n{prefixo}{texto}"
        self.app.terminal.insert("end", f"{mensagem_completa}\n")
        self.app.terminal.see("end")

    def executar_comando_manual(self, comando_texto):
        """Executa comandos digitados pelo usuário sem travar a interface"""
        if not comando_texto.strip():
            return
        threading.Thread(target=self._rodar_comando_subproceso, args=(comando_texto,), daemon=True).start()

    def _rodar_comando_subproceso(self, comando_texto):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            argumentos = comando_texto.split()
            
            if argumentos and argumentos[0].lower() == "adb" and len(argumentos) > 1:
                argumentos[0] = self.adb_path

            self.log_no_terminal(f"Executando: {comando_texto}", "info")
            resultado = subprocess.run(argumentos, capture_output=True, text=True, startupinfo=startupinfo, timeout=10)
            
            if resultado.stdout:
                self.log_no_terminal(resultado.stdout.strip(), "sucesso")
            if resultado.stderr:
                self.log_no_terminal(resultado.stderr.strip(), "erro")
        except subprocess.TimeoutExpired:
            self.log_no_terminal("O comando demorou muito para responder (Timeout).", "erro")
        except Exception as e:
            self.log_no_terminal(f"Falha ao executar: {str(e)}", "erro")

    def atualizar_lista_dispositivos(self):
        """Dispara a varredura do barramento ADB em uma Thread separada"""
        threading.Thread(target=self._executar_varredura_dispositivos, daemon=True).start()

    def _executar_varredura_dispositivos(self):
        self.log_no_terminal("Escaneando barramento ADB em busca de celulares...", "info")
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            resultado = subprocess.run([self.adb_path, "devices"], capture_output=True, text=True, startupinfo=startupinfo)
            linhas = resultado.stdout.splitlines()
            lista_exibicao = []
            
            # CORREÇÃO DA SINTAXE: Agora mapeia a variável 'linhas' corretamente em português
            for linha in linhas[1:]:
                if "device" in linha and not "List" in linha:
                    partes = linha.split()
                    if partes:
                        serial_puro = partes[0]
                        try:
                            cmd_modelo = [self.adb_path, "-s", serial_puro, "shell", "getprop", "ro.product.model"]
                            res_modelo = subprocess.run(cmd_modelo, capture_output=True, text=True, startupinfo=startupinfo, timeout=2)
                            modelo = res_modelo.stdout.strip()
                            if not modelo:
                                modelo = "Dispositivo Android"
                        except Exception:
                            modelo = "Dispositivo Android"
                        
                        lista_exibicao.append(f"{serial_puro} ({modelo})")
            
            if lista_exibicao:
                self.app.combo_dispositivos.configure(values=lista_exibicao)
                self.app.combo_dispositivos.set(lista_exibicao[0])
                self.log_no_terminal(f"Sucesso! {len(lista_exibicao)} celular(es) identificado(s).", "sucesso")
            else:
                self.app.combo_dispositivos.configure(values=["Nenhum Dispositivo"])
                self.app.combo_dispositivos.set("Nenhum Dispositivo")
                self.log_no_terminal("Aviso: Nenhum dispositivo com depuração USB ativa foi detectado.", "erro")
        except Exception as e:
            self.log_no_terminal(f"Erro crítico ao escanear ADB: {str(e)}", "erro")
# =====================================================================
# ARQUIVO: engine_adb.py (PARTE 2 DE 2 - DISPARADORES E FIX DE QR CODE)
# =====================================================================
    def iniciar_scrcpy_usb(self):
        """Captura o dispositivo selecionado e inicia o Scrcpy otimizado via USB"""
        texto_selecionado = self.app.combo_dispositivos.get()
        if texto_selecionado == "Nenhum Dispositivo":
            self.log_no_terminal("Erro: Selecione um celular válido na lista antes de iniciar.", "erro")
            return
        
        serial = texto_selecionado.split()[0]
        threading.Thread(target=self._rodar_scrcpy_processo, args=(serial,), daemon=True).start()

    def _rodar_scrcpy_processo(self, serial):
        try:
            self.log_no_terminal(f"Iniciando espelhamento USB para o serial: {serial}...", "info")
            scrcpy_exe = os.path.join(self.pasta_scrcpy, "scrcpy.exe")
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            comando = [
                scrcpy_exe, 
                "-s", serial, 
                "--no-audio", 
                "--prefer-text"
            ]
            
            processo_scrcpy = subprocess.Popen(comando, startupinfo=startupinfo, cwd=self.pasta_scrcpy)
            scrcpy_pid = processo_scrcpy.pid
            
            self.log_no_terminal("Janela do Scrcpy aberta com sucesso!", "sucesso")
            self.app.after(1500, lambda: self._chamar_painel_gamer_flutuante(serial, scrcpy_pid))
        except Exception as e:
            self.log_no_terminal(f"Falha ao abrir Scrcpy: {str(e)}", "erro")

    def iniciar_scrcpy_wifi(self):
        """Captura o IP digitado, o serial selecionado e faz a ponte de conexão sem fios"""
        texto_selecionado = self.app.combo_dispositivos.get()
        ip_digitado = self.app.campo_ip.get().strip()
        
        if texto_selecionado == "Nenhum Dispositivo":
            self.log_no_terminal("Erro: Selecione um celular para abrir a porta TCPIP.", "erro")
            return
        if not ip_digitado:
            self.log_no_terminal("Erro: Digite o endereço IP do celular.", "erro")
            return
            
        serial = texto_selecionado.split()[0]
        threading.Thread(target=self._rodar_conexao_wifi, args=(serial, ip_digitado), daemon=True).start()

    def _rodar_conexao_wifi(self, serial, ip):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.log_no_terminal(f"Preparando dispositivo {serial} para modo Wi-Fi...", "info")
            
            subprocess.run([self.adb_path, "-s", serial, "tcpip", "5555"], startupinfo=startupinfo, timeout=5)
            self.log_no_terminal("Porta 5555 liberada no celular. Tentando conectar...", "sucesso")
            
            cmd_connect = [self.adb_path, "connect", f"{ip}:5555"]
            res_connect = subprocess.run(cmd_connect, capture_output=True, text=True, startupinfo=startupinfo, timeout=5)
            
            if "connected to" in res_connect.stdout.lower():
                self.log_no_terminal(f"Celular conectado via Wi-Fi no IP: {ip}!", "sucesso")
                scrcpy_exe = os.path.join(self.pasta_scrcpy, "scrcpy.exe")
                comando_scrcpy = [scrcpy_exe, "-s", f"{ip}:5555", "--no-audio", "--prefer-text"]
                
                processo_scrcpy = subprocess.Popen(comando_scrcpy, startupinfo=startupinfo, cwd=self.pasta_scrcpy)
                scrcpy_pid = processo_scrcpy.pid
                
                self.app.after(1500, lambda: self._chamar_painel_gamer_flutuante(f"{ip}:5555", scrcpy_pid))
                self.app.after(1000, self.atualizar_lista_dispositivos)
            else:
                self.log_no_terminal(f"Falha de pareamento: {res_connect.stdout.strip()}", "erro")
        except Exception as e:
            self.log_no_terminal(f"Erro ao conectar via Wi-Fi: {str(e)}", "erro")

    def extrair_ip_dispositivo(self, serial):
        """Descobre o endereço IP do celular selecionado via comandos ADB internos"""
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            cmd = [self.adb_path, "-s", serial, "shell", "ip", "route"]
            resultado = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo, timeout=3)
            
            for linha in resultado.stdout.splitlines():
                if "src" in linha and "wlan" in linha:
                    partes = linha.split()
                    idx = partes.index("src")
                    if idx + 1 < len(partes):
                        return partes[idx + 1]
        except Exception:
            return None
        return None

    def preparar_conexao_qrcode(self):
        """Dispara o processo de automação e captura de dados para o QR Code"""
        texto_selecionado = self.app.combo_dispositivos.get()
        if texto_selecionado == "Nenhum Dispositivo" or ":" in texto_selecionado:
            self.log_no_terminal("Erro: Conecte o celular via USB primeiro.", "erro")
            return
        serial = texto_selecionado.split()[0]
        threading.Thread(target=self._gerar_dados_qrcode, args=(serial,), daemon=True).start()

    def _gerar_dados_qrcode(self, serial):
        self.log_no_terminal("Identificando configurações de rede sem fio...", "info")
        ip_descoberto = self.extrair_ip_dispositivo(serial)
        if not ip_descoberto:
            self.log_no_terminal("Aviso: IP não encontrado na rede local. Usando IP alternativo.", "info")
            ip_descoberto = "192.168.18.100"
            
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run([self.adb_path, "-s", serial, "tcpip", "5555"], startupinfo=startupinfo, timeout=5)
            
            self.log_no_terminal(f"IP para pareamento: {ip_descoberto}. Gerando matriz...", "sucesso")
            string_conexao = f"adb connect {ip_descoberto}:5555"
            self.app.renderizar_qr_visual(string_conexao)
        except Exception as e:
            self.log_no_terminal(f"Erro ao processar QR Code: {str(e)}", "erro")

    def reiniciar_scrcpy_modo_hid(self, serial, pid_atual):
        """Desliga o teclado virtual do celular e passa o controle total para o PC sem fechar a tela"""
        try:
            self.log_no_terminal("Injetando diretrizes de Teclado Físico no Android...", "info")
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            # Comando 1: Ordena ao sistema do Android para ocultar o teclado virtual na tela ao usar o PC
            cmd_ocultar_teclado = [self.adb_path, "-s", serial, "shell", "settings", "put", "secure", "show_ime_with_hard_keyboard", "0"]
            subprocess.run(cmd_ocultar_teclado, startupinfo=startupinfo, capture_output=True)
            
            # Comando 2: Força o Android a priorizar a codificação de texto pura vinda do computador
            cmd_prioridade = [self.adb_path, "-s", serial, "shell", "settings", "put", "secure", "default_input_method", "com.android.inputmethod.latin/.LatinIME"]
            subprocess.run(cmd_prioridade, startupinfo=startupinfo, capture_output=True)
            
            self.log_no_terminal("Modo Digitação Otimizada ativado via Injeção ADB Direta!", "sucesso")
            
        except Exception as e:
            self.log_no_terminal(f"Falha ao injetar parâmetros de teclado: {str(e)}", "erro")

    def _chamar_painel_gamer_flutuante(self, serial, pid):
        """Instancia la barra lateral magnética asociada al proceso activo"""
        try:
            from barra_lateral import JanelaGameplayEmbutida
            self.barra_gamer = JanelaGameplayEmbutida(self.app, serial, pid)
            self.log_no_terminal("Barra de ferramentas gamer vinculada ao processo do jogo!", "sucesso")
        except Exception as e:
            self.log_no_terminal(f"Erro ao ancorar barra de ferramentas: {str(e)}", "erro")
