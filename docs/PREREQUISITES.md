# Prerequisites

Developer tools every Sankit contributor installs **before** cloning the repo. Targets
**macOS** (the team standard). Follow each tool's official install guide — links below.

> Install order matters: **Homebrew first**, then **Fish → Fisher → nvm.fish**. After this doc,
> follow [INSTALLATION.md](./INSTALLATION.md) to set up the repo itself.

## Required

| # | Tool | Install guide | Why |
| --- | --- | --- | --- |
| 1 | **Homebrew** | https://brew.sh | The macOS package manager everything else installs through |
| 2 | **Ghostty** | https://ghostty.org/docs/install | Team reference terminal (GPU-accelerated) |
| 3 | **Fish shell** | https://fishshell.com | The team shell; repo tooling assumes it. Set it as your login shell |
| 4 | **Fisher** | https://github.com/jorgebucaran/fisher#installation | Fish plugin manager (needed for nvm.fish) |
| 5 | **nvm.fish** | https://github.com/jorgebucaran/nvm.fish#installation | Fish-native Node version manager; reads the repo's `.nvmrc` (Node **24**) |
| 6 | **Node 24** | via nvm.fish (above) — https://nodejs.org | JavaScript runtime; pin to 24 |
| 7 | **pnpm 11.9.0** (Corepack) | https://pnpm.io/installation | Package manager. Enable via Corepack (ships with Node) rather than a global install |
| 8 | **GitHub CLI** (`gh`) | https://cli.github.com | Auth + clone the private repo (choose SSH) |
| 9 | **OrbStack** | https://orbstack.dev | Docker / Linux VMs on macOS — local Postgres & backing services later |
| 10 | **LazyGit** | https://github.com/jesse-duffield/lazygit#installation | Terminal Git UI — team default workflow |

> The repo pins **pnpm 11.9.0** and **Node 24** — match those exact versions (see the
> `packageManager` field and `.nvmrc`).

## Recommended (not required)

| Tool | Install guide | Why |
| --- | --- | --- |
| **direnv** | https://direnv.net/docs/installation.html | Per-repo env vars (`.envrc`) auto-load |
| **ripgrep** (`rg`) | https://github.com/BurntSushi/ripgrep#installation | Fast code search |
| **fd** | https://github.com/sharkdp/fd#installation | Fast file find |
| **fff** | https://github.com/dmtrKovalenko/fff | Frecency-ranked file/content search (git-status-boosted; faster than fzf/ripgrep) |
| **jq** | https://jqlang.github.io/jq/download/ | JSON on the CLI |
| **eza** / **bat** | https://eza.rocks · https://github.com/sharkdp/bat#installation | Better `ls` / `cat` |
| **oxc VS Code extension** | https://marketplace.visualstudio.com/items?itemName=oxc.oxc-vscode | oxlint/oxfmt in-editor (we do **not** use ESLint/Prettier) |
| **Expo Go / Xcode / Android Studio** | https://expo.dev/go · App Store · https://developer.android.com/studio | Run `sk-go` on device/simulator |

---

Once Node is on **24** and pnpm on **11.9.0**, you're ready for [INSTALLATION.md](./INSTALLATION.md).
