"""
Datathon Passos Mágicos - EDA respondendo às perguntas do enunciado
--------------------------------------------------------------------
Lê o dataset já limpo/unificado (pede_unificado_long.csv) e gera os gráficos
e estatísticas que respondem às perguntas 1 a 10 do enunciado. A pergunta 11
(insights livres) é tratada ao final com base nos achados anteriores.

Saída: gráficos em /mnt/user-data/outputs/graficos_eda/
       resumo textual impresso no console (para colar na apresentação)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme(style="whitegrid")
PASTA_SAIDA = "/mnt/user-data/outputs/graficos_eda"
os.makedirs(PASTA_SAIDA, exist_ok=True)

df = pd.read_csv("/mnt/user-data/outputs/pede_unificado_long.csv")

CORES_PEDRA = {"Quartzo": "#8a8a8a", "Ágata": "#c07a3e", "Ametista": "#7d5ba6", "Topázio": "#e8b923"}


def salvar(fig, nome):
    fig.tight_layout()
    fig.savefig(f"{PASTA_SAIDA}/{nome}.png", dpi=150)
    plt.close(fig)
    print(f"  -> salvo: {nome}.png")


# =============================================================================
# Q1 - Adequação do nível (IAN): perfil de defasagem e evolução ao longo do ano
# =============================================================================
print("\n=== Q1: Adequação do nível (IAN) ===")

def classificar_defasagem(d):
    if pd.isna(d):
        return np.nan
    if d >= 0:
        return "Sem defasagem"
    if d == -1:
        return "Defasagem leve (-1)"
    return "Defasagem moderada/severa (<=-2)"

df["CLASSE_DEFASAGEM"] = df["DEFASAGEM"].apply(classificar_defasagem)

tab_defasagem = df.groupby(["ANO", "CLASSE_DEFASAGEM"]).size().unstack(fill_value=0)
tab_defasagem_pct = tab_defasagem.div(tab_defasagem.sum(axis=1), axis=0) * 100
print(tab_defasagem_pct.round(1))

fig, ax = plt.subplots(figsize=(8, 5))
tab_defasagem_pct.plot(kind="bar", stacked=True, ax=ax,
                        color=["#2e7d32", "#f9a825", "#c62828"])
ax.set_ylabel("% de alunos")
ax.set_title("Q1 - Perfil de defasagem (IAN) por ano")
ax.legend(title="Classe", bbox_to_anchor=(1.02, 1), loc="upper left")
salvar(fig, "q1_defasagem_por_ano")

fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=df, x="ANO", y="IAN", ax=ax, color="#4a90d9")
ax.set_title("Q1 - Distribuição do IAN por ano")
salvar(fig, "q1_ian_boxplot")


# =============================================================================
# Q2 - Desempenho acadêmico (IDA): melhora, estagna ou cai ao longo dos anos?
# =============================================================================
print("\n=== Q2: Desempenho acadêmico (IDA) ===")
ida_por_ano = df.groupby("ANO")["IDA"].agg(["mean", "median", "std", "count"])
print(ida_por_ano.round(2))

ida_por_fase_ano = df.groupby(["ANO", "FASE"])["IDA"].mean().unstack(0)

fig, ax = plt.subplots(figsize=(8, 5))
sns.pointplot(data=df, x="ANO", y="IDA", ax=ax, color="#c62828", errorbar="ci")
ax.set_title("Q2 - Evolução do IDA médio ao longo dos anos")
salvar(fig, "q2_ida_evolucao")


# =============================================================================
# Q3 - Engajamento (IEG) x desempenho (IDA) e ponto de virada (IPV)
# =============================================================================
print("\n=== Q3: Engajamento (IEG) x IDA e IPV ===")
corr_ieg = df[["IEG", "IDA", "IPV"]].corr()
print(corr_ieg.round(2))

fig, axes = plt.subplots(1, 2, figsize=(11, 5))
sns.regplot(data=df, x="IEG", y="IDA", ax=axes[0], scatter_kws={"alpha": 0.2}, color="#4a90d9")
axes[0].set_title(f"IEG x IDA (r={corr_ieg.loc['IEG','IDA']:.2f})")
sns.regplot(data=df, x="IEG", y="IPV", ax=axes[1], scatter_kws={"alpha": 0.2}, color="#7d5ba6")
axes[1].set_title(f"IEG x IPV (r={corr_ieg.loc['IEG','IPV']:.2f})")
fig.suptitle("Q3 - Relação entre engajamento e desempenho/ponto de virada")
salvar(fig, "q3_ieg_ida_ipv")


# =============================================================================
# Q4 - Autoavaliação (IAA) x desempenho real (IDA) e engajamento (IEG)
# =============================================================================
print("\n=== Q4: Autoavaliação (IAA) x IDA/IEG ===")
# Remove zeros-flag (provável "não avaliado") antes de correlacionar
df_iaa_valido = df[~df["IAA_FLAG_ZERO"]]
corr_iaa = df_iaa_valido[["IAA", "IDA", "IEG"]].corr()
print(corr_iaa.round(2))

fig, axes = plt.subplots(1, 2, figsize=(11, 5))
sns.regplot(data=df_iaa_valido, x="IAA", y="IDA", ax=axes[0], scatter_kws={"alpha": 0.2}, color="#e8b923")
axes[0].set_title(f"IAA x IDA (r={corr_iaa.loc['IAA','IDA']:.2f})")
sns.regplot(data=df_iaa_valido, x="IAA", y="IEG", ax=axes[1], scatter_kws={"alpha": 0.2}, color="#2e7d32")
axes[1].set_title(f"IAA x IEG (r={corr_iaa.loc['IAA','IEG']:.2f})")
fig.suptitle("Q4 - Autoavaliação vs desempenho real e engajamento")
salvar(fig, "q4_iaa_ida_ieg")


# =============================================================================
# Q5 - Aspectos psicossociais (IPS): padrões que antecedem quedas
# =============================================================================
print("\n=== Q5: IPS antecede quedas de desempenho/engajamento? ===")
# Usa dataset wide para comparar IPS(ano N) com variação de IDA/IEG (N -> N+1)
wide = pd.read_csv("/mnt/user-data/outputs/pede_unificado_wide.csv")

for ano_ini, ano_fim in [(2022, 2023), (2023, 2024)]:
    col_ips = f"IPS_{ano_ini}"
    col_ida_ini, col_ida_fim = f"IDA_{ano_ini}", f"IDA_{ano_fim}"
    if col_ips in wide.columns and col_ida_ini in wide.columns and col_ida_fim in wide.columns:
        tmp = wide[[col_ips, col_ida_ini, col_ida_fim]].dropna()
        tmp["QUEDA_IDA"] = tmp[col_ida_fim] < tmp[col_ida_ini]
        media_ips_queda = tmp.groupby("QUEDA_IDA")[col_ips].mean()
        print(f"IPS médio em {ano_ini} | sem queda de IDA em {ano_fim}: {media_ips_queda.get(False, float('nan')):.2f} "
              f"| com queda: {media_ips_queda.get(True, float('nan')):.2f}")

fig, ax = plt.subplots(figsize=(7, 5))
sns.boxplot(data=df, x="ANO", y="IPS", ax=ax, color="#4a90d9")
ax.set_title("Q5 - Distribuição do IPS por ano")
salvar(fig, "q5_ips_por_ano")


# =============================================================================
# Q6 - Avaliação psicopedagógica (IPP) confirma ou contradiz o IAN?
# =============================================================================
print("\n=== Q6: IPP x IAN (concordância) ===")
df_ipp = df.dropna(subset=["IPP", "IAN"])
corr_ipp_ian = df_ipp[["IPP", "IAN"]].corr().iloc[0, 1]
print(f"Correlação IPP x IAN: {corr_ipp_ian:.2f}  (n={len(df_ipp)})")

fig, ax = plt.subplots(figsize=(7, 6))
sns.scatterplot(data=df_ipp, x="IAN", y="IPP", alpha=0.3, ax=ax, color="#c62828")
ax.set_title(f"Q6 - IPP x IAN (r={corr_ipp_ian:.2f})")
salvar(fig, "q6_ipp_ian")


# =============================================================================
# Q7 - Ponto de virada (IPV): quais comportamentos mais influenciam?
# =============================================================================
print("\n=== Q7: Fatores associados ao Ponto de Virada ===")
indicadores = ["IAN", "IDA", "IEG", "IAA", "IPS", "IPP"]
corr_ipv = df[indicadores + ["IPV"]].corr()["IPV"].drop("IPV").sort_values(ascending=False)
print(corr_ipv.round(2))

fig, ax = plt.subplots(figsize=(7, 5))
corr_ipv.plot(kind="barh", ax=ax, color="#7d5ba6")
ax.set_title("Q7 - Correlação de cada indicador com o IPV")
ax.set_xlabel("Correlação de Pearson")
salvar(fig, "q7_correlacao_ipv")


# =============================================================================
# Q8 - Multidimensionalidade: combinações que mais elevam o INDE
# =============================================================================
print("\n=== Q8: Quais indicadores mais elevam o INDE? ===")
indicadores_inde = ["IAN", "IDA", "IEG", "IAA", "IPS", "IPP", "IPV"]
corr_inde = df[indicadores_inde + ["INDE"]].corr()["INDE"].drop("INDE").sort_values(ascending=False)
print(corr_inde.round(2))

fig, ax = plt.subplots(figsize=(7, 5))
corr_inde.plot(kind="barh", ax=ax, color="#2e7d32")
ax.set_title("Q8 - Correlação de cada indicador com o INDE")
ax.set_xlabel("Correlação de Pearson")
salvar(fig, "q8_correlacao_inde")

fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(df[indicadores_inde + ["INDE"]].corr(), annot=True, fmt=".2f", cmap="RdYlGn", ax=ax)
ax.set_title("Q8 - Matriz de correlação entre indicadores e INDE")
salvar(fig, "q8_heatmap_correlacoes")


# =============================================================================
# Q9 - Nota sobre o modelo preditivo (feito em notebook separado)
# =============================================================================
print("\n=== Q9: Modelo preditivo de risco de defasagem -> ver notebook separado ===")


# =============================================================================
# Q10 - Efetividade do programa: indicadores melhoram nas fases/ciclo?
# =============================================================================
print("\n=== Q10: Efetividade do programa por Pedra/Fase ===")
inde_por_pedra_ano = df.groupby(["ANO", "PEDRA"])["INDE"].mean().unstack()
print(inde_por_pedra_ano.round(2))

fig, ax = plt.subplots(figsize=(8, 5))
ordem_pedra = ["Quartzo", "Ágata", "Ametista", "Topázio"]
for pedra in ordem_pedra:
    if pedra in inde_por_pedra_ano.columns:
        ax.plot(inde_por_pedra_ano.index, inde_por_pedra_ano[pedra],
                marker="o", label=pedra, color=CORES_PEDRA[pedra])
ax.set_title("Q10 - INDE médio por Pedra ao longo dos anos")
ax.set_ylabel("INDE médio")
ax.legend(title="Pedra")
salvar(fig, "q10_inde_por_pedra")

# Taxa de ponto de virada por ano
pv_por_ano = df.groupby("ANO")["PONTO_VIRADA"].apply(lambda s: s.map({True: 1, False: 0}).mean() * 100)
print("\nTaxa de Ponto de Virada por ano (%):")
print(pv_por_ano.round(1))
anos_sem_dado_pv = pv_por_ano[pv_por_ano.isna()].index.tolist()
if anos_sem_dado_pv:
    print(f"AVISO: {anos_sem_dado_pv} aparecem como NaN porque a coluna "
          f"'Atingiu PV' está 100% ausente na planilha original nesses anos "
          f"(confirmado -- não é erro de leitura). Não usar esses anos para "
          f"comparação de Ponto de Virada na apresentação sem citar essa limitação.")


print("\n\nGráficos salvos em:", PASTA_SAIDA)
print("Use os prints acima (tabelas e correlações) como base numérica para os slides.")
