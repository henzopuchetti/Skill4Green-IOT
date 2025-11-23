# 🌱 Skill4Green — Módulo de IA & IoT (Global Solution)

**Repositório:** [github.com/henzopuchetti/Skill4Green-IOT](https://github.com/henzopuchetti/Skill4Green-IOT)

---

## 💡 Visão Geral

O **Skill4Green** é um projeto que une **Inteligência Artificial**, **IoT** e **Sustentabilidade Corporativa**.  
Ele analisa, recomenda e valida ações sustentáveis realizadas por colaboradores, transformando economia de energia em aprendizado e engajamento.

Este módulo em **Python (FastAPI)** integra:

- 🌍 **IA Generativa (Groq – Llama 3.3 70B)** para gerar recomendações e mensagens motivacionais personalizadas;
- 🧠 **Visão Computacional (YOLO + SSIM)** para verificar automaticamente se uma tarefa física foi realmente executada (ex.: troca de lâmpadas fluorescentes por LED);
- 🔌 **Integração com API Java** (via HTTP), permitindo que o backend principal consuma as respostas e métricas em tempo real.

---

## ⚙️ Tecnologias Utilizadas

| Tecnologia              | Função                                                     |
|------------------------|------------------------------------------------------------|
| **FastAPI**            | Framework web para construção da API.                     |
| **Uvicorn**            | Servidor ASGI para rodar a aplicação FastAPI.             |
| **Groq (Llama 3.3 70B)** | Modelo de IA generativa usado para gerar recomendações e mensagens. |
| **OpenCV + scikit-image (SSIM)** | Análise estrutural de imagens “antes e depois”.      |
| **Ultralytics YOLO**   | Modelo de visão computacional para detectar mudanças reais em objetos. |
| **httpx**              | Cliente HTTP assíncrono para comunicação com a API da Groq. |
| **python-dotenv**      | Gerencia variáveis sensíveis (como a chave da API) em um arquivo `.env`. |
| **python-multipart**   | Necessário para upload de imagens.                         |
| **torch / torchvision**| Suporte à inferência do YOLO em CPU.                      |

---

## 🧾 Estrutura do Projeto

```txt
Skill4Green-IOT/
│
├── app/
│   ├── main.py             # Ponto principal da API (rotas FastAPI)
│   ├── groq_client.py      # Integração com API Groq (LLM)
│   ├── cv.py               # Comparação de imagens (SSIM)
│   ├── cv_yolo.py          # Análise de imagens com YOLO
│   ├── prompts.py          # Templates de prompts da IA
│   ├── config.py           # Configurações globais e variáveis de ambiente
│   └── __init__.py
│
├── web/
│   ├── index.html          # Interface simples para testes (IA + CV)
│   └── style.css           # Estilos da interface de teste
│
├── requirements.txt        # Dependências da aplicação
├── .gitignore              # Ignora arquivos locais e sensíveis
├── .env.sample             # Exemplo de arquivo .env (sem a sua chave real)
└── README.md               # Documentação do projeto
```

---

## 🔐 Sobre o arquivo `.env`

O `.env` **não é versionado** (está no `.gitignore`), o que significa que **ninguém verá a sua chave de API**.  
No repositório, você deixa apenas o modelo `.env.sample`, por exemplo:

```env
# .env.sample (arquivo exemplo)
GROQ_API_KEY=COLOQUE_SUA_CHAVE_GROQ_AQUI
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE=https://api.groq.com/openai/v1
EMISSION_FACTOR=0.084
TARIFF_KWH=0.95
YOLO_MODEL_PATH=yolo11n.pt
SSIM_THRESHOLD=0.75
YOLO_DELTA_MIN=1
```

Cada pessoa que for rodar o projeto localmente cria o próprio `.env` baseado nesse modelo.

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
.venv\Scripts\activate   # Windows
# ou
source .venv/bin/activate  # Linux/Mac
```

### 3️⃣ Atualizar o pip e instalar dependências

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Criar o arquivo `.env`

Crie um arquivo com o nome de .env, copie o conteudo de .env.sample.

Abra o `.env` e adicione **sua chave da API da Groq** obtida em  
👉 https://console.groq.com

### 5️⃣ Rodar a API

```bash
uvicorn app.main:app --reload --port 8008
```

### 6️⃣ Testar no navegador

Abra o arquivo **`web/index.html`** (clique duas vezes ou sirva via live server) e:

- Teste **/health** para verificar se a API está ativa e qual modelo Groq está sendo usado;
- Teste **/ai/recommendations** para gerar recomendações sustentáveis por setor/perfil;
- Teste **/ai/motivation** para gerar mensagem motivacional + cálculo automático de kWh, CO₂ e R$ com base na tarefa escolhida;
- Faça upload de duas fotos em **/cv/verify** para verificação (SSIM + YOLO).

---

## 🧠 Como Funciona Cada Parte

| Componente                    | Função |
|------------------------------|--------|
| `/ai/recommendations`        | Usa a Groq (Llama 3.3) para gerar tarefas sustentáveis específicas por setor e perfil do usuário. |
| `/ai/recommendations/refresh`| Gera um novo conjunto de recomendações para o mesmo contexto do usuário. |
| `/ai/motivation`             | Calcula kWh / CO₂ / R$ com base no `task_code` e quantidade de execuções e gera uma mensagem motivacional. |
| `/cv/verify`                 | Usa SSIM + YOLO para confirmar se houve mudança real entre as imagens antes/depois (ex.: troca de lâmpada). |
| `/health`                    | Endpoint simples para testar a saúde da aplicação e modelo ativo. |

---

## 🧩 Sobre o `requirements.txt`

O arquivo `requirements.txt` lista **todas as bibliotecas e versões necessárias** para rodar o projeto com consistência entre ambientes.  
Isso garante que, mesmo em outro computador ou servidor, o projeto instale **as mesmas dependências**, evitando erros de versão ou incompatibilidade.

---

## 🔒 Segurança

- O arquivo `.env` com sua chave **não é commitado** (graças ao `.gitignore`).
- Outros usuários podem executar o código normalmente adicionando **suas próprias chaves**.
- Nunca exponha `GROQ_API_KEY` diretamente no código ou em repositórios públicos.

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
git clone https://github.com/henzopuchetti/Skill4Green-IOT.git
cd Skill4Green-IOT
python -m venv .venv
.\.venv\Scriptsctivate  # ou source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.sample .env       # adicione sua chave Groq
uvicorn app.main:app --reload --port 8008
```
