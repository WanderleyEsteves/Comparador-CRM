import pandas as pd
from .ibgeAPI import obter_mapeamento_uf, converter_para_sigla_uf

def padronizar_dados_empresa(df_empresa):
    df = df_empresa.copy()
    
    codigo_para_sigla, _ = obter_mapeamento_uf()
    
    if "CRM" in df.columns:
        # 1 Pega apenas a parte antes do ponto (caso tenha vindo float ex: 12345.0)
        # 2 Exclui os dígitos
        # 3 Remove zeros à esquerda para uniformizar
        df["CRM"] = (
            df["CRM"]
            .astype(str)
            .str.split(".").str[0]
            .str.replace(r"\D", "", regex=True)
            .str.lstrip("0")
            .str.strip()
        )
        
    if "UF" in df.columns:
        df["UF"] = df["UF"].apply(lambda val: converter_para_sigla_uf(val, codigo_para_sigla))
    else:
        print("Alerta: Coluna 'UF' não encontrada na planilha da empresa!")
        
    return df