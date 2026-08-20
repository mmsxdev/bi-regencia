# BI de Regência — Frequência de Instrutores em Sala de Aula

Dashboard interativo em **Streamlit** que analisa a frequência (horas-aula) dos instrutores do quadro usando a aba `CONSOLIDADO ` da planilha de regência.

## Como rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

O app abre automaticamente em `http://localhost:8501`.

> Se o arquivo da planilha não estiver ao lado do `app.py`, defina a variável de ambiente:
> ```bash
> set REGENCIA_EXCEL=C:\caminho\para\planilha.xlsx
> ```

## Conectando a planilha em tempo real (SharePoint / OneDrive / Outlook)

O app pode buscar a planilha **automaticamente por URL**, sem precisar copiar o arquivo para o servidor.
A cada nova atualização, basta salvar a planilha no SharePoint/OneDrive — o painel baixa a versão mais
recente no próximo carregamento e ainda faz atualização automática periódica.

### 1. Obtenha um link de download direto

O link normal de compartilhamento (`.../:x:/...?...&web=1`) não serve — o app precisa de um link que
entregue o **arquivo** diretamente. Duas formas:

**OneDrive pessoal (1drv.ms / onedrive.live.com)**

1. Abra o arquivo no OneDrive na web.
2. Clique em **...** → **Incorporar** (Embed) ou **Baixar**.
3. Copie o link do tipo:
   `https://onedrive.live.com/download?resid=ABC123&authkey=!XYZ`
   Use exatamente esse endereço.

**SharePoint Online (planilha compartilhada no Outlook/Teams)**

1. Certifique-se de que o compartilhamento permita **"Qualquer pessoa com o link"** (modo **Exibir**).
2. Peça o link de compartilhamento (formato `:x:/g/...?e=...`) e acrescente **`&download=1`** no final.
   - Exemplo real deste projeto:
     `https://sesigoias-my.sharepoint.com/:x:/g/personal/ednilzapontes_senai_fieg_com_br/IQBG2JwB_-gXToj05nRpbJy8AQHJ_rpN34nSj1pfrEoOIOs?e=52nID4&download=1`

3. Teste colando o link no navegador em uma aba anônima — se o arquivo `.xlsx` for baixado, o app vai conseguir ler.

> Para integração mais robusta (arquivos privados, sem compartilhar com "qualquer pessoa"), é preciso
> registrar um app no **Microsoft Entra ID** e usar a **Microsoft Graph API**
> (`GET /drives/{driveId}/items/{itemId}/content`). É mais complexo — se precisar, é um próximo passo opcional.

### 2. Configure o app

Defina a variável de ambiente (no Streamlit Cloud, em **Advanced settings → Secrets**):

```bash
REGENCIA_EXCEL_URL=https://sesigoias-my.sharepoint.com/:x:/g/personal/ednilzapontes_senai_fieg_com_br/IQBG2JwB_-gXToj05nRpbJy8AQHJ_rpN34nSj1pfrEoOIOs?e=52nID4&download=1
REGENCIA_REFRESH_MINUTES=10
```

- `REGENCIA_EXCEL_URL` — link de download direto da planilha (tem prioridade sobre o arquivo local).
- `REGENCIA_REFRESH_MINUTES` — frequência (em minutos) da re-busca automática (padrão: 10).
- O botão **"Atualizar dados agora"** na barra lateral força a atualização na hora.

Também dá para usar o **upload manual** na barra lateral (sem configurar nada) — ideal para testes.

## Estrutura dos dados

A aba `CONSOLIDADO ` tem uma linha por instrutor com:

- **DOCENTE**, **Ch** (carga horária), **ÁREA** e **POLO/LOCAL** (local de regência)
- **H/AULA** e **%** por mês (JAN a DEZ) — horas-aula realizadas e frequência (horas ÷ carga horária esperada no mês)
- **ANO** (total de horas no ano), **MÉDIA** e **EXTRA-QUADRO**

O `data_loader.py` localiza dinamicamente as colunas de cada mês pelos cabeçalhos da planilha e consolida tudo em um DataFrame mensal (`melt_monthly`).

### Normalização de áreas e polo

- O painel **unifica automaticamente** áreas com digitação/rótulos antigos (dicionário `AREA_NORM`):
  `Manutenção automotiva (JD)` → `Manutenção automotiva`, `Contrução Civil` → `Construção Civil`,
  `Grafica editorial` → `Gráfica editorial`.
- O campo **POLO/LOCAL** é lido do cabeçalho da planilha se existir coluna `POLO`/`LOCAL`; se não
  existir, é inferido: rótulo antigo "(JD)" → `John Deere`; demais → `Vila Canaã`.
  A coordenação pode adicionar a coluna `POLO` na planilha para controlar os valores oficialmente.

## O que o painel mostra

- **KPIs**: nº de instrutores, horas-aula no período, frequência média, total anual
- **Visão Geral**: frequência média por instrutor (top 15 de menor frequência, ranking completo nas abas seguintes), distribuição da frequência, horas por área e horas por polo
- **Por Instrutor**: ranking completo de horas-aula e heatmap de frequência (instrutor × mês)
- **Por Mês**: horas-aula totais por mês e evolução da frequência média
- **Tabela**: dados consolidados com download em CSV
- **Filtros**: por instrutor, área, polo/local e meses, com botão "Limpar filtros"

Cores da frequência: **azul institucional** para a maioria das barras e **vermelho SENAI** apenas para
situações de alerta (frequência média abaixo de 50%).

## Deploy

### Streamlit Cloud (gratuito — recomendado)

1. Suba este repositório para o GitHub.
2. Acesse [share.streamlit.io](https://share.streamlit.io) → **New app** → escolha o repositório.
3. Em "Main file" coloque `app.py`.
4. Em **Advanced settings → Secrets** defina a variável de ambiente com o link da planilha:

   ```
   REGENCIA_EXCEL_URL=https://onedrive.live.com/download?resid=ABC123&authkey=!XYZ
   ```

   (ou `REGENCIA_EXCEL=` apontando para o arquivo, se preferir manter a planilha no repositório).
5. O `requirements.txt` é instalado automaticamente e o app fica online, buscando a planilha
   atualizada automaticamente.

### Vercel

O Vercel **não tem um template oficial para Streamlit**; o suporte é possível via runtime Python e comando de inicialização, mas exige ajustes:

1. Adicione um `vercel.json`:

   ```json
   {
     "version": 2,
     "builds": [{ "src": "app.py", "use": "@vercel/python", "config": { "maxLambdaSize": "15mb" } }],
     "routes": [{ "src": "/(.*)", "dest": "app.py" }]
   }
   ```

2. Crie um `start.sh`:

   ```bash
   #!/bin/bash
   streamlit run app.py --server.port=$PORT --server.headless=true
   ```

   E aponte o handler para ele no `vercel.json` (ou use `@vercel/static` com build). Como o Streamlit usa WebSocket, é comum precisar configurar `single_session`/`streamlit server`.

> ### Recomendação
> Para projetos Streamlit, o **Streamlit Cloud** é muito mais simples e 100% gratuito. Se quiser publicar via Vercel mesmo assim, o caminho mais confiável hoje é empacotar com `@vercel/python` + `start.sh` e testar o deploy no domínio de preview — porém, resultado pode variar conforme a atualização do Streamlit.

## Arquivos

| Arquivo | Descrição |
|---|---|
| `app.py` | Dashboard Streamlit |
| `data_loader.py` | Leitura e consolidação da planilha |
| `requirements.txt` | Dependências Python |
| `vercel.json` / `start.sh` | Opcionais para deploy no Vercel |