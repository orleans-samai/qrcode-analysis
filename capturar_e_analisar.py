#!/usr/bin/env python3
import os
import sys
import time
import glob
import subprocess
from urllib.parse import urlparse
import cv2

# Importa as funções do analisador
from analisador_qrcode import extrair_qr_code, analisar_seguranca_url, imprimir_relatorio

PASTAS_PRINTS = [
    os.path.expanduser("~/Imagens/Capturas de tela"),
    os.path.expanduser("~/Pictures/Screenshots"),
    os.path.expanduser("~/Imagens"),
    os.path.expanduser("~/Pictures")
]

def obter_pasta_prints():
    """Identifica a pasta de capturas de tela do sistema."""
    for pasta in PASTAS_PRINTS:
        if os.path.exists(pasta):
            return pasta
    padrao = os.path.expanduser("~/Imagens/Capturas de tela")
    os.makedirs(padrao, exist_ok=True)
    return padrao

def exibir_popup_zenity(resultado):
    """Exibe um pop-up visual na tela do usuário usando Zenity."""
    titulo = f"Análise de QR Code: {resultado['status']}"
    
    detalhes = f"Endereço: {resultado['url']}\nRisco: {resultado['score_risco']}/100\n\n"
    
    if resultado["pontos_positivos"]:
        detalhes += "Positivo:\n" + "\n".join(f"  • {p}" for p in resultado["pontos_positivos"]) + "\n\n"
        
    if resultado["pontos_alerta"]:
        detalhes += "Alertas:\n" + "\n".join(f"  • {a}" for a in resultado["pontos_alerta"])
        
    tipo_dialogo = "--info"
    if "PERIGOSO" in resultado["status"] or "SUSPEITO" in resultado["status"]:
        tipo_dialogo = "--warning"
        
    try:
        subprocess.Popen([
            "zenity", tipo_dialogo,
            f"--title={titulo}",
            f"--text={detalhes}",
            "--width=480"
        ])
    except Exception:
        pass

def notificar_erro(mensagem):
    """Notifica o usuário caso o QR Code não tenha sido identificado."""
    try:
        subprocess.Popen([
            "zenity", "--info",
            "--title=Aviso: QR Code",
            f"--text={mensagem}",
            "--width=400"
        ])
    except Exception:
        pass

def processar_imagem(caminho_imagem):
    """Processa o arquivo de print screen capturado."""
    print(f"\n[+] Novo print detectado: {os.path.basename(caminho_imagem)}")
    url, erro = extrair_qr_code(caminho_imagem)
    
    if erro:
        msg = f"{erro}\nDica: selecione o QR Code com uma margem branca ao redor."
        print(f"[-] {msg}")
        notificar_erro(msg)
        return
        
    resultado = analisar_seguranca_url(url)
    imprimir_relatorio(resultado)
    exibir_popup_zenity(resultado)

def iniciar_monitor_continuo(pasta_prints):
    """Monitora continuamente para que o usuário possa tirar quantos prints quiser."""
    arquivos_vistos = set(glob.glob(os.path.join(pasta_prints, "*.png")))
    
    print("=" * 60)
    print("      ANALISADOR DE QR CODE EM TEMPO REAL ATIVO")
    print("=" * 60)
    print(f"Pasta monitorada : {pasta_prints}")
    print("Instruções       : Pressione a tecla 'Print Screen',")
    print("                   selecione a área do QR Code e confirme.")
    print("Status           : Monitorando continuamente (quantos prints quiser).")
    print("                   Pressione Ctrl+C para encerrar.")
    print("=" * 60 + "\n")
    print("[*] Aguardando print screen...")

    try:
        while True:
            time.sleep(0.5)
            arquivos_atuais = set(glob.glob(os.path.join(pasta_prints, "*.png")))
            novos = arquivos_atuais - arquivos_vistos
            
            if novos:
                # Ordena os novos arquivos por data de modificação
                for novo_arquivo in sorted(novos, key=os.path.getmtime):
                    # Pequena pausa para garantir que o GNOME terminou de gravar a imagem no disco
                    time.sleep(0.3)
                    processar_imagem(novo_arquivo)
                
                arquivos_vistos = arquivos_atuais
                print("\n[*] Pronto! Aguardando o próximo print screen (ou Ctrl+C para sair)...")
                
    except KeyboardInterrupt:
        print("\n\n[*] Analisador encerrado com sucesso.")

if __name__ == "__main__":
    pasta = obter_pasta_prints()
    
    # Se o usuário passou um arquivo específico como parâmetro direto
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        processar_imagem(sys.argv[1])
    else:
        # Por padrão agora, entra em modo contínuo direto!
        iniciar_monitor_continuo(pasta)
