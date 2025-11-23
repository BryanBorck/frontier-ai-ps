# CVM Funds Data Structure

This document describes the structure of the investment funds data available at [https://dados.cvm.gov.br/dados/FI/](https://dados.cvm.gov.br/dados/FI/).

The data is organized into the following directories, each containing specific datasets about Brazilian Investment Funds.

## 1. /FI/CAD/ (Registration Data)

Contains registration information for investment funds (active and cancelled).

**File:** `meta_cad_fi.txt`

| Field              | Description                                                           | Type         |
| ------------------ | --------------------------------------------------------------------- | ------------ |
| ADMIN              | Nome do Administrador                                                 | varchar(100) |
| AUDITOR            | Nome do Auditor                                                       | varchar(100) |
| CD_CVM             | Código CVM                                                            | numeric(7)   |
| CLASSE             | Classe                                                                | varchar(100) |
| CLASSE_ANBIMA      | Classificação de Fundos regulados ANBIMA                              | varchar(100) |
| CNPJ_ADMIN         | CNPJ do Administrador                                                 | varchar(20)  |
| CNPJ_AUDITOR       | CNPJ do Auditor                                                       | varchar(20)  |
| CNPJ_CONTROLADOR   | CNPJ do Controlador                                                   | varchar(20)  |
| CNPJ_CUSTODIANTE   | CNPJ do Custodiante                                                   | varchar(20)  |
| CNPJ_FUNDO         | CNPJ do fundo                                                         | varchar(20)  |
| CONDOM             | Forma de condomínio                                                   | varchar(100) |
| CONTROLADOR        | Nome do Controlador                                                   | varchar(100) |
| CPF_CNPJ_GESTOR    | Informa o código de identificação do gestor pessoa física ou jurídica | varchar(20)  |
| CUSTODIANTE        | Nome do Custodiante                                                   | varchar(100) |
| DENOM_SOCIAL       | Denominação Social                                                    | varchar(100) |
| DIRETOR            | Nome do Diretor Responsável                                           | varchar(100) |
| DT_CANCEL          | Data de cancelamento                                                  | date         |
| DT_CONST           | Data de constituição                                                  | date         |
| DT_FIM_EXERC       | Data fim do exercício social                                          | date         |
| DT_INI_ATIV        | Data de início de atividade                                           | date         |
| DT_INI_CLASSE      | Data de início na classe                                              | date         |
| DT_INI_EXERC       | Data início do exercício social                                       | date         |
| DT_INI_SIT         | Data início da situação                                               | date         |
| DT_PATRIM_LIQ      | Data do patrimônio líquido                                            | date         |
| DT_REG             | Data de registro                                                      | date         |
| ENTID_INVEST       | Indica se o fundo é entidade de investimento                          | varchar(1)   |
| FUNDO_COTAS        | Indica se é fundo de cotas                                            | varchar(1)   |
| FUNDO_EXCLUSIVO    | Indica se é fundo exclusivo                                           | varchar(1)   |
| GESTOR             | Nome do Gestor                                                        | varchar(100) |
| INF_TAXA_ADM       | Informações Adicionais (Taxa de administração)                        | varchar(400) |
| INF_TAXA_PERFM     | Informações Adicionais (Taxa de performance)                          | varchar(400) |
| INVEST_CEMPR_EXTER | Indica se o fundo pode aplicar 100% dos recursos no exterior          | varchar(1)   |
| PF_PJ_GESTOR       | Indica se o gestor é pessoa física ou jurídica                        | char(2)      |
| PUBLICO_ALVO       | Público-alvo                                                          | varchar(15)  |
| RENTAB_FUNDO       | Forma de rentabilidade do fundo (indicador de desempenho)             | varchar(100) |
| SIT                | Situação                                                              | varchar(100) |
| TAXA_ADM           | Taxa de administração                                                 | real         |
| TAXA_PERFM         | Taxa de performance                                                   | real         |
| TP_FUNDO           | Tipo de fundo                                                         | varchar(20)  |
| TRIB_LPRAZO        | Indica se possui tributação de longo prazo                            | varchar(3)   |
| VL_PATRIM_LIQ      | Valor do patrimônio líquido                                           | numeric      |

---

## 2. /FI/DOC/BALANCETE/ (Balance Sheet)

Contains monthly balance sheet data.

**File:** `meta_balancete_fi.txt`

| Field              | Description                           | Type        |
| ------------------ | ------------------------------------- | ----------- |
| CD_CONTA_BALCTE    | Código da conta                       | char(8)     |
| CNPJ_FUNDO_CLASSE  | CNPJ do fundo/classe                  | varchar(20) |
| DT_COMPTC          | Data de competência do documento      | date        |
| PLANO_CONTA_BALCTE | Plano contábil utilizado no balancete | varchar(5)  |
| TP_FUNDO_CLASSE    | Tipo de fundo/classe                  | varchar(20) |
| VL_SALDO_BALCTE    | Saldo da conta                        | numeric     |

---

## 3. /FI/DOC/CDA/ (Portfolio Composition - CDA)

Contains detailed portfolio composition (Carteira de Diversificação de Aplicações).

**Files:** `meta_cda_fi_*.txt`

### Common Fields (Across multiple files)

| Field             | Description                             | Type          |
| ----------------- | --------------------------------------- | ------------- |
| CNPJ_FUNDO_CLASSE | CNPJ do fundo/classe                    | varchar(20)   |
| DENOM_SOCIAL      | Denominação Social                      | varchar(255)  |
| DT_COMPTC         | Data de competência do documento        | date          |
| DT_CONFID_APLIC   | Prazo de confidencialidade da aplicação | date          |
| TP_APLIC          | Tipo de aplicação                       | varchar(8000) |
| TP_FUNDO_CLASSE   | Tipo de fundo/classe                    | varchar(20)   |
| VL_MERC_POS_FINAL | Valor de mercado da posição final       | numeric       |

_(Note: Specific files like `meta*cda_fi_BLC*_.txt`contain breakdown by asset class with specific fields like`EMISSOR`, `QT_POS_FINAL`, etc.)\*

---

## 4. /FI/DOC/COMPL/ (Complementary Info)

Contains complementary information filed by funds.

**Files:** `meta_compl_fi_*.txt`

| Field              | Description                                       | Type         |
| ------------------ | ------------------------------------------------- | ------------ |
| CNPJ_FUNDO         | CNPJ do fundo                                     | varchar(20)  |
| DT_COMPTC          | Data de competência do documento                  | date         |
| TP_FUNDO           | Tipo de fundo                                     | varchar(15)  |
| AG_RISCO           | Nome da agência de classificação de risco         | varchar(100) |
| APRES_ADMIN        | Apresentação do administrador                     | text         |
| APRES_GESTOR       | Apresentação do gestor de recursos                | text         |
| GRAU_RISCO         | Grau de risco atribuído                           | varchar(50)  |
| POLIT_ADM_RISCO    | Política de administração de risco                | text         |
| POLIT_DISTRIB      | Política de distribuição de cotas                 | text         |
| POLIT_VOTO         | Política relativa ao exercício de direito do voto | text         |
| RISCO_CART         | Exposição aos fatores de riscos                   | text         |
| TRIBUT_FUNDO_COTST | Descrição da tributação aplicável                 | text         |

---

## 5. /FI/DOC/EVENTUAL/ (Occasional Reports)

Contains occasional documents/events.

**File:** `meta_eventual_fi.txt`

| Field               | Description                      | Type         |
| ------------------- | -------------------------------- | ------------ |
| CNPJ_FUNDO_CLASSE   | CNPJ do fundo/classe             | varchar(20)  |
| DENOM_SOCIAL        | Denominação Social               | varchar(100) |
| DT_COMPTC           | Data de competência do documento | date         |
| DT_RECEB            | Data da recebimento do documento | date         |
| ID_DOC              | Identificador do documento       | int          |
| LINK_ARQ            | Link para download do arquivo    | varchar(181) |
| NM_ARQ              | Nome do arquivo                  | varchar(100) |
| RESULTADO_AUDITORIA | Resultado da auditoria           | varchar(100) |
| TP_DOC              | Tipo do documento                | varchar(15)  |

---

## 6. /FI/DOC/EXTRATO/ (Extract)

Contains extracts of fund information.

**File:** `meta_extrato_fi.txt`

| Field                | Description                                               | Type         |
| -------------------- | --------------------------------------------------------- | ------------ |
| CNPJ_FUNDO_CLASSE    | CNPJ do fundo/classe                                      | varchar(20)  |
| DENOM_SOCIAL         | Denominação Social                                        | varchar(100) |
| DT_COMPTC            | Data de competência do documento                          | date         |
| APLIC_MIN            | Aplicação mínima                                          | decimal      |
| ATUALIZ_DIARIA_COTA  | Indica se o valor da cota será atualizado diariamente     | varchar(1)   |
| CLASSE_ANBIMA        | Classificação de Fundos regulados ANBIMA                  | varchar(100) |
| CONDOM               | Forma de condomínio                                       | varchar(7)   |
| COTA_PL              | Patrimônio Líquido base para o cálculo do valor da cota   | varchar(53)  |
| EXISTE_TAXA_INGRESSO | Indica se o fundo cobra taxa de ingresso                  | varchar(1)   |
| EXISTE_TAXA_PERFM    | Indica se o fundo cobra taxa de performance               | varchar(1)   |
| EXISTE_TAXA_SAIDA    | Indica se o fundo cobra taxa de saída                     | varchar(1)   |
| INF_TAXA_PERFM       | Informações Adicionais (Taxa de performance)              | varchar(400) |
| INVEST_EXTERIOR      | Indica se o fundo pode realizar investimentos no exterior | varchar(1)   |
| POLIT_INVEST         | Política de investimento                                  | varchar(24)  |
| PUBLICO_ALVO         | Público-alvo                                              | varchar(15)  |
| TAXA_ADM             | Taxa de administração                                     | real         |
| TAXA_PERFM           | Taxa de performance                                       | real         |

---

## 7. /FI/DOC/INF_DIARIO/ (Daily Information)

Contains daily data on net worth, quota value, deposits and withdrawals.

**File:** `meta_inf_diario_fi.txt`

| Field             | Description                      | Type        |
| ----------------- | -------------------------------- | ----------- |
| CNPJ_FUNDO_CLASSE | CNPJ do fundo/classe             | varchar(20) |
| DT_COMPTC         | Data de competência do documento | date        |
| TP_FUNDO_CLASSE   | Tipo de fundo/classe             | varchar(15) |
| VL_QUOTA          | Valor da cota                    | numeric     |
| VL_PATRIM_LIQ     | Valor do patrimônio líquido      | numeric     |
| VL_TOTAL          | Valor total da carteira          | numeric     |
| CAPTC_DIA         | Captação do dia                  | numeric     |
| RESG_DIA          | Resgate no dia                   | numeric     |
| NR_COTST          | Número de cotistas               | int         |

---

## 8. /FI/DOC/LAMINA/ (Fact Sheet - Lâmina)

Contains "Lâmina" information (Key Information Document).

**Files:** `meta_lamina_fi_*.txt`

| Field             | Description                      | Type          |
| ----------------- | -------------------------------- | ------------- |
| CNPJ_FUNDO_CLASSE | CNPJ do fundo/classe             | varchar(20)   |
| DENOM_SOCIAL      | Denominação Social               | varchar(100)  |
| DT_COMPTC         | Data de competência do documento | date          |
| PUBLICO_ALVO      | Público-alvo                     | varchar(100)  |
| OBJETIVO          | Objetivo do fundo                | varchar(4000) |
| POLIT_INVEST      | Política de investimento         | varchar(4000) |
| RISCO_CARTEIRA    | Risco da carteira                | varchar(4000) |
| LIQUIDEZ          | Liquidez                         | varchar(4000) |
| PR_RENTAB_MES     | Rentabilidade no mês             | numeric       |
| PR_RENTAB_ANO     | Rentabilidade no ano             | numeric       |

---

## 9. /FI/DOC/PERFIL_MENSAL/ (Monthly Profile)

Contains monthly profile information detailing risk factors, shareholder profile, etc.

**File:** `meta_perfil_mensal_fi.txt`

| Field               | Description                                               | Type         |
| ------------------- | --------------------------------------------------------- | ------------ |
| CNPJ_FUNDO_CLASSE   | CNPJ do fundo/classe                                      | varchar(20)  |
| DENOM_SOCIAL        | Denominação Social                                        | varchar(100) |
| DT_COMPTC           | Data de competência do documento                          | date         |
| ATIVO_CRED_PRIV     | Indica se o regulamento permite ativos de crédito privado | varchar(1)   |
| CENARIO*FPR*\*      | Cenários de Fatores Primitivos de Risco                   | varchar(150) |
| COMITENTE*LIGADO*\* | Indica se comitente é parte relacionada                   | char(1)      |
| FPR                 | Fator primitivo de risco                                  | varchar(50)  |
| NR*COTST*\*         | Número de cotistas por tipo (Banco, Varejo, etc.)         | int          |
| PR_ATIVO_CRED_PRIV  | % de ativos de crédito privado                            | numeric      |
| PR_VAR_CARTEIRA     | VAR da carteira                                           | numeric      |
| ST_LIQDEZ           | Indica liquidez                                           | varchar(1)   |
