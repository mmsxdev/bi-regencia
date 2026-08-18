# GUIA DE APRESENTAÇÃO — BI DE REGÊNCIA (Frequência dos Instrutores)

> Material para apresentar o painel à diretora da unidade e às equipes do SENAI.
> Ele explica **o que é o painel**, **como ler cada gráfico** e **o que os dados reais de 2026 já mostram** — com números, roteiro de fala e mensagens-chave.

---

## 1. O que é o BI de Regência (visão geral)

O painel é um **relatório interativo da frequência dos instrutores do quadro** em sala de aula.
Ele responde a perguntas como:

- Quantas **horas-aula** cada instrutor realizou? E por mês?
- Que **% da carga prevista** cada um está cumprindo? (a chamada **frequência**)
- Quais **áreas** concentram os instrutores com menor atividade?
- Como está a evolução ao longo do **ano**? Onde estão os picos e as quedas?

**Fonte de dados:** a aba `CONSOLIDADO ` da planilha de regência
(`REGÊNCIA - INSTRUTORES DO QUADRO 2026.xlsx`). É a mesma planilha que a coordenação já preenche,
não é uma planilha nova — o painel apenas **lê e organiza** os lançamentos mensais.

**Atualização:** automática (a cada 10 minutos no padrão), com botão "Atualizar dados agora" na
barra lateral. Ou seja, se a coordenação salvar a planilha no SharePoint/OneDrive, o painel passa a
mostrar os números novos sozinho.

---

## 2. Entendendo a fonte de dados (para explicar com segurança)

Na planilha, **cada linha é um instrutor**. As colunas são:

| Campo | O que significa |
|---|---|
| `DOCENTE` | Nome do instrutor |
| `Ch` | Carga horária semanal prevista (ex.: 40 h) |
| `ÁREA` | Área técnica em que atua |
| `POLO / LOCAL` | Local de regência (ex.: `Vila Canaã`, `Jardim Vila Boa (SEDUC)`). Lido da planilha se a coluna existir; se não, inferido pelo painel |
| `H/AULA` (JAN a DEZ) | **Horas-aula realizadas** naquele mês |
| `%` (JAN a DEZ) | **Frequência** = horas-aula ÷ carga esperada no mês |
| `ANO` | Total de horas no ano |
| `MÉDIA` | Média de frequência no período |
| `EXTRA-QUADRO` | Horas de instrutores extra-quadro |

> **Unificação automática de áreas:** o painel normaliza a área na leitura. Ex.: `Manutenção automotiva
> (JD)` (rótulo interno do polo SEDUC) vira **Manutenção automotiva**; `Contrução Civil` vira
> **Construção Civil**; `Grafica editorial` vira **Gráfica editorial**. Assim a análise não fica
> fragmentada por digitação. No `data_loader.py`, basta acrescentar entradas no dicionário `AREA_NORM`.

> **Termo-chave — "frequência":** no painel, frequência **não é** faltas/atrasos. É a relação entre
> o que o instrutor **efetivamente ministrou** e a **carga de regência esperada** para ele naquele mês.
> - 100% → cumpriu exatamente a carga esperada.
> - Acima de 100% → ministrou **mais** do que a carga prevista (ocorre e é um dado valioso).
> - Abaixo de 50% → zona de **alerta** (vermelho/laranja no painel).

> **Detalhe importante de transparência:** o número de instrutores "em atividade" **cresce ao longo do
> ano** (em janeiro, 37 instrutores com lançamento; em agosto em diante, 45). Isso reflete entradas
> (contratações/retornos) ao longo de 2026 — não é uma falha do painel.

---

## 3. Como ler o painel, seção por seção

### 3.1 Cabeçalho e KPIs (cartões no topo)

Ao abrir o painel há **4 indicadores principais**:

| KPI | Ler como |
|---|---|
| **Instrutores ativos** | Quantos instrutores existem no conjunto filtrado (padrão: 45) |
| **Horas-aula no período** | Soma das horas dos meses selecionados (padrão: todo o ano) |
| **Frequência média** | Média das frequências mensais dos instrutores no período — o indicador de saúde do quadro inteiro |
| **Horas-aula no ano** | Total do quadro usando a coluna `ANO` da planilha |

> **Leitura atual (dados 2026, quadro completo):**
> - 45 instrutores
> - ~37.306 horas-aula no período
> - Frequência média: **61,0%**
> - ~36.457 horas-aula no ano (coluna `ANO`)
>
> Note que existem **dois totais** (37.306 vs 36.457): um soma os meses dentro do painel e o outro vem
> da coluna `ANO` da planilha. A diferença (~850 h, cerca de 2%) é um **indicador de conferência**:
> sugere que alguns lançamentos mensais e o total anual da planilha não estão 100% alinhados. Vale
> combinar com a coordenação de padronizar o cálculo — isso mostra rigor com a informação.

### 3.2 Filtros (barra acima das abas)

- **Instrutor(es):** isola um ou vários nomes.
- **Área:** filtra por área técnica (áreas já unificadas pelo painel).
- **Polo / Local:** filtra pelo local de regência (ex.: `Vila Canaã`, `Jardim Vila Boa (SEDUC)`) — separa
  onde atuam sem fragmentar a área.
- **Meses do período:** escolhe quais meses entram nos cálculos (KPIs e gráficos respondem
  instantaneamente).
- **"Limpar filtros":** volta para o quadro completo.

**Uso na apresentação:** é o recurso que permite "fazer perguntas ao dado" ao vivo —
ex.: *"Vamos ver só a área de Manutenção automotiva"* ou *"Agora só o mês de agosto"*.

### 3.3 Aba "Visão Geral"

1. **Frequência média por instrutor** (barras horizontais):
   uma barra por instrutor, colorida pela própria frequência. A legenda acima (Baixa → Alta)
   ensina a ler as cores. Com o quadro completo, os instrutores de menor frequência aparecem
   primeiro (ordenado do menor para o maior).
2. **Distribuição da frequência média** (histograma):
   quantos instrutores em cada faixa. Mostra, de uma olhada, se o quadro está concentrado em
   faixas boas ou ruins. Hoje: 12 instrutores abaixo de 50%, 15 em 50–70%, 16 em 70–100% e 2 acima de 100%.
3. **Horas-aula por área** (barras horizontais):
   onde o esforço em sala está concentrado. Gráfica editorial e Alimentos e bebidas lideram em
   volume; Manutenção automotiva também tem volume grande (13 instrutores, área já unificada), porém
   com frequência baixa.
4. **Horas-aula por polo** (barras horizontais, abaixo da área):
   mostra o volume por local de regência (`Vila Canaã` × `Jardim Vila Boa (SEDUC)`), sem que isso
   divida a área em grupos artificiais.

### 3.4 Aba "Por Instrutor"

1. **Ranking de horas-aula:** quem mais ministrou horas no período (maior volume de trabalho).
2. **Heatmap instrutor × mês (%):** a "radiografia" do quadro. Cada célula é a frequência de um
   instrutor em um mês, com a mesma escala de cores.
   - **Leitura visual:** colunas escuras/vermelhas = meses fracos; linhas vermelhas = instrutores com
     baixa atividade ao longo do ano. As colunas de **julho e dezembro** ficam visivelmente mais
     fracas (férias/encerramento) — normal. Linhas específicas persistentemente vermelhas são o
     **alvo de gestão**.

### 3.5 Aba "Por Mês"

1. **Horas-aula totais por mês:** volume de atividade mensal do quadro inteiro.
2. **Frequência média por mês (linha):** a evolução do indicador central. Este é o gráfico mais
   fácil de mostrar a sazonalidade.

> **Curva de 2026 (para a apresentação):**
> JAN 41% → FEV 62% → MAR 78% → ABR 73% → MAI 70% → JUN 71% → **JUL 18%** → AGO 82% → SET 78%
> → OUT 64% → NOV 59% → **DEZ 37%**
>
> A leitura natural: **janeiro** (início de ano, entrada/reajuste de contrato), **julho** (férias
> escolares) e **dezembro** (encerramento) são os vales esperados. Março–Setembro concentram o
> período produtivo. É importante **calibrar a meta de frequência levando a sazonalidade em conta** —
> cobrar 80% em julho seria injusto.

### 3.6 Aba "Tabela"

Os dados consolidados na íntegra (carga, área, **polo**, horas e % por mês, totais) com botão
**"Baixar dados em CSV"**. Serve para conferência, auditoria e para gerar relatórios fora do painel.

---

## 4. O que os dados mostram hoje (insights reais de 2026)

> Estes pontos são o coração da apresentação: mostram que o painel **transforma a planilha em
> informação de gestão**.

### 4.1 Panorama do quadro
- **45 instrutores**, frequência média de **61%**, ~37,3 mil horas-aula no ano.
- Mais de **1/4 do quadro (12 instrutores, 27%) está abaixo de 50%** de frequência — zona de alerta.
- Apenas **2 instrutores acima de 100%** (ministram acima da carga prevista).

### 4.2 Onde está a atenção (riscos)
Os 5 menores índices em 2026 são de **Manutenção automotiva / (JD)**:

| Instrutor | Área | Freq. média | Horas no ano |
|---|---|---|---|
| DIOGO DE SOUZA PIMENTEL | Manutenção automotiva | 10,8% | 207 |
| DINAIRON DA SILVA BORGES | Manutenção automotiva | 14,6% | 280 |
| CAIO CEZAR BRAZ E SILVA | Manutenção automotiva | 22,1% | 383 |
| JOÃO VICTOR NEVES NASCIMENTO | Manutenção automotiva | 30,9% | 371 |
| MANOEL DA PACIÊNCIA RAMALHO DE SOUSA | Manutenção automotiva | 34,1% | 655 |

- Na área **Manutenção automotiva** (13 instrutores — inclui o polo "JD", unificado pelo painel),
  **7 estão abaixo de 50%**. Frequência média da área: **~46%** — a mais crítica do quadro.
- Outras áreas com frequência abaixo da média geral: **Administração (~44%)**, **Segurança do
  trabalho (~36%)**.
- **Pergunta para a diretora trocar em gestão:** os instrutores com baixa frequência estão com
  carga reduzida? Afastados parcialmente? Realocação de unidades? O painel não responde o "porquê",
  mas aponta **quem** e **onde** — e é isso que orienta a conversa com a coordenação.

### 4.3 Destaques positivos (espelho para boas práticas)
- **Gráfica editorial** (11 instrutores): maior volume (~9.712 h) e maior frequência média (~75%).
- **Alimentos e bebidas** (6 instrutores): ~73% de frequência, **BRUNA ARIEL DIAS GUARIGLIA**
  com **103,8%** e ~1.495 h no ano.
- **ROMULO FLORIANO LIMEIRA** (Gráfica editorial): **109,5%** — maior frequência do quadro.
- **LEIDINA LAIS** (Manutenção automotiva): **1.552 h** no ano — maior volume do quadro, mesmo
  estando em uma área crítica. Exemplo de que "pessoa certa no lugar certo faz diferença".

### 4.4 Sazonalidade (para calibrar metas)
A queda de **julho (18%)** aparece como o maior vale do ano e coincide com o recesso escolar.
Janeiro (41%) e dezembro (37%) têm comportamento de início/fim de ciclo. **Recomendação:** usar os
meses de março a setembro como referência de "frequência saudável" (78–82%) e definir metas por
período, em vez de uma única meta anual.

### 4.5 Qualidade dos dados (transparência e plano de ação)
- **Nomes de área com erros de digitação:** `Contrução Civil` e `Grafica editorial` **já são corrigidos
  automaticamente** pelo painel (ver 4.6). O ideal é corrigir também na planilha-fonte para manter tudo
  padronizado.
- **1 instrutora sem total anual** (THAUANA MACHADO, coluna `ANO` vazia) apesar de ter horas mensais.
- **Instrutores com meses sem lançamento** (ex.: CHRISTIAN TEILOR com 7 meses, JOÃO VICTOR MARTINS
  com 5) — parte pode ser entrada durante o ano, mas vale conferir se foi falta de preenchimento.
- **Coluna EXTRA-QUADRO zerada** em todo o quadro — provavelmente ainda não é usada.
- **Dois totais distintos** (37.306 h vs 36.457 h): recomendar padrão único de cálculo.

> **Mensagem:** o painel também **aponta falhas de preenchimento**, o que é info de processo —
> ensina a melhorar a planilha-fonte e dá mais credibilidade aos próximos números.

### 4.6 As duas "Manutenção automotiva" — o rótulo (JD) já está resolvido no painel

**O que era:** a planilha tinha `Manutenção automotiva` e `Manutenção automotiva (JD)` como áreas
"diferentes". Isso **não** eram duas áreas técnicas:
- A planilha inteira é da **Escola SENAI Vila Canaã** — inclusive os instrutores "(JD)"
  (BRUNO SILVA OLIVEIRA e WELLINGTON CHAVES PEREIRA, ambos com 40 h).
- A aba `MODELO SEDUC` da própria planilha traz a escola parceira **Col. Est. Jardim Vila Boa** e o curso
  **"Técnico em Manutenção Automotiva - Seduc"** — indicação de que **"JD" = Jardim (Vila Boa)**, o polo
  da escola parceira do programa SEDUC.

> ⚠️ **Transparência:** a sigla "JD" não está explicada em nenhuma célula da planilha — a leitura acima é
> a **interpretação mais provável**. Confirme com a coordenação de regência.

**O que mudou (implementado no painel):**
1. **Área unificada:** o `data_loader.py` normaliza `Manutenção automotiva (JD)` → **Manutenção automotiva**
   (mesma regra também corrige `Contrução Civil` → `Construção Civil` e `Grafica editorial` → `Gráfica editorial`).
2. **Novo campo POLO / LOCAL:** identifica o **local de regência** — `Vila Canaã` (unidade) e
   `Jardim Vila Boa (SEDUC)` (polo da escola parceira).
   - Se a planilha tiver uma coluna `POLO`/`LOCAL` no cabeçalho, o painel **lê dela** (assim a coordenação
     controla os valores).
   - Se a coluna **não existir**, o painel **infere**: rótulo "(JD)" → `Jardim Vila Boa (SEDUC)`; demais → `Vila Canaã`.
3. **Novo filtro "Polo / Local":** permite isolar `Jardim Vila Boa (SEDUC)` sem que a área se fragmente.
4. **Gráfico "Horas-aula por polo"** na aba Visão Geral e coluna **POLO** na aba Tabela/CSV.

**Resultado:** a diretora enxerga **Manutenção automotiva como uma área única** (13 instrutores,
7 abaixo de 50%) e, se quiser, vê separado o que acontece em cada polo.

**Pendência para a coordenação:** preencher a coluna `POLO/LOCAL` na planilha para **todos** os
instrutores (assim o painel passa a usar o valor oficial em vez da inferência).

---

## 5. Roteiro de apresentação (script sugerido, ~15 min)

> Ajuste o tom: linguagem de gestão, sem jargão técnico. O objetivo é mostrar que **dados viram
> decisão**.

1. **Abertura (1 min) — o que vamos ver:**
   "Este painel consolida as horas-aula dos nossos 45 instrutores a partir da planilha de regência
   que a coordenação já preenche. Ele responde: quem está ministrando, quanto, e se está cumprindo
   a carga prevista."

2. **Os 4 números azuis do topo (2 min):**
   "45 instrutores, ~37,3 mil horas-aula no ano, frequência média de 61%." Destaque de que 61% é a
   média geral, mas esconde realidades diferentes — e é isso que vamos destrinchar.

3. **Aba "Por Mês" (3 min):** mostre a linha da frequência.
   "Veja a curva do ano: janeiro começa em 41%, sobe para 78% em março, mantém 70–78% no semestre,
   cai para 18% em julho — férias — e retorna a 82% em agosto. Dezembro fecha em 37%. O padrão é
   absolutamente esperado para o calendário escolar."

4. **Aba "Visão Geral" (3 min):** histograma + ranking.
   "Quando olhamos a distribuição, 12 instrutores, 27% do quadro, estão abaixo de 50% de frequência.
   Estes são nossos pontos de atenção. Em contraste, 16 instrutores estão entre 70% e 100%, e 2
   acima de 100% — gente que dá conta e mais um pouco."

5. **Filtro por área: Manutenção automotiva (3 min):**
   "Filtrando a área (que o painel unifica, incluindo o polo do SEDUC), vemos que 7 de 13 instrutores
   estão abaixo de 50%. Os quatro menores índices do quadro inteiro estão aqui. Não é por acaso — a área
   precisa de atenção da coordenação: carga reduzida? afastamentos? remanejamento?"
   *(Opcional: filtrar em seguida **Polo = Jardim Vila Boa (SEDUC)** para mostrar os 2 instrutores do
   polo parceiro e explicar que é a mesma área em outro local.)*

6. **Destaques e boas práticas (2 min):**
   "Do outro lado, Gráfica editorial e Alimentos e bebidas rodam a 74–75%. É o espelho do que
   funciona — podemos usar esses instrutores como referência de planejamento de carga."

7. **Encerramento — plano de ação (1 min):**
   "Três encaminhamentos:
   1) coordenação valida os casos de baixa frequência (por quê?);
   2) padronizamos a planilha (preencher POLO/LOCAL, totais, fechar a divergência dos dois totais);
   3) definimos metas de frequência por período, respeitando férias.
   E o painel garante o acompanhamento mensal — vamos encerrar o ano acompanhando este número."

---

## 6. Mensagens-chave (para fixar na apresentação)

- **O dado já existia** (planilha) — o painel o **transforma em informação** com KPIs, rankings e
  evolução temporal.
- **A frequência é a régua básica:** quem cumpre o que foi previsto. Hoje, ~**27% do quadro está
  abaixo de 50%** — isso é dinheiro e capacidade de ensino subaproveitados.
- **O problema é concentrado e identificável:** a ferramenta aponta os **nomes**, **áreas**, **polos**
  e **meses** — o painel não julga, ele localiza.
- **Há exemplos de sucesso dentro da própria casa:** áreas e instrutores com frequência ≥100% —
  referência de como planejar.
- **Sazonalidade explica parte das quedas:** meta única para o ano é injusta; metas por período são
  melhores.
- **O painel também melhora o processo:** ele expõe falhas de preenchimento, o que fortalece a
  planilha-fonte e os próximos ciclos.

---

## 7. Glossário rápido

| Termo | Definição |
|---|---|
| **Regência** | Aulas ministradas / horas em sala de aula realizadas pelos instrutores |
| **Quadro** | Conjunto de instrutores efetivos da unidade (a planilha "Quadro 2026") |
| **Frequência (%)** | Horas-aula ÷ carga de regência esperada no mês |
| **H/AULA** | Horas-aula realizadas (contagem) |
| **Carga horária (Ch)** | Carga semanal prevista do instrutor (15 a 40 h no quadro atual) |
| **Extra-quadro** | Instrutor eventual/terceirizado fora do quadro (coluna ainda zerada) |
| **Heatmap** | Matriz colorida (instrutor × mês) que destaca padrões de frequência |

---

## 8. Dicas práticas para a apresentação

- **Abra o painel antes** em um navegador com a tela do projetor já encaixada. Teste o filtro de
  "Manutenção automotiva" para evitar surpresa.
- **Nunca apresente com filtros de outra sessão:** use "Limpar filtros" para começar do todo.
- **Se não tiver internet/projeção:** use o backup `apresentacao/BI_Regencia_Apresentacao.pptx` ou
  `apresentacao/GRAFICOS_BI.pdf` (gráficos em página única) e entregue o `RESUMO_1_PAGINA.docx`.
- **Mostre a evidência, não o tool:** cada insight deste guia tem o gráfico correspondente no painel —
  vá dos KPIs → Por Mês → Visão Geral → filtro por área. É uma narrativa, não uma lista de telas.
- **Encerre com um "próximo passo"** (validação da coordenação + metas por período): apresentação que
  termina com decisão é apresentação que convence.

---

## 9. Pacote de materiais da apresentação

| Arquivo | O que é |
|---|---|
| `GUIA_APRESENTACAO.md` | Este guia completo (conceitos, leituras, insights, script de fala) |
| `apresentacao/BI_Regencia_Apresentacao.pptx` | Deck de slides (tema SENAI escuro, com os gráficos reais) |
| `apresentacao/GRAFICOS_BI.pdf` | Todos os gráficos em páginas únicas — backup de projeção/impressão |
| `apresentacao/DEMO_LIVE.md` | Roteiro de cliques e falas para a demo ao vivo (com plano B) |
| `RESUMO_1_PAGINA.docx` | Síntese executiva em 1 página para entregar à diretora |
| `apresentacao/gerar_graficos.py` | Script para regerar os gráficos quando a planilha mudar |
| `apresentacao/gerar_ppt.py` | Script para regerar o PowerPoint |
| `apresentacao/gerar_pdf.py` | Script para regerar o PDF dos gráficos |
| `apresentacao/gerar_resumo.py` | Script para regerar o resumo de 1 página |

> Para atualizar tudo depois de uma nova versão da planilha:
> `python apresentacao\gerar_graficos.py` → `python apresentacao\gerar_ppt.py` →
> `python apresentacao\gerar_pdf.py` → `python apresentacao\gerar_resumo.py`
> (dependências: `pip install plotly kaleido python-pptx python-docx Pillow`).

---

*Guia gerado a partir da leitura dos dados reais de 2026 do projeto `BI-Regencia`.*
*Números referem-se à versão atual da planilha `REGÊNCIA - INSTRUTORES DO QUADRO 2026.xlsx` — conferir antes da apresentação, pois a planilha pode ser atualizada.*