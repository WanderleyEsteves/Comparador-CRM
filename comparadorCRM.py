# Importando bibliotecas

import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from src.normalizador import padronizar_dados_empresa
from src.statusCompliance import (
    classificar_risco,
    verificar_alerta_inscricao,
    verificar_especialidade,
)


BASE_DIR = Path(__file__).parent
PASTA_CFM_ZIP = BASE_DIR / "dados" / "cfm_zip"
PASTA_EMPRESA = BASE_DIR / "dados" / "empresa"
PASTA_RESULTADO = BASE_DIR / "dados" / "resultado"
COLUNAS_CFM = ["CRM", "UF", "Nome", "Tipo_Inscricao", "Situacao_Inscricao", "Especialidade"]


def encontrar_arquivo(pasta, extensao, descricao):
    arquivos = sorted(pasta.glob(f"*{extensao}"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo {descricao} encontrado em {pasta}")
    return arquivos[0]


def juntar_especialidades(especialidades):
    especialidades_unicas = []

    for especialidade in especialidades:
        if especialidade and especialidade not in especialidades_unicas:
            especialidades_unicas.append(especialidade)

    return ", ".join(especialidades_unicas)


def ler_cfm(arquivo_zip):
    registros = []

    with zipfile.ZipFile(arquivo_zip, "r") as zip_cfm:
        arquivos_txt = [
            nome for nome in zip_cfm.namelist()
            if nome.lower().endswith(".txt") and not nome.startswith("__MACOSX")
        ]

        if not arquivos_txt:
            raise ValueError("O ZIP não possui arquivos TXT do CFM.")

        print(f"Total de arquivos de médicos encontrados: {len(arquivos_txt)}")

        for nome_arquivo in arquivos_txt:
            print(f"Lendo arquivo CFM: {nome_arquivo}")
            conteudo = zip_cfm.read(nome_arquivo)
            try:
                texto = conteudo.decode("utf-8")
            except UnicodeDecodeError:
                texto = conteudo.decode("cp1252", errors="replace")

            for linha in texto.splitlines():
                if not linha.strip():
                    continue

                campos = [campo.strip() for campo in linha.split("!")]
                campos = campos[:5] + ["!".join(campos[5:])]
                campos.extend([""] * (6 - len(campos)))
                registros.append(campos[:6])

    df_cfm = pd.DataFrame(registros, columns=COLUNAS_CFM)
    df_cfm["CRM"] = (
        df_cfm["CRM"].astype(str).str.replace(r"\D", "", regex=True).str.lstrip("0")
    )
    df_cfm["UF"] = df_cfm["UF"].astype(str).str.strip().str.upper()
    df_cfm["Nome"] = df_cfm["Nome"].astype(str).str.strip().str.upper()
    df_cfm["Especialidade"] = df_cfm["Especialidade"].fillna("").astype(str).str.strip()

    return df_cfm.groupby(["CRM", "UF"], as_index=False).agg({
        "Nome": "first",
        "Tipo_Inscricao": "first",
        "Situacao_Inscricao": "first",
        "Especialidade": juntar_especialidades,
    })


def aplicar_regras(resultado):
    nome_vazio = resultado["Nome"].isna() | (resultado["Nome"].str.strip() == "")

    resultado["Status"] = np.where(
        nome_vazio,
        "Não encontrado",
        "Encontrado",
    )

    print("Aplicando classificação de risco...")
    resultado["Classificacao_Risco"] = resultado.apply(classificar_risco, axis=1)

    print("Aplicando alertas de inscrição...")
    resultado["Alerta_Inscricao"] = resultado.apply(verificar_alerta_inscricao, axis=1)

    print("Verificando especialidades...")
    resultado["Status_Especialidade"] = resultado.apply(verificar_especialidade, axis=1)

    return resultado


def main():
    print("================== Comparador CRM =================\n")

    try:
        arquivo_zip = encontrar_arquivo(PASTA_CFM_ZIP, ".zip", "ZIP")
        arquivo_excel = encontrar_arquivo(PASTA_EMPRESA, ".xlsx", "Excel")
    except (FileNotFoundError, ValueError) as erro:
        print(f"ERRO: {erro}")
        return 1

    print(f"Base do CFM: {arquivo_zip.name}")
    print(f"Planilha da empresa: {arquivo_excel.name}\n")

    print("Carregando base do CFM...")
    df_cfm = ler_cfm(arquivo_zip)

    print("\nCarregando e tratando planilha da empresa...")
    df_empresa = pd.read_excel(arquivo_excel)
    df_empresa.columns = df_empresa.columns.astype(str).str.strip()
    df_empresa = padronizar_dados_empresa(df_empresa)

    colunas_obrigatorias = {"CRM", "UF"}
    if not colunas_obrigatorias.issubset(df_empresa.columns):
        raise ValueError("A planilha da empresa precisa ter as colunas CRM e UF.")

    print("Realizando cruzamento e aplicando regras...")
    resultado = df_empresa.merge(df_cfm, on=["CRM", "UF"], how="left")
    resultado = aplicar_regras(resultado)

    PASTA_RESULTADO.mkdir(parents=True, exist_ok=True)
    arquivo_saida = PASTA_RESULTADO / "medicos_verificados.xlsx"

    try:
        resultado.to_excel(arquivo_saida, index=False)
    except PermissionError:
        print("ERRO: Feche o arquivo medicos_verificados.xlsx e tente novamente.")
        return 1

    print(f"\nProcesso concluído com sucesso! Arquivo gerado em:\n   {arquivo_saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())