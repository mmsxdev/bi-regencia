# ROTEIRO DA DEMO AO VIVO — BI DE REGÊNCIA

Checklist e sequência de cliques para apresentar o painel à diretora. Tempo estimado: **15–20 min**.

---

## 1. Antes de apresentar (no dia anterior)

- [ ] Rodar o app uma vez e confirmar que abre: `streamlit run app.py` (na pasta do projeto)
- [ ] Confirmar a fonte de dados: barra lateral mostra "**Conexão: arquivo local**" ou "**Conexão: URL**"
- [ ] Clicar em **Atualizar dados agora** e ver os KPIs atualizarem
- [ ] Testar o filtro **Área → Manutenção automotiva** e o botão **Limpar filtros**
- [ ] Se for usar projeção: abrir o navegador em tela cheia (F11) com o painel já carregado
- [ ] Ter à mão os backups: `apresentacao/BI_Regencia_Apresentacao.pptx`,
      `apresentacao/GRAFICOS_BI.pdf` e `RESUMO_1_PAGINA.docx`

## 2. Sequência na hora (ao vivo)

| Passo | O que fazer | O que dizer (resumo) |
|---|---|---|
| 1 | Tela inicial | "Este painel consolida a regência dos 45 instrutores a partir da planilha de regência." |
| 2 | Apontar os 4 KPIs | "45 instrutores, 61% de frequência média, 37,3 mil horas-aula e 12 instrutores abaixo de 50%." |
| 3 | Aba **Por Mês** → gráfico de linha | "A curva do ano: vale em janeiro, pico no 2º trimestre, queda em julho (férias), recuperação em agosto." |
| 4 | Aba **Visão Geral** → histograma | "27% do quadro está abaixo de 50%; só 2 instrutores passam de 100%." |
| 5 | Aba **Visão Geral** → horas por área | "O volume se concentra em Gráfica editorial e Alimentos e bebidas." |
| 6 | Filtrar **Área = Manutenção automotiva** | "A área crítica: área única de 13 instrutores, 7 abaixo de 50%. Nome e área identificados." |
| 6a | (opcional) Filtrar **Polo = Jardim Vila Boa (SEDUC)** | "Estes 2 são os instrutores do polo da escola parceira — a mesma área, em outro local." |
| 7 | Clicar **Limpar filtros** | "Voltamos ao quadro completo." |
| 8 | Aba **Por Instrutor** → heatmap | "Radiografia mês a mês: colunas fracas em julho/dezembro são calendário; linhas vermelhas são gestão." |
| 9 | Aba **Tabela** → **Baixar dados em CSV** (opcional) | "Dá para auditar/exportar qualquer recorte." |
| 10 | Encerrar | "Próximos passos: validar casos com coordenação, padronizar planilha e metas por período." |

## 3. Filtros = perguntas ao vivo (truques úteis)

- **Só um instrutor:** selecionar o nome em **Instrutor(es)** → KPIs e gráficos mostram aquele docente.
- **Um semestre:** em **Meses do período**, tirar JAN–JUL para ver o segundo semestre.
- **Uma área (unificada):** **Área = Manutenção automotiva** → mostra os 13 instrutores (incluindo o
  polo JD unificado) → ranking interno da área.
- **Ver o polo SEDUC:** **Polo = Jardim Vila Boa (SEDUC)** → isola os 2 instrutores do polo parceiro.
- **Perceber a unificação:** no filtro **Área**, a opção única é "Manutenção automotiva" (sem "(JD)").

## 4. Plano B (sem internet / app fora do ar)

- Abrir `apresentacao/BI_Regencia_Apresentacao.pptx` — deck completo com os mesmos gráficos.
- Abrir `apresentacao/GRAFICOS_BI.pdf` — gráficos em página única para projetar.
- Entregar `RESUMO_1_PAGINA.docx` — síntese em 1 página.

## 5. Frases de reforço (para fechar)

- "O dado já existia na planilha; o BI o transforma em informação de gestão."
- "Não é o painel que julga o instrutor — ele localiza o caso para a coordenação tratar."
- "Meta única anual seria injusta: julho e dezembro são férias/recesso."