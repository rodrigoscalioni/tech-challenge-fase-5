# Fase 5 · Marco 1 — Fundação de Dados

**Status:** contrato de dados v0.1 para validação.  
**Fonte de registros individuais:** `BASE DE DADOS PEDE 2024 - DATATHON.xlsx`, com abas `PEDE2022`, `PEDE2023` e `PEDE2024`.  
**Demais arquivos:** referências metodológicas e contextuais, não novas fontes de registros individuais.

## 1. Decisão de modelagem

A tabela principal terá granularidade **aluno-ano**, chave composta `(RA, ano)`. O mesmo RA pode existir em anos diferentes; isso é esperado e necessário para a análise longitudinal. A ingestão deve preservar o valor original de cada célula e o ano de origem.

| Fonte | Registros | Colunas | RAs únicos | INDE numérico | INDE sem valor numérico |
|---|---:|---:|---:|---:|---:|
| PEDE2022 | 860 | 42 | 860 | 860 | 0 |
| PEDE2023 | 1.014 | 48 | 1.014 | 931 | 83 |
| PEDE2024 | 1.156 | 50 | 1.156 | 1.054 | 102 |
| **Total de observações** | **3.030** | — | — | **2.845** | **185** |

### Sobreposição de RAs

- 2022–2023: **600** estudantes.
- 2023–2024: **765** estudantes.
- 2022–2024: **472** estudantes.
- Presentes nos três anos: **468** estudantes.

Os nomes anonimizados coincidem em todos os RAs compartilhados, **mas são derivados do próprio número do RA** (ex.: `RA-1` → `Aluno-1`). Logo, a igualdade do nome não é uma prova independente de identidade. Devemos utilizar o RA como hipótese de vínculo, com sinalização de inconsistências de idade, gênero e ano de ingresso.

## 2. Achados de qualidade prioritários

**INDE de 2023:** 82 ocorrências de `#N/A` e 1 de `#DIV/0!`. Elas se concentram em Fase 8 (63), Fase 7 (13), Fase 4 (6) e Fase 2 (1).

**INDE de 2024:** 63 ocorrências de `#DIV/0!`, 1 de `#N/A` e 38 de `INCLUIR`. Todos os 102 casos estão nos grupos Fase 8 (64) e código 9 (38); **os 1.054 alunos de Alfa a Fase 7 têm INDE numérico**. Nunca computar esses 102 casos como nota zero nem como baixo desempenho.

**Históricos replicados em 2024:** o número `75` funciona como marcador em vários campos de 2022/2023 e em campos correntes como IAA e notas. Na planilha 2024, aparece 684 vezes em `INDE 22`, 391 em `INDE 23`, 102 em `IAA`, 105 em `Mat`, 106 em `Por` e 682 em `Ing`. Ele não é nota `7,5` e não pode entrar no cálculo de média. Para análises anuais, priorizar o campo da **aba correspondente ao ano**, e não a cópia histórica em outra aba.

**Ponto de virada:** `Atingiu PV` contém 113 “Sim” e 747 “Não” em 2022. Em 2023 e 2024 está integralmente vazio. O `IPV` numérico é outro indicador; não substituir a ausência do booleano por uma regra inventada.

**IPP:** coluna numérica inexistente em 2022; presente em 2023/2024. Isso limita a comparação histórica do IPP e a reconstrução independente do INDE em 2022.

**Cabeçalhos:** 2023 tem duas colunas nomeadas `Destaque IPV`; 2024 tem duas `Ativo/ Inativo`. Conservar ambas com seus índices originais na Bronze e evitar sobrescrever uma pela outra.

**Fase 2024:** em 960 registros, o conteúdo de `Fase` coincide com `Turma`; os 196 restantes são Alfa. Para as demais fases, a primeira posição traz um nível numérico, mas o código `9` é um grupo particular com 38 registros `INCLUIR`. Não presumir que código 9 equivale à Fase 8 sem confirmação metodológica.

**Consistência longitudinal:** 199 dos 765 RAs comuns entre 2023 e 2024 divergem em `Ano ingresso`; nenhum muda o nome anonimizado. Há ainda 21 casos com aumento da idade de 2 ou 3 anos entre 2023 e 2024 (pode envolver erros ou diferentes critérios de referência); registrar flags. Entre 2022 e 2023 há 12 diferenças de gênero após a padronização textual. Essas divergências precisam ficar auditáveis.

## 3. Contrato lógico da Silver

Uma linha por `(ra, ano)` com colunas recomendadas:

| Bloco | Campos recomendados | Observação |
|---|---|---|
| Identificação | `ra`, `ano`, `nome_anonimizado` | Não publicar resultados individuais |
| Trajetória | `fase_original`, `fase_padronizada`, `turma_original`, `idade`, `ano_ingresso_reportado` | Preserve origem e flag de consistência |
| Ensino | `tipo_instituicao`, `fase_ideal`, `defasagem` | Defasagem negativa = aluno abaixo do nível ideal |
| Indicadores | `inde`, `ian`, `ida`, `ieg`, `iaa`, `ips`, `ipp`, `ipv` | Valores numéricos validados por ano e disponibilidade |
| Complementos | `nota_matematica`, `nota_portugues`, `nota_ingles`, `pedra`, `atingiu_ponto_virada` | Ausência não equivale a zero |
| Rastreabilidade | `arquivo_origem`, `aba_origem`, `linha_origem`, `data_processamento` | Reproduzir resultados |
| Qualidade | `flag_inde_invalido`, `flag_sentinel`, `flag_fase_desconhecida`, `flag_ingresso_inconsistente`, `flag_idade_inconsistente` | Registradas sem corrigir silenciosamente |

Campos de recomendações psicológicas, escolas nominais e textos livres devem permanecer em área restrita e **fora do espaço Genie gerencial** no MVP.

## 4. Semântica dos indicadores

| Métrica | Definição | Principal cuidado |
|---|---|---|
| IAN | Adequação da fase atual à fase ideal | D = fase efetiva − fase ideal; negativo indica defasagem |
| IDA | Desempenho acadêmico | As notas de inglês não estão disponíveis para todas as fases; não recalcular IDA como média simples de três matérias sem validação |
| IEG | Engajamento nas atividades | Não presumir comparabilidade perfeita entre critérios de coleta anuais |
| IAA | Autoavaliação do estudante | Em 2024 há valores 10,002 e marcadores 75; preservar e sinalizar |
| IPS | Aspectos psicossociais | Indicador sensível e avaliativo; interpretações agregadas e cautelosas |
| IPP | Aspectos psicopedagógicos | Sem coluna equivalente em 2022 |
| IPV | Indicador numérico de ponto de virada | Diferente do evento `Atingiu PV` |
| INDE | Índice ponderado dos sete indicadores, dependente da fase | Usar o INDE oficial do ano; a fórmula histórica deve ser testada antes de recálculo |
| Pedra | Faixa/conceito de desempenho | Preservar classificação original, pois limites/regras podem mudar |

**Ponderação metodológica histórica (referência, sujeita à validação por ano):**

- Fases Alfa–7: `INDE = 0,1*IAN + 0,2*IDA + 0,2*IEG + 0,1*IAA + 0,1*IPS + 0,1*IPP + 0,2*IPV`.
- Fase 8: `INDE = 0,1*IAN + 0,4*IDA + 0,2*IEG + 0,1*IAA + 0,2*IPS`.

Essas fórmulas vêm da metodologia PEDE e **não autorizam automaticamente reprocessar os registros de 2023/2024**: antes é preciso conferir se parâmetros e instrumentos de avaliação foram mantidos. Na base recebida, a Fase 8 não possui INDE numérico em 2023/2024.

## 5. Regras de tratamento aprováveis

1. Preservar Bronze por aba sem perda de linha/coluna, com nome original de cada campo e posição quando houver cabeçalhos duplicados.
2. Normalizar a fase 2022 (`0..7`) e 2023 (`ALFA`, `FASE 1..8`); em 2024 obter fase 1..8 dos códigos de turma e manter `9` em categoria especial pendente. Nunca mapear `9 → 8` sem respaldo.
3. Converter `#N/A`, `#DIV/0!`, `INCLUIR` e sentinelas de escala fora do domínio (como `75`) em **nulos analíticos**, mantendo valor bruto e motivo.
4. Converter `Agata` e `Ágata` a uma grafia comum na Silver, sem recalcular a pedra a partir do INDE.
5. Harmonizar `Menina/Menino` com `Feminino/Masculino`; marcar divergências entre anos como problema de identidade.
6. Nunca usar `0` como substituição para dados ausentes. Um zero presente na origem será inicialmente preservado e avaliado conforme a regra do indicador.
7. Não descartar automaticamente `10,002`/`10,01`; preservar valores, sinalizar excesso da escala e definir com a metodologia se há tolerância de arredondamento.
8. Para indicador médio, explicitar sempre `N_alunos_validos` e `N_registros_sem_dado`; não usar denominador com registros inválidos.
9. Separar visão anual (todos os avaliados em cada ano) da visão longitudinal (RAs comuns entre anos).
10. Não inferir causalidade nem rotular indivíduos como “alto risco” automaticamente; análises de priorização devem orientar revisão humana.

## 6. Critérios de aceite do primeiro pipeline

- [ ] Bronze tem exatamente 860, 1.014 e 1.156 linhas por ano, respectivamente.
- [ ] `(RA, ano)` é único na Silver; não há `RA` nulo.
- [ ] `INDE` corrente possui 860, 931 e 1.054 registros numéricos validados por ano.
- [ ] Os 102 registros sem INDE corrente de 2024 são preservados com flag e não influenciam a média.
- [ ] A validação longitudinal encontra 468 RAs com registros nos três anos.
- [ ] A Gold computa médias sem converter `75` em nota; `N` observado acompanha cada resultado.
- [ ] Os campos e relatórios de psicologia individuais não são expostos à interface conversacional.
- [ ] Todos os valores derivados têm origem, lógica e teste documentados.

## 7. Próximas três entregas técnicas

**01 — Ingestão Bronze:** exportar as três abas para arquivos de ingestão versionados no código, preservar a origem, carregar no Databricks e conferir contagens.

**02 — Tratamento Silver:** aplicar mapeamento de campos, flags e reconciliações com a regra “não corrigir silenciosamente”; testar chaves e tipos.

**03 — Primeiras views Gold:** criar indicadores de defasagem (IAN), desempenho (IDA) e evolução longitudinal por coortes; comparar resultados SQL com cálculos reproduzíveis.

**Decisões em aberto antes da Silver definitiva:** significado do código 9, tratamento da Fase 8 e critérios específicos para a escala dos indicadores. Esses pontos não impedem a Bronze e uma primeira Silver controlada.

## 8. Referências de negócio

- Enunciado `[DTAT] - Datathon - Fase 5.pdf`, páginas 3–9 (requisitos, perguntas e entregáveis).
- `Dicionário Dados Datathon.pdf` (conceitos e histórico PEDE).
- `PEDE_ Pontos importantes.docx` (fórmulas de defasagem e composição do INDE).
- `Relatório PEDE2022.pdf`, `Relatório PEDE2021.pdf` e `Relatório PEDE2020.pdf` (metodologia e comparações históricas).
- `relatorio_de_atividades_2022_passosmagicos_compressed.pdf`, páginas 11–13 (retorno presencial e progressão por fases).
- `relatorio_de_atividades_passosmagicos_2023_compressed.pdf`, páginas 7, 13–16 (metodologia, expansão e indicadores).
- `Relatorio_atividades_2020.pdf` e `Relatorio-de-Atividades-2021-4_compressed.pdf` (contexto histórico, pandemia e modalidades de ensino).

**Nota:** os relatórios de atividades podem incluir beneficiários, inscritos e participantes fora do escopo estrito da pesquisa PEDE, portanto não devem ser usados para forçar a reconciliação das contagens do Excel.