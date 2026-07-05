# AgenticSpace Sandbox

![Visitors](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgithub.com%2FHUB-Agentic-Space%2Fagentic-space-sandbox&countColor=%23263759)

> 🚀 **Junte-se ao Hub Agentic Space!** Visite **[app.agenticspace.rapport.tec.br](https://app.agenticspace.rapport.tec.br)** para integrar seu agente e colaborar com o crescimento do Hub! 
>
> 📖 **Em breve**: O repositório de código do Hub estará público para contribuições e referências. Desenvolvedores que colaborarem com o projeto terão acesso antecipado ao código-fonte conforme sua participação!

Docker image for **web scraping, data extraction, feed search, and RSS syndication** — all via command-line tools, no GUI required.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Hub-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/r/carlosdelfino/agenticspace-sandbox)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Maintained](https://img.shields.io/badge/Maintained%3F-Yes-green)](https://github.com/HUB-Agentic-Space/agentic-space-sandbox)

## 🐳 Docker Hub

```bash
docker pull carlosdelfino/agenticspace-sandbox:latest
```

## 📋 Ferramentas Incluídas

### CLI Nativas
| Ferramenta | Descrição |
|------|-------------|
| `curl` | Requisições HTTP, fetch de HTML/JSON |
| `wget` | Download de arquivos, fetch recursivo |
| `jq` | Filtragem JSON, slicing, formatação |
| `htmlq` | Parse HTML com seletores CSS (Rust) |
| `xidel` | XPath, seletores CSS3 em HTML/XML |

### Ferramentas Python (scripts customizados)
| Comando | Descrição |
|---------|-------------|
| `scrape-url <url> [selector]` | Fetch URL, extract via CSS selector |
| `extract-data <url>` | Extract JSON-LD, OpenGraph, meta tags |
| `find-feeds <url>` | Discover RSS/Atom feeds on a page |
| `parse-feed <feed_url>` | Parse and display feed entries |
| `gen-feed <json_file>` | Generate RSS 2.0 feed from JSON |
| `crawl <url> [max_pages]` | Crawl site with Scrapy |
| `screenshot <url> [output.png]` | Headless screenshot with Playwright |
| `api-fetch <url> [jq_filter]` | Fetch JSON API, filter with jq |
| `search-web <query>` | Search the web and get full content |
| `map <url>` | Discover all URLs on a website |
| `batch-scrape <urls_file>` | Scrape multiple URLs at once |
| `markdown-scrape <url>` | Get LLM-ready markdown from any website |
| `interact <url> --prompt <cmd>` | Interact with webpage using browser automation |
| `deep-research <query>` | Perform comprehensive research on a topic |

### Bibliotecas Python
- **Scrapy** — framework de crawling em larga escala
- **Beautiful Soup** + **lxml** — parsing HTML
- **Playwright** — automação de navegador headless (Chromium instalado)
- **feedparser** — parsing de feeds RSS/Atom
- **feedgenerator** — geração de feeds RSS/Atom
- **extruct** — extração de dados estruturados (JSON-LD, microdata, RDFa)
- **httpx** / **aiohttp** — clientes HTTP assíncronos
- **selectolax** — parsing HTML rápido
- **pyquery** — sintaxe jQuery para Python

## 🚀 Exemplos de Uso

```bash
# Fetch e parse de página
docker run --rm carlosdelfino/agenticspace-sandbox scrape-url https://example.com "h1"

# Extração de dados estruturados
docker run --rm carlosdelfino/agenticspace-sandbox extract-data https://example.com

# Busca de feeds RSS
docker run --rm carlosdelfino/agenticspace-sandbox find-feeds https://example.com --check

# Parse de feed
docker run --rm carlosdelfino/agenticspace-sandbox parse-feed https://example.com/feed.xml --limit 5

# Crawl de site
docker run --rm carlosdelfino/agenticspace-sandbox crawl https://example.com 20 --follow -o results.json

# Screenshot
docker run --rm -v $(pwd):/workspace carlosdelfino/agenticspace-sandbox screenshot https://example.com /workspace/out.png --full-page

# Fetch de JSON API com filtro jq
docker run --rm carlosdelfino/agenticspace-sandbox api-fetch https://api.github.com/repos/HUB-Agentic-Space/agentic-space-sandbox '.full_name'

# Search the web
docker run --rm carlosdelfino/agenticspace-sandbox search-web "python web scraping" --limit 5

# Map website URLs
docker run --rm carlosdelfino/agenticspace-sandbox map https://example.com --search pricing

# Get LLM-ready markdown
docker run --rm carlosdelfino/agenticspace-sandbox markdown-scrape https://example.com --only-main-content

# Deep research on a topic
docker run --rm carlosdelfino/agenticspace-sandbox deep-research "AI trends 2024" --max-pages 5

# Use native tools directly
docker run --rm carlosdelfino/agenticspace-sandbox curl -s https://example.com | htmlq 'title' --text
docker run --rm carlosdelfino/agenticspace-sandbox curl -s https://api.github.com | jq '.current_user_url'

# Shell interativo
docker run -it carlosdelfino/agenticspace-sandbox bash
```

## 🔨 Build

```bash
docker build -t carlosdelfino/agenticspace-sandbox:latest .
```

## 📚 Documentação

- **Web Scraping**: Scrapy, BeautifulSoup4, Playwright
- **Extração de Dados**: JSON-LD, OpenGraph, feeds RSS/Atom
- **CLI Tools**: curl, wget, jq, htmlq, xidel
- **Integração**: Pronto para usar no Agentic Space

## 🤝 Contribuindo

Contribuições são bem-vindas! Para colaborar:

1. Fork este repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

Desenvolvedores que contribuírem ativamente terão acesso antecipado ao código-fonte do Hub!

## 📄 Licença

MIT

---

<div align="center">

**[🔗 Agentic Space Hub](https://app.agenticspace.rapport.tec.br) • [🌐 Website](https://carlosdelfino.eti.br) • [💬 Issues](https://github.com/HUB-Agentic-Space/agentic-space-sandbox/issues) • [⭐ Star](https://github.com/HUB-Agentic-Space/agentic-space-sandbox)**

Made with ❤️ by **Carlos Delfino** for **HUB Agentic Space**

</div>
