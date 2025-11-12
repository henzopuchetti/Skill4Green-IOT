# 🌱 Skill4Green — Módulo de IA & IoT (Global Soluction)

**Repositório:** [github.com/henzopuchetti/Skill4Green-IOT.git](https://github.com/henzopuchetti/Skill4Green-IOT.git)

---

## 💡 Visão Geral

O **Skill4Green** é um projeto que une **Inteligência Artificial**, **IoT** e **Sustentabilidade Corporativa**.  
Ele analisa, recomenda e valida ações sustentáveis realizadas por colaboradores, transformando economia de energia em aprendizado e engajamento.

Este módulo em **Python (FastAPI)** integra:
- 🌍 **IA Generativa (Gemini Flash)** para gerar recomendações e mensagens motivacionais personalizadas;  
- 🧠 **Visão Computacional (YOLO + SSIM)** para verificar automaticamente se uma tarefa física foi realmente executada (ex.: troca de lâmpadas fluorescentes por LED);  
- 🔌 **Integração com API Java** (via HTTP), permitindo que o backend principal consuma as respostas e métricas em tempo real.

---

## ⚙️ Tecnologias Utilizadas

| Tecnologia | Função |
|-------------|--------|
| **FastAPI** | Framework web para construção da API. |
| **Uvicorn** | Servidor ASGI para rodar a aplicação FastAPI. |
| **Google Gemini Flash** | Modelo de IA Generativa usado para gerar recomendações e mensagens. |
| **OpenCV + scikit-image (SSIM)** | Análise estrutural de imagens “antes e depois”. |
| **Ultralytics YOLO** | Modelo de visão computacional para detectar mudanças reais em objetos. |
| **httpx** | Cliente HTTP assíncrono para comunicação com a API do Gemini. |
| **python-dotenv** | Gerencia variáveis sensíveis (como a chave da API) em um arquivo `.env`. |
| **python-multipart** | Necessário para upload de imagens. |
| **torch / torchvision** | Suporte à inferência do YOLO em CPU. |

---

## 🧾 Estrutura do Projeto

```
Skill4Green-IOT/
│
├── app/
│   ├── main.py                # Ponto principal da API (rotas FastAPI)
│   ├── gemini_client.py       # Integração com API Gemini Flash
│   ├── cv.py                  # Comparação de imagens (SSIM)
│   ├── cv_yolo.py             # Análise de imagens com YOLO
│   ├── prompts.py             # Templates de prompts da IA
│   ├── config.py              # Configurações globais e variáveis de ambiente
│   └── __init__.py
│
├── requirements.txt           # Dependências da aplicação
├── .gitignore                 # Ignora arquivos locais e sensíveis
├── .env.sample                # Exemplo de arquivo .env (sem a sua chave real)
├── index.html                 # Interface simples para testes
└── README.md                  # Documentação do projeto
```

---

## 🔐 Sobre o arquivo `.env`

O `.env` **não é versionado** (está no `.gitignore`), o que significa que **ninguém verá a sua chave de API**.  
No repositório, você deixará apenas o modelo `.env.sample`, por exemplo:

```bash
# .env.sample (arquivo exemplo)
GEMINI_API_KEY=COLOQUE_SUA_CHAVE_AQUI
GEMINI_MODEL=gemini-1.5-flash
GEMINI_BASE=https://generativelanguage.googleapis.com
EMISSION_FACTOR=0.084
TARIFF_KWH=0.95
YOLO_MODEL_PATH=yolo11n.pt
SSIM_THRESHOLD=0.75
YOLO_DELTA_MIN=1
```

---

## 💻 Instalação e Execução Local

### 1️⃣ Clonar o repositório
```bash
git clone https://github.com/henzopuchetti/Skill4Green-IOT.git
cd Skill4Green-IOT
```

### 2️⃣ Criar e ativar o ambiente virtual
```bash
python -m venv .venv
.\.venv\Scripts\activate   # Windows
# ou
source .venv/bin/activate    # Linux/Mac
```

### 3️⃣ Atualizar o pip e instalar dependências
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Criar o arquivo `.env`
Copie o exemplo:
```bash
cp .env.sample .env
```
Abra o `.env` e adicione **sua chave da API do Gemini** obtida em  
👉 [Google AI Studio](https://aistudio.google.com/app/apikey)

### 5️⃣ Rodar a API
```bash
uvicorn app.main:app --reload --port 8008
```

### 6️⃣ Testar no navegador
Abra o arquivo **`index.html`** e:
- Teste **/health** para verificar se a API está ativa;
- Teste **/ai/recommendations** e **/ai/motivation**;
- Faça upload de duas fotos em **/cv/verify** para verificação (SSIM + YOLO).

---

## 🧠 Como Funciona Cada Parte

| Componente | Função |
|-------------|--------|
| `/ai/recommendations` | Usa a IA Gemini para gerar trilhas de aprendizado sustentáveis personalizadas. |
| `/ai/motivation` | Gera mensagens motivacionais dinâmicas com base nos dados de economia (kWh, CO₂, custo). |
| `/cv/compare` | Compara duas imagens (antes/depois) e retorna o grau de diferença estrutural (SSIM). |
| `/cv/verify` | Usa SSIM + YOLO para confirmar se houve mudança real (ex.: troca de lâmpada). |
| `/health` | Endpoint simples para testar a saúde da aplicação e modelo ativo. |

---

## 🧩 Sobre o `requirements.txt`

O arquivo `requirements.txt` lista **todas as bibliotecas e versões necessárias** para rodar o projeto com consistência entre ambientes.  
Isso garante que, mesmo em outro computador ou servidor, o projeto instale **as mesmas dependências**, evitando erros de versão ou incompatibilidade.

> 💡 Ele é essencial para quem for clonar e executar o projeto localmente.

---

## 🔒 Segurança

- O arquivo `.env` com sua chave **não é commitado** (graças ao `.gitignore`).
- Outros usuários podem executar o código normalmente adicionando **suas próprias chaves**.
- Nunca exponha `GEMINI_API_KEY` diretamente no código ou em repositórios públicos.

---

## 🚀 Futuras Expansões

- Integração em tempo real com a **API Java** do Skill4Green.  
- Painel de monitoramento de impacto ambiental coletivo.  
- Treinamento de modelo YOLO específico para **troca de lâmpadas fluorescentes vs LED**.  
- Deploy automático via **Docker + GitHub Actions**.

---

## 👨‍💻 Autor

**Henzo Boschiero Puchetti**  
📍 [GitHub](https://github.com/henzopuchetti)

---

### ✅ Resumo Rápido
```bash
git clone https://github.com/henzopuchetti/Challenge-IOT.git
cd Challenge-IOT
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.sample .env   # adicione sua chave Gemini
uvicorn app.main:app --reload --port 8008
```
