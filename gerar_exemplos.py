#!/usr/bin/env python3
"""
Script utilitário para gerar imagens de teste de QR Code:
1. Um QR Code apontando para o site oficial do Google (Seguro).
2. Um QR Code apontando para uma URL simulando tentativa de Quishing/Golpe (Suspeito/Perigoso).
"""

import os
import qrcode
from PIL import Image, ImageDraw

def gerar_qr_rotulado(url, rotulo, caminho_saida):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
    # Adiciona espaço inferior para o rótulo descritivo
    largura, altura = img_qr.size
    altura_total = altura + 50
    nova_imagem = Image.new("RGB", (largura, altura_total), "white")
    nova_imagem.paste(img_qr, (0, 0))
    
    draw = ImageDraw.Draw(nova_imagem)
    bbox = draw.textbbox((0, 0), rotulo)
    largura_texto = bbox[2] - bbox[0]
    draw.text(((largura - largura_texto) // 2, altura + 15), rotulo, fill="black")
    
    nova_imagem.save(caminho_saida)
    print(f"[✓] Gerado: {caminho_saida} -> {url}")

def main():
    diretorio_exemplos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")
    os.makedirs(diretorio_exemplos, exist_ok=True)
    
    print("Gerando QR Codes de demonstração...")
    gerar_qr_rotulado(
        url="https://www.google.com.br",
        rotulo="www.google.com.br (Oficial)",
        caminho_saida=os.path.join(diretorio_exemplos, "qrcode_google.png")
    )
    
    gerar_qr_rotulado(
        url="https://www.verificacao-fake-seguranca-alerta.com.br/rastreio",
        rotulo="exemplo-fake-alerta.com.br (Ficticio)",
        caminho_saida=os.path.join(diretorio_exemplos, "qrcode_ficticio.png")
    )
    print("\nConcluído com sucesso!")

if __name__ == "__main__":
    main()
