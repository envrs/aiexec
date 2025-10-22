<!-- markdownlint-disable MD030 -->

![Aiexec logo](./docs/static/img/aiexec-logo-color-black-solid.svg)

[![Release Notes](https://img.shields.io/github/release/khulnasoft/aiexec?style=flat-square)](https://github.com/khulnasoft/aiexec/releases)
[![PyPI - License](https://img.shields.io/badge/license-MIT-orange)](https://opensource.org/licenses/MIT)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/aiexec?style=flat-square)](https://pypistats.org/packages/aiexec)
[![GitHub star chart](https://img.shields.io/github/stars/khulnasoft/aiexec?style=flat-square)](https://star-history.com/#khulnasoft/aiexec)
[![Open Issues](https://img.shields.io/github/issues-raw/khulnasoft/aiexec?style=flat-square)](https://github.com/khulnasoft/aiexec/issues)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/khulnasoft.svg?style=social&label=Follow%20%40Aiexec)](https://twitter.com/aiexec_ai)
[![YouTube Channel](https://img.shields.io/youtube/channel/subscribers/UCn2bInQrjdDYKEEmbpwblLQ?label=Subscribe)](https://www.youtube.com/@Aiexec)
[![Discord Server](https://img.shields.io/discord/1116803230643527710?logo=discord&style=social&label=Join)](https://discord.gg/EqksyE2EX9)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/khulnasoft/aiexec)

> [!CAUTION]
> - Aiexec versions 1.6.0 through 1.6.3 have a critical bug where `.env` files are not read, potentially causing security vulnerabilities. **DO NOT** upgrade to these versions if you use `.env` files for configuration. Instead, upgrade to 1.6.4, which includes a fix for this bug.
> - Windows users of Aiexec Desktop should **not** use the in-app update feature to upgrade to Aiexec version 1.6.0. For upgrade instructions, see [Windows Desktop update issue](https://docs.aiexec.org/release-notes#windows-desktop-update-issue).
> - Users must update to Aiexec >= 1.3 to protect against [CVE-2025-3248](https://nvd.nist.gov/vuln/detail/CVE-2025-3248)
> - Users must update to Aiexec >= 1.5.1 to protect against [CVE-2025-57760](https://github.com/khulnasoft/aiexec/security/advisories/GHSA-4gv9-mp8m-592r)
>
> For security information, see our [Security Policy](./SECURITY.md) and [Security Advisories](https://github.com/khulnasoft/aiexec/security/advisories).

[Aiexec](https://aiexec.org) is a powerful tool for building and deploying AI-powered agents and workflows. It provides developers with both a visual authoring experience and built-in API and MCP servers that turn every workflow into a tool that can be integrated into applications built on any framework or stack. Aiexec comes with batteries included and supports all major LLMs, vector databases and a growing library of AI tools.

## ✨ Highlight features

- **Visual builder interface** to quickly get started and iterate .
- **Source code access** lets you customize any component using Python.
- **Interactive playground** to immediately test and refine your flows with step-by-step control.
- **Multi-agent orchestration** with conversation management and retrieval.
- **Deploy as an API** or export as JSON for Python apps.
- **Deploy as an MCP server** and turn your flows into tools for MCP clients.
- **Observability** with LangSmith, LangFuse and other integrations.
- **Enterprise-ready** security and scalability.

## ⚡️ Quickstart

### Install locally (recommended)

Requires Python 3.10–3.13 and [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended package manager).

#### Install

```shell
$ uv pip install aiexec -U
```

Installs the latest Aiexec package.

#### Run

```shell
$ uv run aiexec run
```

Starts the Aiexec server at http://127.0.0.1:7860.

That's it! You're ready to build with Aiexec 🎉

### Other install options

- [Docker](https://docs.aiexec.org/deployment-docker)
- [Desktop app](https://docs.aiexec.org/get-started-installation#install-and-run-aiexec-desktop)

### Install from repo

If you're contributing or running from source, see [DEVELOPMENT.md](./DEVELOPMENT.md) for setup instructions.

## 📦 Deployment

Aiexec is completely open source and you can deploy it to all major deployment clouds. To learn how to use Docker to deploy Aiexec, see the [Docker deployment guide](https://docs.aiexec.org/deployment-docker).

## ⭐ Stay up-to-date

Star Aiexec on GitHub to be instantly notified of new releases.

![Star Aiexec](https://github.com/user-attachments/assets/03168b17-a11d-4b2a-b0f7-c1cce69e5a2c)

## 👋 Contribute

We welcome contributions from developers of all levels. If you'd like to contribute, please check our [contributing guidelines](./CONTRIBUTING.md) and help make Aiexec more accessible.

---

[![Star History Chart](https://api.star-history.com/svg?repos=khulnasoft/aiexec&type=Timeline)](https://star-history.com/#khulnasoft/aiexec&Date)

## ❤️ Contributors

[![aiexec contributors](https://contrib.rocks/image?repo=khulnasoft/aiexec)](https://github.com/khulnasoft/aiexec/graphs/contributors)
