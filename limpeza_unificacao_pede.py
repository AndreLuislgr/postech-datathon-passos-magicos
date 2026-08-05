"""
Datathon Passos Mágicos - Limpeza e Unificação da Base PEDE (2022, 2023, 2024)
--------------------------------------------------------------------------------
Objetivo: ler as 3 abas da planilha original (uma por ano, com colunas diferentes
entre si) e transformar em um único dataset "long" (uma linha por aluno-ano),
com nomes de colunas padronizados, prontos para EDA e modelagem preditiva.

Saída:
    - pede_unificado_long.csv   -> uma linha por (RA, Ano)
    - pede_unificado_wide.csv   -> uma linha por RA, com sufixo _2022/_2023/_2024

Uso:
    python limpeza_unificacao_pede.py
"""

import pandas as pd
import numpy as np
import unicodedata
import re

CAMINHO_XLSX = (
    "https://raw.githubusercontent.com/AndreLuislgr/"
    "postech-datathon-passos-magicos/main/"
    "BASE%20DE%20DADOS%20PEDE%202024%20-%20DATATHON.xlsx"
)
# Lendo direto do repositório GitHub (pandas aceita URL normalmente).
# Repare que o nome do arquivo no repositório usa ESPAÇOS
# ("BASE DE DADOS PEDE 2024 - DATATHON.xlsx"), por isso o link usa "%20"
# no lugar dos espaços (codificação de URL).
#
# Se preferir rodar localmente em vez de puxar do GitHub, troque a linha
# acima por um caminho relativo simples, com o arquivo na mesma pasta do
# script, por exemplo:
#
# CAMINHO_XLSX = "BASE DE DADOS PEDE 2024 - DATATHON.xlsx"
#
# Evite caminhos absolutos (tipo "/mnt/..." ou "C:\Users\...") -- eles
# quebram assim que o script roda em outra máquina/ambiente.

# ---------------------------------------------------------------------------
# 1. Mapeamento de colunas: nome original (por aba) -> nome padronizado
#    Baseado no dicionário de dados + inspeção das 3 abas.
# ---------------------------------------------------------------------------

MAPA_2022 = {
    "RA": "RA",
    "Fase": "FASE",
    "Turma": "TURMA",
    "Nome": "NOME",
    "Ano nasc": "ANO_NASC",
    "Idade 22": "IDADE",
    "Gênero": "GENERO",
    "Ano ingresso": "ANO_INGRESSO",
    "Instituição de ensino": "INSTITUICAO_ENSINO",
    "Pedra 20": "PEDRA_2020",
    "Pedra 21": "PEDRA_2021",
    "Pedra 22": "PEDRA",
    "INDE 22": "INDE",
    "Cg": "CG",
    "Cf": "CF",
    "Ct": "CT",
    "Nº Av": "QTDE_AVAL",
    "IAA": "IAA",
    "IEG": "IEG",
    "IPS": "IPS",
    "Rec Psicologia": "REC_PSICO",
    "IDA": "IDA",
    "Matem": "NOTA_MAT",
    "Portug": "NOTA_PORT",
    "Inglês": "NOTA_ING",
    "Indicado": "INDICADO_BOLSA",
    "Atingiu PV": "PONTO_VIRADA",
    "IPV": "IPV",
    "IAN": "IAN",
    "Fase ideal": "FASE_IDEAL",
    "Defas": "DEFASAGEM",
    "Destaque IEG": "DESTAQUE_IEG",
    "Destaque IDA": "DESTAQUE_IDA",
    "Destaque IPV": "DESTAQUE_IPV",
}

MAPA_2023 = {
    "RA": "RA",
    "Fase": "FASE",
    "INDE 2023": "INDE",
    "Pedra 2023": "PEDRA",
    "Turma": "TURMA",
    "Nome Anonimizado": "NOME",
    "Data de Nasc": "DATA_NASC",
    "Idade": "IDADE",
    "Gênero": "GENERO",
    "Ano ingresso": "ANO_INGRESSO",
    "Instituição de ensino": "INSTITUICAO_ENSINO",
    "Pedra 20": "PEDRA_2020",
    "Pedra 21": "PEDRA_2021",
    "Pedra 22": "PEDRA_2022",
    "Cg": "CG",
    "Cf": "CF",
    "Ct": "CT",
    "Nº Av": "QTDE_AVAL",
    "IAA": "IAA",
    "IEG": "IEG",
    "IPS": "IPS",
    "IPP": "IPP",
    "Rec Psicologia": "REC_PSICO",
    "IDA": "IDA",
    "Mat": "NOTA_MAT",
    "Por": "NOTA_PORT",
    "Ing": "NOTA_ING",
    "Indicado": "INDICADO_BOLSA",
    "Atingiu PV": "PONTO_VIRADA",
    "IPV": "IPV",
    "IAN": "IAN",
    "Fase Ideal": "FASE_IDEAL",
    "Defasagem": "DEFASAGEM",
    "Destaque IEG": "DESTAQUE_IEG",
    "Destaque IDA": "DESTAQUE_IDA",
    # OBS: "Destaque IPV" aparece duplicado no cabeçalho original de 2023;
    # o pandas renomeia automaticamente a segunda ocorrência para
    # "Destaque IPV.1" ao ler o Excel — tratamos isso no código abaixo.
    "Destaque IPV": "DESTAQUE_IPV",
}

MAPA_2024 = {
    "RA": "RA",
    "Fase": "FASE",
    "INDE 2024": "INDE",
    "Pedra 2024": "PEDRA",
    "Turma": "TURMA",
    "Nome Anonimizado": "NOME",
    "Data de Nasc": "DATA_NASC",
    "Idade": "IDADE",
    "Gênero": "GENERO",
    "Ano ingresso": "ANO_INGRESSO",
    "Instituição de ensino": "INSTITUICAO_ENSINO",
    "Pedra 20": "PEDRA_2020",
    "Pedra 21": "PEDRA_2021",
    "Pedra 22": "PEDRA_2022",
    "Pedra 23": "PEDRA_2023",
    "Cg": "CG",
    "Cf": "CF",
    "Ct": "CT",
    "Nº Av": "QTDE_AVAL",
    "IAA": "IAA",
    "IEG": "IEG",
    "IPS": "IPS",
    "IPP": "IPP",
    "Rec Psicologia": "REC_PSICO",
    "IDA": "IDA",
    "Mat": "NOTA_MAT",
    "Por": "NOTA_PORT",
    "Ing": "NOTA_ING",
    "Indicado": "INDICADO_BOLSA",
    "Atingiu PV": "PONTO_VIRADA",
    "IPV": "IPV",
    "IAN": "IAN",
    "Fase Ideal": "FASE_IDEAL",
    "Defasagem": "DEFASAGEM",
    "Destaque IEG": "DESTAQUE_IEG",
    "Destaque IDA": "DESTAQUE_IDA",
    "Destaque IPV": "DESTAQUE_IPV",
    "Escola": "ESCOLA",
    "Ativo/ Inativo": "STATUS_ATIVO",
}

# Colunas finais que queremos manter no dataset "long" (uma linha por aluno-ano)
COLUNAS_FINAIS = [
    "RA", "ANO", "NOME", "FASE", "TURMA", "GENERO", "IDADE",
    "ANO_INGRESSO", "INSTITUICAO_ENSINO", "ESCOLA", "STATUS_ATIVO",
    "PEDRA", "INDE",
    "IAN", "IDA", "IEG", "IAA", "IPS", "IPP", "IPV",
    "FASE_IDEAL", "DEFASAGEM", "PONTO_VIRADA", "INDICADO_BOLSA",
    "NOTA_MAT", "NOTA_PORT", "NOTA_ING",
    "CG", "CF", "CT", "QTDE_AVAL", "REC_PSICO",
    "DESTAQUE_IEG", "DESTAQUE_IDA", "DESTAQUE_IPV",
]


def normalizar_texto(s):
    """Remove acentos e espaços duplicados, para comparação de nomes de coluna."""
    if not isinstance(s, str):
        return s
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("utf-8")
    return re.sub(r"\s+", " ", s).strip()


def deduplicar_colunas(df):
    """
    Quando o Excel tem colunas com nome repetido (ex.: 'Destaque IPV' duas vezes
    em 2023, 'Ativo/ Inativo' duas vezes em 2024), o pandas as renomeia para
    'Destaque IPV' e 'Destaque IPV.1'. Aqui a gente combina as duas em uma só
    coluna (preenchendo valores nulos de uma com a outra) para não perder dado.
    """
    colunas_base = {}
    for col in df.columns:
        base = re.sub(r"\.\d+$", "", col)  # remove sufixo .1, .2 etc
        colunas_base.setdefault(base, []).append(col)

    for base, cols in colunas_base.items():
        if len(cols) > 1:
            # combina todas as variantes, priorizando a primeira não-nula
            combinado = df[cols[0]]
            for c in cols[1:]:
                combinado = combinado.combine_first(df[c])
            df = df.drop(columns=cols)
            df[base] = combinado
    return df


def carregar_e_padronizar(sheet_name, mapa, ano):
    print(f"Lendo aba {sheet_name}...")
    df = pd.read_excel(CAMINHO_XLSX, sheet_name=sheet_name)
    df = deduplicar_colunas(df)

    # Renomeia só as colunas que existem no mapa (evita erro se algo mudar)
    colunas_presentes = {k: v for k, v in mapa.items() if k in df.columns}
    df = df.rename(columns=colunas_presentes)

    df["ANO"] = ano

    # Garante que todas as colunas finais existam (preenche com NaN se faltar)
    for col in COLUNAS_FINAIS:
        if col not in df.columns:
            df[col] = np.nan

    return df[COLUNAS_FINAIS]


def limpar_tipos(df):
    """Corrige tipos de dados: números, booleanos, categorias."""

    # RA como string padronizada (remove "RA-" se quiser manter só o número, mas
    # aqui mantemos como veio para não perder rastreabilidade)
    df["RA"] = df["RA"].astype(str).str.strip()

    # Ano/Idade/Ano ingresso como inteiros (nullable, pois pode ter NaN)
    for col in ["ANO", "IDADE", "ANO_INGRESSO", "DEFASAGEM", "QTDE_AVAL"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # FASE_IDEAL vem como texto ("Fase 8 (Universitários)"), não número.
    # Mantemos como string e extraímos o número da fase à parte.
    df["FASE_IDEAL"] = df["FASE_IDEAL"].astype(str).str.strip()
    df.loc[df["FASE_IDEAL"].isin(["nan", "None", ""]), "FASE_IDEAL"] = np.nan
    df["FASE_IDEAL_NUM"] = df["FASE_IDEAL"].str.extract(r"(\d+)").astype(float)

    # Fase: em 2022 vem como número ("7"), em 2023/2024 vem como nome de etapa
    # ("ALFA", "1", "2" etc.). Mantemos como string para preservar ambos os
    # formatos, mas criamos uma versão numérica quando possível.
    df["FASE"] = df["FASE"].astype(str).str.strip()
    df["FASE_NUM"] = pd.to_numeric(df["FASE"], errors="coerce")

    # Indicadores numéricos (0 a 10)
    indicadores = ["INDE", "IAN", "IDA", "IEG", "IAA", "IPS", "IPP", "IPV",
                    "NOTA_MAT", "NOTA_PORT", "NOTA_ING", "CG", "CF", "CT"]
    for col in indicadores:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Zeros em indicadores de avaliação (IAA, IEG, IPS, IDA, IPV, IAN) muitas
    # vezes representam "não avaliado" e não uma nota real de 0. Isso aparece
    # nos exemplos (ex.: IAA = 0.0 junto de outros indicadores normais).
    # Deixamos um flag para não confundir "nota baixa real" com "não avaliado"
    # sem apagar o dado -- decisão de tratamento fica documentada aqui, ajuste
    # conforme sua análise de outliers (IQR) mostrar necessário.
    for col in ["IAA", "IEG", "IPS", "IDA", "IPV", "IAN"]:
        df[f"{col}_FLAG_ZERO"] = df[col] == 0

    # Booleanos: Sim/Não -> True/False
    mapa_bool = {"Sim": True, "Não": False, "sim": True, "não": False}
    for col in ["PONTO_VIRADA", "INDICADO_BOLSA"]:
        df[col] = df[col].map(mapa_bool).where(df[col].isin(mapa_bool.keys()), df[col])

    # Pedra: padroniza capitalização, acentuação e remove espaços.
    # A planilha mistura "Agata" (sem acento) e "Ágata" (com acento) como se
    # fossem categorias diferentes -- normalizamos para uma só.
    df["PEDRA"] = df["PEDRA"].astype(str).str.strip().str.title()
    df.loc[df["PEDRA"].isin(["Nan", "None", ""]), "PEDRA"] = np.nan
    df["PEDRA"] = df["PEDRA"].replace({"Agata": "Ágata"})
    # "Incluir" não é uma classificação de Pedra válida -- aparece como
    # placeholder para alunos sem INDE calculado ainda (ex.: recém-ingressos
    # em 2024 sem avaliação completa). Tratamos como dado ausente.
    df.loc[df["PEDRA"] == "Incluir", "PEDRA"] = np.nan

    # Gênero: padroniza (Menina/Feminino -> Feminino, Menino/Masculino -> Masculino)
    mapa_genero = {
        "Menina": "Feminino", "Feminino": "Feminino",
        "Menino": "Masculino", "Masculino": "Masculino",
    }
    df["GENERO"] = df["GENERO"].map(mapa_genero).fillna(df["GENERO"])

    return df


def remover_outliers_iqr(df, colunas, grupo_col="ANO"):
    """
    Marca outliers via IQR (1.5x) por indicador, calculado dentro de cada ano
    (mesma lógica usada no seu script Spread On-Off). Não remove as linhas,
    apenas sinaliza -- decisão de excluir ou não fica para a etapa de EDA.
    """
    df = df.copy()
    for col in colunas:
        flag_col = f"{col}_OUTLIER"
        df[flag_col] = False
        for ano, grupo in df.groupby(grupo_col):
            serie = grupo[col].dropna()
            if len(serie) < 5:
                continue
            q1, q3 = serie.quantile([0.25, 0.75])
            iqr = q3 - q1
            lim_inf, lim_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            idx_outlier = grupo[(grupo[col] < lim_inf) | (grupo[col] > lim_sup)].index
            df.loc[idx_outlier, flag_col] = True
    return df


def validar(df):
    """Checagens básicas de sanidade do dataset final."""
    print("\n--- Validação ---")
    print("Linhas totais:", len(df))
    print("Anos presentes:", sorted(df['ANO'].dropna().unique()))
    print("RAs únicos:", df['RA'].nunique())
    print("\nNulos por coluna (top 15):")
    print(df.isna().sum().sort_values(ascending=False).head(15))

    # Aviso explícito: algumas colunas são 100% nulas em certos anos porque a
    # planilha ORIGINAL não preenche esses campos nesses anos (confirmado por
    # inspeção manual) -- não é um bug de leitura/merge deste script.
    colunas_possivelmente_ausentes_por_ano = [
        "CG", "CF", "CT", "PONTO_VIRADA", "REC_PSICO",
        "DESTAQUE_IEG", "DESTAQUE_IDA", "DESTAQUE_IPV",
    ]
    print("\nCobertura por ano das colunas frequentemente ausentes na fonte "
          "(pode ser 0% em determinado ano -- isso é um buraco da planilha "
          "original, não erro deste script):")
    for col in colunas_possivelmente_ausentes_por_ano:
        cobertura = df.groupby("ANO")[col].apply(lambda s: s.notna().mean() * 100)
        print(f"  {col}: " + ", ".join(f"{int(ano)}={p:.0f}%" for ano, p in cobertura.items()))

    faixa_indicadores = ["INDE", "IAN", "IDA", "IEG", "IAA", "IPS", "IPP", "IPV"]
    print("\nValores fora da faixa 0-10 (na maioria dos casos é ruído de "
          "arredondamento da planilha original, ex.: 10.002 em vez de 10.0 -- "
          "não costuma ser erro de dado real; vale checar caso a caso se o "
          "excesso for grande):")
    algum_fora_faixa = False
    for col in faixa_indicadores:
        fora_faixa = df[(df[col] < 0) | (df[col] > 10)][col].dropna()
        if len(fora_faixa) > 0:
            algum_fora_faixa = True
            excesso_max = max((fora_faixa - 10).max(), (0 - fora_faixa).max())
            print(f"  {col}: {len(fora_faixa)} valores (desvio máx. de {excesso_max:.3f} "
                  f"em relação ao limite 0-10)")
    if not algum_fora_faixa:
        print("  Nenhum valor fora da faixa 0-10.")


def main():
    df22 = carregar_e_padronizar("PEDE2022", MAPA_2022, 2022)
    df23 = carregar_e_padronizar("PEDE2023", MAPA_2023, 2023)
    df24 = carregar_e_padronizar("PEDE2024", MAPA_2024, 2024)

    df_long = pd.concat([df22, df23, df24], ignore_index=True)
    df_long = limpar_tipos(df_long)

    colunas_indicadores = ["INDE", "IAN", "IDA", "IEG", "IAA", "IPS", "IPP", "IPV"]
    df_long = remover_outliers_iqr(df_long, colunas_indicadores)

    validar(df_long)

    df_long.to_csv("pede_unificado_long.csv", index=False, encoding="utf-8-sig")
    print("\nSalvo: pede_unificado_long.csv (uma linha por aluno-ano)")

    # Versão wide: uma linha por aluno, colunas com sufixo do ano
    df_wide = df_long.pivot_table(
        index=["RA", "NOME", "GENERO", "ANO_INGRESSO"],
        columns="ANO",
        values=[c for c in COLUNAS_FINAIS if c not in
                ["RA", "NOME", "GENERO", "ANO_INGRESSO", "ANO"]],
        aggfunc="first",
    )
    df_wide.columns = [f"{col}_{int(ano)}" for col, ano in df_wide.columns]
    df_wide = df_wide.reset_index()
    df_wide.to_csv("pede_unificado_wide.csv", index=False, encoding="utf-8-sig")
    print("Salvo: pede_unificado_wide.csv (uma linha por aluno, colunas por ano)")


if __name__ == "__main__":
    main()
