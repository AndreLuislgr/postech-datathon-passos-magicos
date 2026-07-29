# Datathon Passos Mágicos — PosTech

Análise de dados e modelo preditivo de risco de defasagem escolar para a
**Associação Passos Mágicos**, com base na pesquisa PEDE (Pesquisa Extensiva
do Desenvolvimento Educacional) de 2022, 2023 e 2024.

## 🎯 Sobre o projeto

A Passos Mágicos atua há 35 anos na transformação da vida de crianças e
jovens em vulnerabilidade social por meio da educação. Este projeto usa os
dados do PEDE para responder perguntas de negócio sobre desempenho,
engajamento e efetividade do programa, além de construir um modelo preditivo
que estima o **risco de um aluno entrar em defasagem** no ano seguinte.

## 📁 Estrutura do repositório

```
├── app.py                                  # App Streamlit (predição de risco)
├── requirements.txt                        # Dependências do app
├── modelo_risco_defasagem.pkl              # Modelo treinado (Random Forest)
├── schema_features.json                    # Schema das features esperadas pelo modelo
├── limpeza_unificacao_pede.py               # Script de limpeza e unificação da base
├── eda_datathon_pede.py                     # Script de EDA (respostas às 11 perguntas)
├── modelo_preditivo_risco_defasagem.ipynb  # Notebook: feature engineering, treino, avaliação
├── pede_unificado_long.csv                 # Base tratada (1 linha por aluno-ano)
├── pede_unificado_wide.csv                 # Base tratada (1 linha por aluno, colunas por ano)
└── graficos_eda/                           # Gráficos gerados pela EDA
```

## 🧹 1. Limpeza e unificação dos dados

`limpeza_unificacao_pede.py` lê as 3 abas da planilha original (uma por ano,
cada uma com nomenclatura diferente de colunas), padroniza nomes, corrige
tipos, resolve colunas duplicadas do Excel, normaliza categorias (ex.:
"Agata" vs "Ágata") e sinaliza outliers via IQR — sem removê-los, apenas
marcando para decisão posterior.

```bash
python limpeza_unificacao_pede.py
```

Gera `pede_unificado_long.csv` e `pede_unificado_wide.csv`.

## 📊 2. Análise exploratória (EDA)

`eda_datathon_pede.py` responde às 11 perguntas do desafio (adequação de
nível, desempenho acadêmico, engajamento, autoavaliação, aspectos
psicossociais/psicopedagógicos, ponto de virada, multidimensionalidade dos
indicadores e efetividade do programa), gerando os gráficos em
`graficos_eda/`.

```bash
python eda_datathon_pede.py
```

**Principais achados:**
- Defasagem severa caiu de 47,7% (2022) para 38,1% (2024) dos alunos.
- IDA (desempenho acadêmico) melhorou de 6,09 para 6,66 (2022→2023) e se
  manteve estável em 2024 (6,35).
- Autoavaliação (IAA) tem correlação fraca com desempenho real (r=0,13).
- Ponto de Virada (IPV) é mais influenciado por IPP (0,61), IEG (0,56) e
  IDA (0,56).
- INDE é mais elevado por IDA (0,79), IEG (0,75) e IPV (0,72).

## 🤖 3. Modelo preditivo de risco de defasagem

`modelo_preditivo_risco_defasagem.ipynb` constrói o modelo que estima a
probabilidade de um aluno entrar em risco de defasagem no ano seguinte,
com as etapas:

1. **Feature engineering**: indicadores do ano corrente (IAN, IDA, IEG, IAA,
   IPS, IPP, IPV, INDE, defasagem) + Pedra/Gênero + features derivadas
   (`GAP_ENGAJAMENTO_APRENDIZAGEM`, `TEMPO_NA_PM`)
2. **Split treino/teste** estratificado (75/25)
3. **Modelagem**: comparação entre Regressão Logística e Random Forest
4. **Avaliação**: classification report, matriz de confusão, curva ROC,
   importância de variáveis

**Resultado:** Random Forest com AUC-ROC de 0,79 e recall de 75% na classe
de risco.

## 🖥️ 4. App Streamlit

`app.py` carrega o modelo treinado e permite inserir os indicadores de um
aluno para obter a probabilidade de risco de defasagem.

**Rodar localmente:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

**App em produção:** [link do deploy no Streamlit Community Cloud aqui]

## 📹 5. Vídeo de apresentação

[link do vídeo aqui]

## 🗂️ Fonte dos dados

Base de dados e dicionário de dados fornecidos pela PosTech/Associação
Passos Mágicos (Datathon Fase 5).

## 👤 Autor

André — Datathon PosTech, Fase 5.
