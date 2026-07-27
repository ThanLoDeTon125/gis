# Prerequisites

This document lists the developer tools that you must install before you clone the repository.
The instructions are for **macOS**, the team standard. Follow the official installation guide for
each tool. The links are in the tables below.

> The installation order is important: install **Homebrew** first, then **Fish → Fisher →
> nvm.fish**. After you complete this document, follow [INSTALLATION.md](./INSTALLATION.md) to set
> up the repository.

## Required

| #   | Tool                       | Install guide                                          | Why                                                                                           |
| --- | -------------------------- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| 1   | **Homebrew**               | https://brew.sh                                        | The macOS package manager. You install all the other tools through it                         |
| 2   | **Ghostty**                | https://ghostty.org/docs/install                       | The team reference terminal (GPU-accelerated)                                                 |
| 3   | **Fish shell**             | https://fishshell.com                                  | The team shell. The repository tooling expects it. Set it as your login shell                 |
| 4   | **Fisher**                 | https://github.com/jorgebucaran/fisher#installation    | The plugin manager for Fish. It is necessary for nvm.fish                                     |
| 5   | **nvm.fish**               | https://github.com/jorgebucaran/nvm.fish#installation  | The Node version manager for Fish. It reads the repository's `.nvmrc` (Node **24**)           |
| 6   | **Node 24**                | with nvm.fish (above) — https://nodejs.org             | The JavaScript runtime. Use version 24 only                                                   |
| 7   | **pnpm 11.9.0** (Corepack) | https://pnpm.io/installation                           | The package manager. Enable it with Corepack (included with Node). Do not install it globally |
| 8   | **GitHub CLI** (`gh`)      | https://cli.github.com                                 | Authenticates and clones the private repository (select SSH)                                  |
| 9   | **OrbStack**               | https://orbstack.dev                                   | Docker / Linux VMs on macOS — for local Postgres and other services later                     |
| 10  | **LazyGit**                | https://github.com/jesse-duffield/lazygit#installation | The terminal Git UI — the team default workflow                                               |

> The repository requires **pnpm 11.9.0** and **Node 24**. Install these exact versions (see the
> `packageManager` field and `.nvmrc`).

## Recommended (not required)

| Tool                                 | Install guide                                                          | Why                                                                               |
| ------------------------------------ | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **direnv**                           | https://direnv.net/docs/installation.html                              | Loads the environment variables of a repository (`.envrc`) automatically          |
| **ripgrep** (`rg`)                   | https://github.com/BurntSushi/ripgrep#installation                     | Fast code search                                                                  |
| **fd**                               | https://github.com/sharkdp/fd#installation                             | Fast file search                                                                  |
| **fff**                              | https://github.com/dmtrKovalenko/fff                                   | Frecency-ranked file/content search (git-status-boosted; faster than fzf/ripgrep) |
| **jq**                               | https://jqlang.github.io/jq/download/                                  | JSON on the CLI                                                                   |
| **eza** / **bat**                    | https://eza.rocks · https://github.com/sharkdp/bat#installation        | Better `ls` / `cat`                                                               |
| **oxc VS Code extension**            | https://marketplace.visualstudio.com/items?itemName=oxc.oxc-vscode     | oxlint/oxfmt in the editor (we do **not** use ESLint or Prettier)                 |
| **Expo Go / Xcode / Android Studio** | https://expo.dev/go · App Store · https://developer.android.com/studio | Run `sk-go` on a device or a simulator                                            |

---

When Node is on **24** and pnpm is on **11.9.0**, continue with [INSTALLATION.md](./INSTALLATION.md).
