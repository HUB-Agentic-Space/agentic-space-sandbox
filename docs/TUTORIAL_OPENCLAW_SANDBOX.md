# Tutorial: Configurando o AgenticSpace Sandbox no OpenClaw

Este tutorial explica, passo a passo, como configurar a imagem Docker
`carlosdelfino/agenticspace-sandbox:latest` como sandbox de um agente no
OpenClaw. Se você nunca configurou um agente com sandbox Docker antes,
este guia foi escrito para você.

---

## Índice

1. [O que é uma sandbox no OpenClaw?](#1-o-que-é-uma-sandbox-no-openclaw)
2. [Pré-requisitos](#2-pré-requisitos)
3. [Entendendo a estrutura do `openclaw.json`](#3-entendendo-a-estrutura-do-openclawjson)
4. [Anatomia da configuração `sandbox`](#4-anatomia-da-configuração-sandbox)
5. [Configuração passo a passo](#5-configuração-passo-a-passo)
6. [Exemplo completo: Agente Web Scraper](#6-exemplo-completo-agente-web-scraper)
7. [Explicação detalhada de cada campo](#7-explicação-detalhada-de-cada-campo)
8. [Bind mounts: como compartilhar arquivos com o container](#8-bind-mounts-como-compartilhar-arquivos-com-o-container)
9. [Variáveis de ambiente](#9-variáveis-de-ambiente)
10. [Configurações opcionais avançadas](#10-configurações-opcionais-avançadas)
11. [Verificando se tudo funciona](#11-verificando-se-tudo-funciona)
12. [Solução de problemas comuns](#12-solução-de-problemas-comuns)

---

## 1. O que é uma sandbox no OpenClaw?

Uma **sandbox** é um ambiente isolado onde o agente executa comandos. Em
vez de rodar comandos diretamente no seu sistema, o OpenClaw pode executá-los
dentro de um container Docker. Isso traz três benefícios principais:

- **Segurança:** o agente não tem acesso direto ao seu sistema operacional
- **Reprodutibilidade:** o ambiente é sempre o mesmo, independente da máquina
- **Isolamento:** ferramentas e dependências ficam contidas na imagem

A imagem `carlosdelfino/agenticspace-sandbox:latest` vem pré-configurada com
ferramentas de web scraping, extração de dados, busca de feeds e sindicação
RSS — tudo via linha de comando, ideal para automação.

---

## 2. Pré-requisitos

Antes de começar, certifique-se de que você tem:

- **Docker** instalado e rodando na sua máquina
  ```bash
  docker --version
  docker info
  ```
- **OpenClaw** instalado e configurado
- O arquivo de configuração principal em `~/.openclaw/openclaw.json`
- A imagem Docker baixada:
  ```bash
  docker pull carlosdelfino/agenticspace-sandbox:latest
  ```

---

## 3. Entendendo a estrutura do `openclaw.json`

O arquivo `~/.openclaw/openclaw.json` é o arquivo central de configuração do
OpenClaw. Ele tem esta estrutura geral:

```
~/.openclaw/openclaw.json
├── "tools"          → configuração global de ferramentas
├── "meta"           → metadados (versão, última atualização)
├── "agents"         → lista de agentes
│   ├── "defaults"   → configurações padrão para todos os agentes
│   └── [agentes individuais]  → cada agente é um objeto na lista
│       ├── "id"
│       ├── "name"
│       ├── "workspace"
│       ├── "model"
│       ├── "sandbox"     ← É AQUI QUE CONFIGURAMOS O DOCKER
│       ├── "heartbeat"
│       ├── "tools"
│       └── "skills"
```

Cada agente é um objeto JSON dentro do array `agents`. A configuração da
sandbox fica dentro de cada agente individual, na chave `"sandbox"`.

---

## 4. Anatomia da configuração `sandbox`

Aqui está o bloco de configuração que vamos explicar, adaptado para a imagem
AgenticSpace Sandbox:

```json
"sandbox": {
  "mode": "all",
  "scope": "agent",
  "workspaceAccess": "rw",
  "backend": "docker",
  "docker": {
    "image": "carlosdelfino/agenticspace-sandbox:latest",
    "network": "bridge",
    "extraHosts": [
      "host.docker.internal:host-gateway"
    ],
    "binds": [
      "/home/SEU_USUARIO/workspace/openclaw-workspace/skills:/skills:ro",
      "/home/SEU_USUARIO/workspace/openclaw-workspace/plugins:/plugins:ro"
    ],
    "dangerouslyAllowExternalBindSources": true,
    "env": {
      "PUID": "1000",
      "PGID": "1000",
      "TZ": "America/Fortaleza"
    }
  }
}
```

Vamos detalhar cada parte nas seções a seguir.

---

## 5. Configuração passo a passo

### Passo 1: Abra o arquivo de configuração

```bash
nano ~/.openclaw/openclaw.json
```

Ou use seu editor favorito (VS Code, Vim, etc).

### Passo 2: Localize o agente ou crie um novo

Procure pela seção `"agents"` no arquivo. Você verá uma lista (array JSON)
de agentes. Cada agente é um objeto entre `{ }`.

Para **criar um novo agente**, adicione um novo objeto na lista:

```json
{
  "id": "agentic-space-scraper",
  "name": "Agentic Space Scraper",
  "workspace": "/home/SEU_USUARIO/workspace/openclaw-workspace/agents/agentic-space-scraper",
  "agentDir": "/home/SEU_USUARIO/.openclaw/agents/agentic-space-scraper/agent",
  "model": "openrouter/free",
  "sandbox": {
    ...
  }
}
```

### Passo 3: Adicione o bloco `sandbox`

Dentro do objeto do agente, adicione a configuração de sandbox:

```json
"sandbox": {
  "mode": "all",
  "scope": "agent",
  "workspaceAccess": "rw",
  "backend": "docker",
  "docker": {
    "image": "carlosdelfino/agenticspace-sandbox:latest",
    "network": "bridge",
    "extraHosts": [
      "host.docker.internal:host-gateway"
    ],
    "binds": [
      "/home/SEU_USUARIO/workspace/openclaw-workspace/skills:/skills:ro",
      "/home/SEU_USUARIO/workspace/openclaw-workspace/plugins:/plugins:ro"
    ],
    "dangerouslyAllowExternalBindSources": true,
    "env": {
      "PUID": "1000",
      "PGID": "1000",
      "TZ": "America/Fortaleza"
    }
  }
}
```

> **Atenção:** substitua `SEU_USUARIO` pelo seu nome de usuário real no Linux.
> Por exemplo: `/home/carlosdelfino/workspace/...`

### Passo 4: Salve o arquivo

Salve e feche o arquivo. O OpenClaw recarrega a configuração automaticamente
ou na próxima reinicialização.

---

## 6. Exemplo completo: Agente Web Scraper

Aqui está um exemplo completo de um agente configurado para usar a imagem
AgenticSpace Sandbox:

```json
{
  "id": "agentic-space-scraper",
  "name": "Agentic Space Scraper",
  "workspace": "/home/carlosdelfino/workspace/openclaw-workspace/agents/agentic-space-scraper",
  "agentDir": "/home/carlosdelfino/.openclaw/agents/agentic-space-scraper/agent",
  "model": "openrouter/free",
  "groupChat": {
    "historyLimit": 5,
    "mentionPatterns": [
      "@?Scraper",
      "\\bScraper\\b"
    ]
  },
  "sandbox": {
    "mode": "all",
    "scope": "agent",
    "workspaceAccess": "rw",
    "backend": "docker",
    "docker": {
      "image": "carlosdelfino/agenticspace-sandbox:latest",
      "network": "bridge",
      "extraHosts": [
        "host.docker.internal:host-gateway"
      ],
      "binds": [
        "/home/carlosdelfino/workspace/openclaw-workspace/skills:/skills:ro",
        "/home/carlosdelfino/workspace/openclaw-workspace/plugins:/plugins:ro"
      ],
      "dangerouslyAllowExternalBindSources": true,
      "env": {
        "PUID": "1000",
        "PGID": "1000",
        "TZ": "America/Fortaleza"
      }
    }
  },
  "heartbeat": {
    "every": "30m",
    "lightContext": false,
    "isolatedSession": false,
    "skipWhenBusy": false
  },
  "tools": {
    "alsoAllow": [
      "duckduckgo",
      "web_search",
      "web_fetch",
      "browser",
      "message"
    ]
  },
  "skills": [
    "firecrawl",
    "firecrawl-search",
    "firecrawl-scrape",
    "self-improving-agent"
  ]
}
```

---

## 7. Explicação detalhada de cada campo

### `sandbox.mode`

```json
"mode": "all"
```

Controla **quando** a sandbox é usada:

| Valor | Descrição |
|-------|-----------|
| `"all"` | Todos os comandos executados pelo agente rodam na sandbox |
| `"exec"` | Apenas comandos de execução (shell) rodam na sandbox |
| `"none"` | Sandbox desativada (comandos rodam no host) |

**Recomendado:** `"all"` para máximo isolamento.

### `sandbox.scope`

```json
"scope": "agent"
```

Define o escopo do isolamento:

| Valor | Descrição |
|-------|-----------|
| `"agent"` | Cada agente tem seu próprio container isolado |
| `"session"` | Cada sessão de conversa tem seu próprio container |
| `"global"` | Todos os agentes compartilham o mesmo container |

**Recomendado:** `"agent"` para que cada agente tenha seu ambiente próprio.

### `sandbox.workspaceAccess`

```json
"workspaceAccess": "rw"
```

Define as permissões de acesso ao workspace do agente:

| Valor | Descrição |
|-------|-----------|
| `"rw"` | Leitura e escrita (o agente pode criar/modificar arquivos) |
| `"ro"` | Somente leitura (o agente pode ler mas não modificar) |
| `"none"` | Sem acesso ao workspace |

**Recomendado:** `"rw"` para que o agente possa salvar resultados de scraping.

### `sandbox.backend`

```json
"backend": "docker"
```

Define a tecnologia de isolamento. Atualmente, `"docker"` é o backend
principal suportado.

### `sandbox.docker.image`

```json
"image": "carlosdelfino/agenticspace-sandbox:latest"
```

A imagem Docker que será usada como ambiente. Esta imagem contém:

- **CLI tools:** `curl`, `wget`, `jq`, `htmlq`, `xidel`
- **Python tools:** `scrape-url`, `extract-data`, `find-feeds`, `parse-feed`,
  `gen-feed`, `crawl`, `screenshot`, `api-fetch`
- **Bibliotecas:** Scrapy, BeautifulSoup, Playwright (Chromium headless),
  feedparser, feedgenerator, extruct, httpx, aiohttp, e mais

### `sandbox.docker.network`

```json
"network": "bridge"
```

O modo de rede do container:

| Valor | Descrição |
|-------|-----------|
| `"bridge"` | Rede Docker padrão (isolada, com NAT) — **recomendado** |
| `"host"` | Compartilha a rede do host (menos isolamento) |
| `"none"` | Sem rede (máximo isolamento, mas sem acesso à internet) |

**Importante:** Para web scraping, a sandbox **precisa** de acesso à internet.
Use `"bridge"` (padrão) ou `"host"`.

### `sandbox.docker.extraHosts`

```json
"extraHosts": [
  "host.docker.internal:host-gateway"
]
```

Adiciona entradas no `/etc/hosts` do container. A entrada
`host.docker.internal:host-gateway` permite que o container acesse serviços
rodando na máquina host (útil se você tem APIs locais que o agente precisa
chamar).

### `sandbox.docker.binds`

```json
"binds": [
  "/home/carlosdelfino/workspace/openclaw-workspace/skills:/skills:ro",
  "/home/carlosdelfino/workspace/openclaw-workspace/plugins:/plugins:ro"
]
```

Monta diretórios do host dentro do container. O formato é:

```
"caminho_no_host:caminho_no_container:modo"
```

- **`ro`** = read-only (somente leitura)
- **`rw`** = read-write (leitura e escrita)

Neste exemplo:
- `/skills` → habilidades do OpenClaw (somente leitura, para o agente consultar)
- `/plugins` → plugins do OpenClaw (somente leitura)

Você pode adicionar mais binds, por exemplo, um diretório para salvar
resultados de scraping:

```json
"binds": [
  "/home/carlosdelfino/workspace/openclaw-workspace/skills:/skills:ro",
  "/home/carlosdelfino/workspace/openclaw-workspace/plugins:/plugins:ro",
  "/home/carlosdelfino/workspace/openclaw-workspace/agents/agentic-space-scraper/output:/workspace/output:rw"
]
```

### `sandbox.docker.dangerouslyAllowExternalBindSources`

```json
"dangerouslyAllowExternalBindSources": true
```

Permite que binds apontem para diretórios fora do workspace padrão do
OpenClaw. Sem esta opção, o OpenClaw pode bloquear binds para caminhos
externos por segurança.

> **Aviso:** O nome "dangerously" indica que esta opção reduz o isolamento.
> Use apenas se você confia nos caminhos configurados.

### `sandbox.docker.env`

```json
"env": {
  "PUID": "1000",
  "PGID": "1000",
  "TZ": "America/Fortaleza"
}
```

Variáveis de ambiente injetadas no container:

| Variável | Descrição |
|----------|-----------|
| `PUID` | ID do usuário que rodará os processos no container (evita problemas de permissão com arquivos montados) |
| `PGID` | ID do grupo correspondente |
| `TZ` | Fuso horário (para timestamps corretos em logs e resultados) |

**Como descobrir seu PUID/PGID:**

```bash
id -u  # mostra seu UID (PUID)
id -g  # mostra seu GID (PGID)
```

---

## 8. Bind mounts: como compartilhar arquivos com o container

Bind mounts são a forma de compartilhar arquivos entre sua máquina e o
container Docker. Pense nisso como "pastas compartilhadas".

### Sintaxe

```
"/caminho/no/host:/caminho/no/container:modo"
```

### Exemplos práticos

```json
"binds": [
  // Skills (somente leitura — o agente consulta mas não modifica)
  "/home/carlosdelfino/workspace/openclaw-workspace/skills:/skills:ro",

  // Plugins (somente leitura)
  "/home/carlosdelfino/workspace/openclaw-workspace/plugins:/plugins:ro",

  // Diretório de saída (leitura e escrita — o agente salva resultados aqui)
  "/home/carlosdelfino/workspace/openclaw-workspace/agents/agentic-space-scraper/output:/workspace/output:rw",

  // Diretório de configurações (somente leitura)
  "/home/carlosdelfino/workspace/openclaw-workspace/agents/agentic-space-scraper/config:/workspace/config:ro"
]
```

### Dica importante

Sempre crie os diretórios no host **antes** de iniciar o agente:

```bash
mkdir -p /home/carlosdelfino/workspace/openclaw-workspace/agents/agentic-space-scraper/output
mkdir -p /home/carlosdelfino/workspace/openclaw-workspace/agents/agentic-space-scraper/config
```

---

## 9. Variáveis de ambiente

Além das variáveis padrão (`PUID`, `PGID`, `TZ`), você pode adicionar
variáveis específicas para o AgenticSpace Sandbox:

```json
"env": {
  "PUID": "1000",
  "PGID": "1000",
  "TZ": "America/Fortaleza",
  "PLAYWRIGHT_BROWSERS_PATH": "/opt/playwright-browsers",
  "PYTHONUNBUFFERED": "1",
  "SCRAPE_USER_AGENT": "MyBot/1.0 (+https://example.com)"
}
```

| Variável | Descrição |
|----------|-----------|
| `PLAYWRIGHT_BROWSERS_PATH` | Onde os browsers do Playwright estão instalados |
| `PYTHONUNBUFFERED` | `1` = output Python em tempo real (sem buffer) |
| `SCRAPE_USER_AGENT` | User-Agent customizado para scraping (se seus scripts usarem) |

---

## 10. Configurações opcionais avançadas

### Heartbeat (batimento cardíaco do agente)

Controla com que frequência o agente "acorda" para verificar tarefas:

```json
"heartbeat": {
  "every": "30m",
  "lightContext": false,
  "isolatedSession": false,
  "skipWhenBusy": false
}
```

| Campo | Descrição |
|-------|-----------|
| `every` | Intervalo entre verificações (`"30m"`, `"1h"`, `"5m"`, etc) |
| `lightContext` | `true` = usa menos contexto (economiza tokens) |
| `isolatedSession` | `true` = cada heartbeat roda em sessão separada |
| `skipWhenBusy` | `true` = pula o heartbeat se o agente estiver ocupado |

### Tools (ferramentas permitidas)

```json
"tools": {
  "alsoAllow": [
    "duckduckgo",
    "web_search",
    "web_fetch",
    "browser",
    "message"
  ]
}
```

Lista ferramentas adicionais que o agente pode usar além das padrão.
Para um agente de scraping, recomendamos:

- `web_search` — buscar na web
- `web_fetch` — fetch de URLs
- `browser` — automação de browser
- `duckduckgo` — busca via DuckDuckGo
- `firecrawl_search` — busca via Firecrawl (se disponível)
- `firecrawl_scrape` — scrape via Firecrawl (se disponível)

### Skills (habilidades)

```json
"skills": [
  "firecrawl",
  "firecrawl-search",
  "firecrawl-scrape",
  "self-improving-agent"
]
```

Skills são capacidades pré-configuradas que o agente pode usar. Para
scraping, as skills do Firecrawl são especialmente úteis.

### GroupChat (chat em grupo)

```json
"groupChat": {
  "historyLimit": 5,
  "mentionPatterns": [
    "@?Scraper",
    "\\bScraper\\b"
  ]
}
```

Permite que o agente seja mencionado em chats grupais:

- `historyLimit` — quantas mensagens de histórico o agente vê
- `mentionPatterns` — padrões regex que ativam o agente (ex: `@Scraper` ou
  apenas a palavra `Scraper`)

---

## 11. Verificando se tudo funciona

### Teste 1: Verificar se o agente reconhece a sandbox

Inicie uma conversa com o agente e peça para ele executar:

```
Execute: scrape-url https://example.com "h1"
```

O agente deve responder com algo como:

```
Example Domain
```

### Teste 2: Verificar ferramentas CLI nativas

```
Execute: curl -s https://httpbin.org/json | jq '.slideshow.title'
```

Resposta esperada:

```json
"Sample Slide Show"
```

### Teste 3: Verificar find-feeds

```
Execute: find-feeds https://www.theverge.com --check
```

### Teste 4: Verificar Playwright (screenshot)

```
Execute: screenshot https://example.com /workspace/output/test.png --full-page
```

Verifique se o arquivo foi criado no diretório de output mapeado no bind.

### Teste 5: Shell interativo no container

Para debug manual, você pode entrar no container:

```bash
docker run -it carlosdelfino/agenticspace-sandbox:latest bash
```

Dentro do container, teste os comandos:

```bash
scrape-url --help
find-feeds --help
parse-feed --help
curl --version
jq --version
python3 -c "import scrapy; print(scrapy.__version__)"
```

---

## 12. Solução de problemas comuns

### Problema: "Permission denied" ao executar scripts

**Causa:** Os scripts não têm permissão de execução.

**Solução:** A imagem já vem com permissões corretas, mas se você estiver
montando scripts próprios via bind, adicione permissões:

```bash
chmod +x /home/carlosdelfino/workspace/openclaw-workspace/agents/agentic-space-scraper/scripts/*.py
```

### Problema: "docker: not found" ou "Cannot connect to Docker"

**Causa:** Docker não está rodando ou não está acessível.

**Solução:**

```bash
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Faça logout e login novamente
```

### Problema: "image not found" ou "pull access denied"

**Causa:** A imagem não foi baixada ou não está acessível.

**Solução:**

```bash
docker pull carlosdelfino/agenticspace-sandbox:latest
```

### Problema: Playwright não consegue abrir browser

**Causa:** Dependências do Chromium podem estar faltando.

**Solução:** A imagem já instala as dependências, mas se você estiver
construindo uma imagem customizada, certifique-se de rodar:

```bash
playwright install --with-deps chromium
```

### Problema: Arquivos criados no container pertencem ao root

**Causa:** O container está rodando como root e os arquivos montados via
bind ficam com permissão root.

**Solução:** Use as variáveis `PUID` e `PGID` com seu UID/GID real:

```bash
id -u  # PUID
id -g  # PGID
```

```json
"env": {
  "PUID": "1000",
  "PGID": "1000"
}
```

### Problema: "JSON parse error" no openclaw.json

**Causa:** Erro de sintaxe no JSON (vírgula faltando, aspas incorretas, etc).

**Solução:** Valide o JSON:

```bash
cat ~/.openclaw/openclaw.json | jq .
```

Se houver erro, o `jq` apontará a linha e coluna do problema.

### Problema: O agente não consegue acessar a internet

**Causa:** Rede do container configurada como `"none"` ou firewall bloqueando.

**Solução:** Use `"network": "bridge"` (padrão) e verifique se não há
firewall bloqueando o tráfego Docker:

```bash
sudo iptables -L DOCKER -n
```

---

## Resumo rápido

Para configurar o AgenticSpace Sandbox como sandbox de um agente no OpenClaw:

1. **Baixe a imagem:** `docker pull carlosdelfino/agenticspace-sandbox:latest`
2. **Abra o config:** `nano ~/.openclaw/openclaw.json`
3. **Adicione o bloco `sandbox`** no agente desejado (veja seção 5)
4. **Ajuste os caminhos** dos binds para o seu usuário
5. **Configure `PUID`/`PGID`** com seu UID/GID
6. **Salve e teste** com os comandos da seção 11

A imagem vem pronta para uso com todas as ferramentas de scraping, extração
de dados, feeds e RSS pré-instaladas. Basta configurar e usar!
