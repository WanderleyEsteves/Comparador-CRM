# CFM Doctor Batch Reconciler & Compliance Engine 🩺📊

Pipeline de processamento em lote (ETL) e reconciliação de dados cadastrais desenvolvido em **Python**. O sistema realiza o parsing, a normalização e o cruzamento automatizado de bases médicas internas contra a base de dados pública do **Conselho Federal de Medicina (CFM)**, aplicando regras de conformidade e auditoria de risco legal.

---

## 📌 Contexto & Especificação Técnica

O Conselho Federal de Medicina disponibiliza periodicamente o arquivo **`TOTAL.ZIP`** para instituições conveniadas, em conformidade com a **Resolução CFM nº 2.309/2022**.

### 📄 Padrão do Arquivo Fonte (CFM):

* **Estrutura do Pacote:** Arquivo compactado contendo 27 arquivos de texto (`AC.txt`, `SP.txt`, `RJ.txt`...), um para cada Unidade Federativa.
* **Layout:** Sem linha de cabeçalho, com registros delimitados pelo caractere `!`.
* **Codificação e Fim de Linha:** Codificado estritamente em `UTF-8` com terminação `CRLF (\r\n)`.
* **Esquema de Colunas (6 campos fixos):**
  1. `CRM` (Número de inscrição no Conselho Regional)
  2. `UF` (Sigla da Unidade Federativa)
  3. `Nome` (Nome do profissional em caixa alta)
  4. `Tipo de Inscrição` (*Principal*, *Secundária*, *Provisória*, *Estud.Méd.Estrangeiro*...)
  5. `Situação da Inscrição` (*Ativo*, *Cassado*, *Cancelado*, *Suspenso*, *Falecido*...)
  6. `Especialidade` (Especialidades e áreas de atuação com seus respectivos números de RQE).

---

## 🚀 Arquitetura & Fluxo de Processamento

O pipeline opera em um fluxo linear de 5 etapas:

1. **Ingestão dos Arquivos:**
   `TOTAL.zip (CFM)` -> Leitura direta dos 27 `.txt` em memória (UTF-8 / fallback CP1252) -> Extração dos registros delimitados por `!`.

2. **Sanitização da Base do CFM:**
   Registros brutos -> Limpeza de espaços (`strip`) -> Padronização de CRM (`lstrip("0")`) -> Agrupamento de especialidades/RQEs por CRM + UF (evita duplicatas).

3. **Padronização da Planilha Interna:**
   `medicos.xlsx` -> Extração numérica do CRM -> Consulta à API do IBGE (ou fallback local) para converter códigos de estado em siglas UF (`35` -> `SP`).

4. **Cruzamento & Regras de Compliance (Join CRM + UF):**
   Bases unificadas -> Classificação de Status (`Encontrado` / `Não encontrado`) -> Aplicação da Matriz de Risco:
   * **Risco Legal:** Cassado, Suspenso, Interdição Cautelar, Inscrição Anulada.
   * **Cadastro Desatualizado:** Falecido, Aposentado, Transferido, Inoperante.
   * **Regular:** Ativo.
   * **Alertas de Tipo:** Principal, Secundária, Provisória, Licença Estrangeira.
   * **Qualificação:** Especialista Registrado com RQE vs. Clínico Geral (sem RQE).

5. **Exportação do Relatório:**
   Dados auditados -> Consolidação em DataFrame -> `dados/resultado/medicos_verificados.xlsx`.
---

## 📁 Estrutura de Diretórios

   ```text
CRM_VALIDADOR/
├── dados/
│   ├── cfm_zip/            # Diretório de entrada do TOTAL.zip do CFM
│   ├── empresa/            # Diretório com a planilha interna (.xlsx)
│   └── resultado/          # Planilha consolidada de saída
├── src/
│   ├── __init__.py
│   ├── ibgeAPI.py          # Módulo de integração com a API do IBGE
│   ├── normalizador.py     # Sanitização e padronização de chaves (CRM/UF)
│   └── status_compliance.py # Regras de negócio e matriz de risco
├── comparadorCRM.py        # Orquestrador do pipeline de dados
├── gerador.py              # Script para geração de dados sintéticos de teste
├── requirements.txt        # Dependências do projeto
└── README.md
```

---

## ⚙️ Como Executar

python gerador.py
Isso criará um TOTAL.zip com layouts reais do CFM e uma base de médicos de exemplo com múltiplos cenários de teste.

python comparadorCRM.py
O relatório final auditado será gerado em dados/resultado/medicos_verificados.xlsx.

---

## 🏛️ Referências Oficiais e Legislação

Este projeto foi construído estritamente de acordo com as especificações públicas.

* **Portal de Informações do CFM:** [CFM — Listagem de Médicos](https://sistemas.cfm.org.br/listamedicos/informacoes)
* **API de Localidades (IBGE):** [IBGE Serviços — API de Estados](https://servicodados.ibge.gov.br/api/docs/localidades)

> **Nota sobre Dados e Privacidade:** O repositório contém apenas o código-fonte da ferramenta de processamento. Nenhum dado cadastral real de profissionais ou dados proprietários de empresas estão armazenados ou disponibilizados neste repositório, utilizando exclusivamente bases sintéticas/mockadas para testes de software.

---

## 🔒 Dados e Conformidade (LGPD)
Todos os dados, nomes e identificadores utilizados nos scripts de teste e demonstração neste repositório são 100% fictícios e sintéticos, elaborados exclusivamente para validação de lógica computacional e demonstração de engenharia de software, sem vínculo com cadastros médicos reais.

---

## ⚖️ Aviso Legal (Disclaimer)

* **Sem Vínculo Institucional:** Este projeto é uma ferramenta independente de processamento de dados e **não possui qualquer vínculo, afiliação, endosso ou ligação oficial** com o Conselho Federal de Medicina (CFM), Conselhos Regionais (CRMs) ou com o Instituto Brasileiro de Geografia e Estatística (IBGE).
* **Finalidade:** O código foi desenvolvido exclusivamente para fins de estudo, demonstração de engenharia de dados e automação de processos baseados em layouts públicos.
* **Marcas e Direitos:** Todos os nomes institucionais, siglas e termos normativos citados pertencem aos seus respectivos titulares e são utilizados estritamente como referência técnica de compatibilidade.