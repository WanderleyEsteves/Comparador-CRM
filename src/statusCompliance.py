import pandas as pd


def classificar_risco(linha):
    
    nome = linha.get("Nome")
    situacao = str(linha.get("Situacao_Inscricao", "")).strip()

    if pd.isna(nome) or nome == "":
        return "CRM Não Encontrado"

    situacoes_bloqueadas = [
        "Cassado",
        "Cancelado",
        "Inscrição anulada",
        "Suspenso - total",
        "Suspenso por ordem judicial - total",
        "Suspensão total temporária",
        "Interdição cautelar - total",
        "Suspenso - parcial",
        "Suspenso por ordem judicial - parcial",
        "Suspensão parcial permanente",
        "Interdição cautelar - parcial",
        "Suspenso",
        "Afastado",
        "Interditado cautelarmente",
        "Interditado parcialmente",
        "Suspenso por ordem judicial",
    ]
    if situacao in situacoes_bloqueadas:
        return "Risco Legal (Inscrição Irregular)"

    situacoes_inativas = [
        "Falecido",
        "Aposentado",
        "Transferido",
        "Inoperante",
        "Sem o exercício da profissão na UF",
    ]
    if situacao in situacoes_inativas:
        return "Cadastro Desatualizado"

    if situacao == "Ativo":
        return "Regular"

    return "Outro"


def verificar_alerta_inscricao(linha):
    
    nome = linha.get("Nome")
    tipo_inscricao = str(linha.get("Tipo_Inscricao", "")).strip().title()

    if pd.isna(nome) or nome == "":
        return "Não Aplicável"

    if "Secundária" in tipo_inscricao or "Secundaria" in tipo_inscricao:
        return "Atenção: Inscrição Secundária"
    elif "Provisória" in tipo_inscricao or "Provisoria" in tipo_inscricao:
        return "Atenção: Inscrição Provisória"
    elif "Estrangeiro" in tipo_inscricao:
        return "Atenção: Licença Estrangeira"
    elif "Principal" in tipo_inscricao or "Primária" in tipo_inscricao:
        return "Regular (Inscrição Principal)"

    return "Outro"


def verificar_especialidade(linha):
    
    nome = linha.get("Nome")
    especialidade = linha.get("Especialidade")

    if pd.isna(nome) or nome == "":
        return "Não Aplicável"

    if pd.isna(especialidade) or str(especialidade).strip() == "":
        return "Sem RQE Registrado (Clínico Geral)"

    return "Especialista Registrado"