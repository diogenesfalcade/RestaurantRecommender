# Sistema de Recomendação de Restaurantes com Análise de Sentimentos

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-2.2-150458?logo=pandas)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.5-F7931E?logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Este repositório contém o código e a documentação do Projeto de Conclusão **"Sistema de Recomendação de Restaurantes por Filtragem Baseada em Conteúdo com Análise de Sentimentos"**, apresentado ao Programa de Especialização em Data Science e Big Data da Universidade Federal do Paraná (UFPR).

---

## Aplicação

Você pode testar a aplicação diretamente na Streamlit Community Cloud:

🔗 **[Acesse aqui](https://restaurantrecommender.streamlit.app/)**

### Interface da Aplicação
![Interface da Aplicação](https://i.imgur.com/Q8aERiI.png)

---

## O Projeto

Este projeto implementa um sistema de recomendação de restaurantes com base em filtragem baseada em conteúdo, enriquecido por uma análise de sentimentos aplicada às avaliações textuais dos usuários. O objetivo é oferecer sugestões personalizadas que conciliem relevância, reputação e diversidade.

Os dados utilizados abrangem 2.181 restaurantes de Curitiba, coletados via APIs públicas do Google Maps e TripAdvisor. As recomendações são pré-processadas e armazenadas em formato `.parquet`, otimizando a velocidade da aplicação web desenvolvida com Streamlit.

> Desenvolvido por **Diógenes Antonio Falcade Pereira**, com orientação do Prof. **Marcos A. Zanata Alves**.

---

## Funcionalidades

- 🔍 **Recomendações por Similaridade:** Sugestões personalizadas com base em um escore ponderado entre similaridade, avaliação geral e sentimento.
- 💬 **Análise de Sentimentos:** Classificação automática (positivo, neutro ou negativo) das avaliações com um modelo leve (_LLM Ollama 3.2 1B_).
- 🌟 **Sugestões Adicionais para Descoberta:**
  - Dois restaurantes populares, aleatórios entre os 100 melhores.
  - Uma "joia escondida": restaurante com menos de 100 avaliações, sentimento positivo e alta similaridade.
- ⚡ **Interface Rápida e Intuitiva:** Desenvolvida com _Streamlit_, com carregamento em cache.
- 🚀 **Desempenho Otimizado:** Tempo de resposta inferior a 1 segundo, graças ao pré-processamento.

---

## Arquitetura e Metodologia

O sistema foi dividido em duas etapas principais: processamento offline intensivo e interface web leve.

### 1. Coleta de Dados
- APIs: _Google Maps Places_ e _TripAdvisor_
- Período: janeiro–fevereiro de 2025
- Armazenamento em banco **PostgreSQL**

### 2. Análise de Sentimentos
- Mais de 24 mil comentários classificados com _Ollama 3.2 1B (local)_
- Métrica: `score de sentimento = %positivas - %negativas`

### 3. Engenharia de Atributos e PCA
- Variáveis categóricas transformadas → ~154 atributos
- Redução de dimensionalidade com **PCA** (preservando 95% da variância)

### 4. Similaridade e Escore Ponderado
- Métrica de similaridade: **distância do cosseno**
- Fatores para o ranking final:
  - 70% Similaridade
  - 20% Nota média
  - 10% Score de sentimento

### 5. Pré-processamento e Exportação
- Recomendações calculadas offline
- Exportadas para `.parquet` para leitura eficiente com Pandas

### 6. Interface Web
- Construída com **Streamlit**
- Carrega os dados em cache (sem recomputação online)

---

## Tech Stack

| Camada             | Ferramentas                                      |
|--------------------|--------------------------------------------------|
| Linguagem          | Python 3.11                                      |
| Dados              | Pandas, Scikit-learn, SQLAlchemy                 |
| Interface          | Streamlit                                        |
| Banco de Dados     | PostgreSQL                                       |
| Coleta de Dados    | APIs do Google Maps e TripAdvisor                |
| NLP                | Ollama 3.2 1B (LLM local para análise de sentimentos) |

---

![Fluxo do Sistema](https://i.imgur.com/Nkv46wB.png)  
<sub>*Fluxograma do sistema, conforme Figura 1 do documento técnico.*</sub>

## Executando Localmente

### 1. Clone o repositório
```bash
git clone https://github.com/diogenesfalcade/RestaurantRecommender
cd RestaurantRecommender
```

### 2.  **Crie e ative um ambiente virtual:**
```bash
python -m venv pyvenv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3.  **Instale as dependências:**
```bash
pip install -r requirements.txt
```

### 4.  **Execute a aplicação Streamlit:**
```bash
streamlit run app.py
```
