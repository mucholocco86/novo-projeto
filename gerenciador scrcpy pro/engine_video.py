# =====================================================================
# ARQUIVO: engine_video.py (PARTE 1 DE 1 - DICIONÁRIOS DE CODEC)
# =====================================================================
class ControladorVideo:
    def __init__(self):
        """Gerencia os perfis de qualidade de transmissão do Scrcpy"""
        
        # Mapeamento de resoluções comerciais idênticas ao WASD+
        self.perfis_resolucao = {
            "Auto (Nativo)": "",
            "1920x1080": "1920",
            "1280x720": "1280",
            "1024x576": "1024",
            "800x450": "800",
            "640x360 (Modo FPS)": "640"
        }
        
        # Mapeamento de Bitrates para controle de delay de rede
        self.perfis_bitrate = {
            "1 Mbps (Mínimo Delay)": "1m",
            "2 Mbps": "2m",
            "4 Mbps": "4m",
            "8 Mbps (Padrão Equilíbrio)": "8m",
            "16 Mbps": "16m",
            "32 Mbps (Ultra Qualidade)": "32m"
        }
        
        # Limites de quadros por segundo para placas de vídeo fracas ou fortes
        self.perfis_fps = {
            "30 FPS (Econômico)": "30",
            "60 FPS (Fluidez Gamer)": "60",
            "90 FPS (Alta Taxa)": "90",
            "128 FPS (Máximo Motorola)": "128"
        }

    def extrair_argumentos_video(self, res_nome, bit_nome, fps_nome):
        """Converte as seleções textuais da interface em flags reais para o Scrcpy"""
        argumentos = []
        
        # Captura o tamanho máximo se não for automático
        max_size = self.perfis_resolucao.get(res_nome, "")
        if max_size:
            argumentos.extend(["--max-size", max_size])
            
        # Captura a taxa de bits
        bitrate = self.perfis_bitrate.get(bit_nome, "8m")
        argumentos.extend(["--video-bit-rate", bitrate])
        
        # Captura o limite de quadros
        fps = self.perfis_fps.get(fps_nome, "60")
        argumentos.extend(["--max-fps", fps])
        
        return argumentos
