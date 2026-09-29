import cv2
import sys
import os
import socket
from urllib.parse import urlparse

# Termos frequentemente usados em links maliciosos e golpes de phishing
TERMOS_SUSPEITOS = [
    "verificacao", "fake", "rastreio", "seguranca", "atualizacao",
    "bloqueio", "suporte", "urgente", "recadastro", "premiacao",
    "login", "auth", "confirmar", "taxa", "correios", "encomenda"
]

def extrair_qr_code(caminho_imagem):
    """Lê a imagem e decodifica o QR Code usando OpenCV."""
    if not os.path.exists(caminho_imagem):
        return None, f"Arquivo não encontrado: {caminho_imagem}"
    
    img = cv2.imread(caminho_imagem)
    if img is None:
        return None, "Não foi possível abrir a imagem."
    
    detector = cv2.QRCodeDetector()
    dados, pontos, _ = detector.detectAndDecode(img)
    
    if not dados:
        return None, "Nenhum QR Code legível foi detectado na imagem."
    
    return dados, None

def analisar_seguranca_url(url):
    """Executa checagens heurísticas e de rede para avaliar o risco da URL."""
    relatorio = {
        "url": url,
        "pontos_alerta": [],
        "pontos_positivos": [],
        "score_risco": 0, # 0 = Seguro, 100 = Muito Perigoso
        "status": "SEGURO"
    }
    
    # 1. Checagem de formato de URL
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        relatorio["pontos_alerta"].append("O conteúdo decodificado não é uma URL web padrão.")
        relatorio["score_risco"] += 40
        relatorio["status"] = "SUSPEITO"
        return relatorio

    hostname = parsed.hostname or ""
    path = parsed.path or ""

    # 2. Protocolo (HTTPS vs HTTP)
    if parsed.scheme == "https":
        relatorio["pontos_positivos"].append("Utiliza conexão criptografada (HTTPS).")
    else:
        relatorio["pontos_alerta"].append("Não utiliza HTTPS (conexão insegura HTTP).")
        relatorio["score_risco"] += 25

    # 3. Presença de IP direto em vez de domínio
    if hostname.replace(".", "").isdigit():
        relatorio["pontos_alerta"].append("A URL usa um endereço IP direto em vez de nome de domínio.")
        relatorio["score_risco"] += 40

    # 4. Excesso de hífens no domínio (comum em domínios falsos/descartáveis)
    if hostname.count("-") >= 3:
        relatorio["pontos_alerta"].append(f"Domínio com muitos hífens ({hostname.count('-')}), comum em sites clonados.")
        relatorio["score_risco"] += 30

    # 5. Termos suspeitos / Engenharia Social
    termos_encontrados = [t for t in TERMOS_SUSPEITOS if t in hostname.lower() or t in path.lower()]
    if termos_encontrados:
        relatorio["pontos_alerta"].append(f"Contém palavras-chave típicas de phishing: {', '.join(termos_encontrados)}")
        relatorio["score_risco"] += 35

    # 6. Teste de DNS (Verifica se o domínio existe de fato)
    try:
        ip = socket.gethostbyname(hostname)
        relatorio["pontos_positivos"].append(f"Domínio registrado e ativo na internet (IP: {ip}).")
    except socket.gaierror:
        relatorio["pontos_alerta"].append("O domínio não existe ou não responde a resolução DNS (domínio falso/inválido).")
        relatorio["score_risco"] += 50

    # 7. Domínios confiáveis notórios
    dominios_confiaveis = ["google.com", "google.com.br", "gov.br", "github.com", "microsoft.com"]
    if any(hostname == d or hostname.endswith("." + d) for d in dominios_confiaveis):
        relatorio["pontos_positivos"].append("Pertence a uma organização amplamente reconhecida e verificada.")
        relatorio["score_risco"] = max(0, relatorio["score_risco"] - 50)

    # Classificação final baseada no score
    if relatorio["score_risco"] >= 50:
        relatorio["status"] = "PERIGOSO / GOLPE PROVÁVEL"
    elif relatorio["score_risco"] >= 20:
        relatorio["status"] = "SUSPEITO / ATENÇÃO"
    else:
        relatorio["status"] = "SEGURO"

    return relatorio

def imprimir_relatorio(resultado):
    print("=" * 60)
    print("             RELATÓRIO DE ANÁLISE DE QR CODE")
    print("=" * 60)
    print(f"Endereço Detectado : {resultado['url']}")
    print(f"Veredito           : {resultado['status']}")
    print(f"Nível de Risco     : {resultado['score_risco']}/100")
    print("-" * 60)
    
    if resultado["pontos_positivos"]:
        print("Indicadores Positivos:")
        for pos in resultado["pontos_positivos"]:
            print(f"  [✓] {pos}")
            
    if resultado["pontos_alerta"]:
        print("\nAlertas de Segurança:")
        for alerta in resultado["pontos_alerta"]:
            print(f"  [!] {alerta}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 analisador_qrcode.py <caminho_da_imagem>")
        sys.exit(1)
        
    arquivo = sys.argv[1]
    url_lida, erro = extrair_qr_code(arquivo)
    
    if erro:
        print(f"Erro: {erro}")
        sys.exit(1)
        
    resultado = analisar_seguranca_url(url_lida)
    imprimir_relatorio(resultado)
