# Prerequisites

Các tool mà mọi dev Sankit cần cài **trước khi** clone repo. Doc này nhắm tới **macOS** (chuẩn
chung của team). Cứ theo guide chính thức của từng tool — link ở bên dưới.

> Thứ tự cài quan trọng: **Homebrew trước**, rồi tới **Fish → Fisher → nvm.fish**. Cài xong doc
> này thì qua [INSTALLATION.vi.md](./INSTALLATION.vi.md) để set up repo.

## Bắt buộc

| # | Tool | Guide cài đặt | Để làm gì |
| --- | --- | --- | --- |
| 1 | **Homebrew** | https://brew.sh | Package manager của macOS, mọi thứ còn lại cài qua nó |
| 2 | **Ghostty** | https://ghostty.org/docs/install | Terminal chuẩn của team (GPU-accelerated) |
| 3 | **Fish shell** | https://fishshell.com | Shell của team; tooling trong repo mặc định là Fish. Nhớ set làm login shell |
| 4 | **Fisher** | https://github.com/jorgebucaran/fisher#installation | Plugin manager cho Fish (cần để cài nvm.fish) |
| 5 | **nvm.fish** | https://github.com/jorgebucaran/nvm.fish#installation | Node version manager native cho Fish; tự đọc `.nvmrc` của repo (Node **24**) |
| 6 | **Node 24** | cài qua nvm.fish (ở trên) — https://nodejs.org | Runtime JavaScript; pin về đúng bản 24 |
| 7 | **pnpm 11.9.0** (Corepack) | https://pnpm.io/installation | Package manager. Bật qua Corepack (đi kèm Node) thay vì cài global |
| 8 | **GitHub CLI** (`gh`) | https://cli.github.com | Auth + clone private repo (chọn SSH) |
| 9 | **OrbStack** | https://orbstack.dev | Docker / Linux VM trên macOS — sau này chạy Postgres và các service local |
| 10 | **LazyGit** | https://github.com/jesse-duffield/lazygit#installation | Git UI trên terminal — workflow mặc định của team |

> Repo pin cứng **pnpm 11.9.0** và **Node 24** — cài đúng hai bản này (xem field
> `packageManager` và file `.nvmrc`).

## Nên có (không bắt buộc)

| Tool | Guide cài đặt | Để làm gì |
| --- | --- | --- |
| **direnv** | https://direnv.net/docs/installation.html | Tự load env var theo repo (`.envrc`) |
| **ripgrep** (`rg`) | https://github.com/BurntSushi/ripgrep#installation | Search code nhanh |
| **fd** | https://github.com/sharkdp/fd#installation | Tìm file nhanh |
| **fff** | https://github.com/dmtrKovalenko/fff | Search file/nội dung theo frecency (ưu tiên file git-dirty; nhanh hơn fzf/ripgrep) |
| **jq** | https://jqlang.github.io/jq/download/ | Xử lý JSON trên CLI |
| **eza** / **bat** | https://eza.rocks · https://github.com/sharkdp/bat#installation | Bản `ls` / `cat` xịn hơn |
| **oxc VS Code extension** | https://marketplace.visualstudio.com/items?itemName=oxc.oxc-vscode | oxlint/oxfmt ngay trong editor (team **không** dùng ESLint/Prettier) |
| **Expo Go / Xcode / Android Studio** | https://expo.dev/go · App Store · https://developer.android.com/studio | Chạy `sk-go` trên device/simulator |

---

Khi Node đã ở **24** và pnpm ở **11.9.0** là bạn sẵn sàng qua [INSTALLATION.vi.md](./INSTALLATION.vi.md).
