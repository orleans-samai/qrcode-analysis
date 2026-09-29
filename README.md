# 🛡️ QRCode Analysis & Quishing Detector

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Security: Anti-Phishing](https://img.shields.io/badge/Security-Anti--Phishing-red.svg)](#)

> Ferramenta em tempo real em Python para inspeção e análise de segurança de QR Codes via captura de tela (*Print Screen*), prevenindo ataques de **Quishing** (QR Code Phishing) antes de qualquer acesso ao link.

---

## 🎯 O Problema: Quishing

O **Quishing** (combinação de *QR Code* e *Phishing*) é um vetor de ataque cada vez mais explorado por criminosos. Ao contrário de links convencionais, o conteúdo de um QR Code é imperceptível a olho nu, levando usuários a acessar páginas falsas, formulários de clonagem de cartões ou vetores de malware em seus dispositivos.

Este projeto resolve essa vulnerabilidade ao permitir que você selecione a área de um QR Code visível na tela e receba imediatamente um diagnóstico de risco, sem abrir o navegador e sem expor seus dispositivos.

---

## ✨ Funcionalidades

- **📸 Captura Instantânea:** Integração com atalhos de seleção de tela do sistema operacional (`Print Screen` / recortar área).
- **🔍 Decodificação Local:** Processamento direto da imagem em memória através do `cv2.QRCodeDetector()` do OpenCV, sem envio de dados para servidores externos.
- **🛡️ Motor Heurístico de Avaliação de Risco (Score 0-100):**
  - **Protocolo:** Validação de criptografia de transporte (`HTTPS` vs `HTTP` inseguro).
  - **Detecção de IP Direto:** Identifica tentativas de camuflagem usando IPs numéricos em vez de nomes de domínio.
  - **Typosquatting & Domínios Clonados:** Detecção de padrões sintáticos suspeitos (excesso de hífens, subdomínios repetitivos).
  - **Engenharia Social:** Dicionário léxico contra termos típicos de phishing (*rastreio*, *segurança*, *bloqueio*, *atualização*, *correios*, etc.).
  - **Resolução Preventiva de DNS:** Checagem via `socket` para constatar se o domínio existe e possui registro ativo na internet.
  - **Allowlist Conhecida:** Redução de falso-positivo para domínios de organizações consolidadas.
- **🖥️ Feedback Imediato:** Emissão de notificações modais na área de trabalho (*Zenity*) e relatórios detalhados com cores e marcadores no terminal.
- **🔄 Modo Monitor Contínuo:** Permite analisar múltiplos QR Codes sucessivos em segundo plano.

---

## 🏗️ Fluxo de Funcionamento

```text
 [ QR Code na Tela ]
          │
          ▼  (Atalho de Print Screen / Recorte)
 [ Captura de Imagem (.png) ]
          │
          ▼
 [ OpenCV: cv2.QRCodeDetector ] ──> Extrai URL / Conteúdo
          │
          ▼
 [ Motor Heurístico de Risco ]
   ├─ Análise Léxica & Padrões (urllib)
   ├─ Checagem de DNS Ativo (socket)
   └─ Cálculo de Score (0 a 100)
          │
    ┌─────┴────────────────┐
    ▼                      ▼
[ Alerta Visual ]    [ Log no Terminal ]
(Pop-up Zenity)       (Relatório Completo)
```

---

## 📁 Estrutura do Repositório

```text
qrcode-analysis/
├── analisador_qrcode.py     # Módulo central de decodificação e análise heurística
├── capturar_e_analisar.py    # Monitor contínuo de capturas de tela e interface visual
├── gerar_exemplos.py        # Utilitário para gerar QR codes de demonstração
├── examples/                # QR Codes de exemplo para testes
│   ├── qrcode_google.png    # Exemplo classificado como Seguro
│   └── qrcode_ficticio.png  # Exemplo simulando Phishing (Perigoso)
├── requirements.txt         # Dependências do projeto
├── LICENSE                  # Licença MIT
└── README.md                # Documentação do projeto
```

---

## 🚀 Como Instalar e Usar

### 1. Pré-requisitos

* Python 3.10 ou superior
* Sistema Linux (Ubuntu, Debian, Fedora, Mint, etc.)
* Pacote `zenity` para pop-ups nativos (geralmente pré-instalado em ambientes GNOME/XFCE):
  ```bash
  sudo apt install zenity -y
  ```

### 2. Instalação

Clone o repositório e instale as dependências:

```bash
git clone https://github.com/orleans-samai/qrcode-analysis.git
cd qrcode-analysis

# (Recomendado) Crie e ative um ambiente virtual:
python3 -m venv .venv
source .venv/bin/activate

# Instale os pacotes necessários:
pip install -r requirements.txt
```

---

## 💻 Modos de Execução

### Modo 1: Monitor Contínuo de Print Screen (Recomendado)

Inicie o monitor em segundo plano:

```bash
python3 capturar_e_analisar.py
```

1. Pressione a tecla **`Print Screen`** no seu teclado.
2. Selecione apenas a área do QR Code exibido na tela (lembre-se de manter uma pequena margem branca ao redor).
3. O script detectará o novo print instantaneamente, exibindo o diagnóstico no terminal e um pop-up de alerta na sua tela!
4. Para encerrar o monitor, pressione `Ctrl + C`.

---

### Modo 2: Análise de Imagem Individual (CLI)

Você também pode passar qualquer arquivo de imagem diretamente como parâmetro:

```bash
python3 analisador_qrcode.py examples/qrcode_google.png
```

**Exemplo de Saída (URL Segura):**
```text
============================================================
             RELATÓRIO DE ANÁLISE DE QR CODE
============================================================
Endereço Detectado : https://www.google.com.br
Veredito           : SEGURO
Nível de Risco     : 0/100
------------------------------------------------------------
Indicadores Positivos:
  [✓] Utiliza conexão criptografada (HTTPS).
  [✓] Domínio registrado e ativo na internet (IP: 142.250.219.131).
  [✓] Pertence a uma organização amplamente reconhecida e verificada.
============================================================
```

**Exemplo de Saída (Tentativa de Golpe / Quishing):**
```bash
python3 analisador_qrcode.py examples/qrcode_ficticio.png
```

```text
============================================================
             RELATÓRIO DE ANÁLISE DE QR CODE
============================================================
Endereço Detectado : https://www.verificacao-fake-seguranca-alerta.com.br/rastreio
Veredito           : PERIGOSO / GOLPE PROVÁVEL
Nível de Risco     : 115/100
------------------------------------------------------------
Indicadores Positivos:
  [✓] Utiliza conexão criptografada (HTTPS).

Alertas de Segurança:
  [!] Domínio com muitos hífens (3), comum em sites clonados.
  [!] Contém palavras-chave típicas de phishing: verificacao, fake, rastreio, seguranca
  [!] O domínio não existe ou não responde a resolução DNS (domínio falso/inválido).
============================================================
```

---

### Modo 3: Gerar Novos Exemplos de Teste

Para recriar as imagens de teste da pasta `examples/`:

```bash
python3 gerar_exemplos.py
```

---

## 🔒 Boas Práticas de Segurança com QR Codes

1. **Nunca escaneie códigos sem inspecionar a URL de destino.**
2. **Desconfie de QR Codes colados sobre outros** em estabelecimentos comerciais ou contas de consumo.
3. **Evite inserir dados pessoais ou bancários** em páginas abertas diretamente por QR Codes sem validar a autenticidade do remetente.

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para obter mais informações.

---

Desenvolvido por **[Orleans Samai](https://github.com/orleans-samai)** 🚀
