import os
import zipfile
import pandas as pd

def processar_zip_cfm_para_csv(caminho_zip, pasta_destino, nome_arquivo_csv="base_completa_cfm.csv"):

    if not os.path.exists(caminho_zip):
        print(f"ERRO: Arquivo não encontrado em:\n   {caminho_zip}")
        return

    os.makedirs(pasta_destino, exist_ok=True)
    caminho_csv_final = os.path.join(pasta_destino, nome_arquivo_csv)
    colunas = ["CRM", "UF", "Nome", "Tipo_Inscricao", "Situacao_Inscricao", "Especialidade"]
    
    registros_totais = []
    
    print(f"Lendo o arquivo ZIP: {caminho_zip}...")
    
    with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
        for item in zip_ref.namelist():
            
            if item.lower().endswith('.txt') and not item.startswith('__MACOSX'):
                nome_simples = os.path.basename(item)
                print(f"  -> Lendo estado: {nome_simples}")
                
                with zip_ref.open(item) as file:
                    conteudo_bytes = file.read()
                    
                    try:
                        texto = conteudo_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        texto = conteudo_bytes.decode('cp1252', errors='replace')
                    
                    linhas = texto.splitlines()
                    for linha in linhas:
                        if not linha.strip():
                            continue
                        partes = linha.split('!')
                        
                        if len(partes) < 6:
                            partes.extend([""] * (6 - len(partes)))
                        elif len(partes) > 6:
                            partes = partes[:5] + ["!".join(partes[5:])]
                            
                        registros_totais.append(partes[:6])

    if not registros_totais:
        print("Nenhum registro foi encontrado nos arquivos .TXT do ZIP.")
        return

    print("\nCriando DataFrame consolidado...")
    df_consolidado = pd.DataFrame(registros_totais, columns=colunas)
    
    print(f"Salvando CSV em:\n   {caminho_csv_final}")
    df_consolidado.to_csv(caminho_csv_final, sep=';', index=False, encoding='utf-8-sig')
    
    print(f"\nConcluído com sucesso! Total de registros: {len(df_consolidado):,}")

if __name__ == "__main__":
    diretorio_raiz = os.path.dirname(os.path.abspath(__file__))
    caminho_zip_cfm = os.path.join(diretorio_raiz, "dados", "cfm_zip", "TOTAL.zip")
    pasta_saida = os.path.join(diretorio_raiz, "cfm completo csv")
    
    processar_zip_cfm_para_csv(caminho_zip_cfm, pasta_saida)