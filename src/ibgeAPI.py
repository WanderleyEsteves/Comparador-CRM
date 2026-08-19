import requests

URL_API_IBGE = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"

def obter_mapeamento_uf():
    codigo_para_sigla = {}
    sigla_para_codigo = {}

    try:

        response = requests.get(URL_API_IBGE, timeout=5)
        response.raise_for_status()
        dados = response.json()

        for estado in dados:
            codigo = str(estado["id"])

            sigla = estado["sigla"].upper()

            codigo_para_sigla[codigo] = sigla

            sigla_para_codigo[sigla] = codigo

    except Exception as e:
        print(f"Aviso: Não foi possível conectar à API do IBGE ({e}). Usando mapa estático de fallback.")
        
        codigo_para_sigla = {
            "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO",
            "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL",
            "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR",
            "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"
        }
        sigla_para_codigo = {sigla: cod for cod, sigla in codigo_para_sigla.items()}

    return codigo_para_sigla, sigla_para_codigo


def converter_para_sigla_uf(valor_uf, mapa_codigo_sigla):
    if pd_isna(valor_uf):
        return None
    texto_uf = str(valor_uf).strip().split(".")[0].upper()

    if texto_uf in mapa_codigo_sigla:
        return mapa_codigo_sigla[texto_uf]

    return texto_uf


def pd_isna(val):
    return val is None or val == "" or str(val).lower() in ["nan", "none", "<na>"]