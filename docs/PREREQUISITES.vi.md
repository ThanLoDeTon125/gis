# Prerequisites

Tài liệu này liệt kê các developer tool mà bạn phải cài trước khi clone repository. Hướng dẫn
nhắm tới **macOS**, chuẩn chung của team. Làm theo guide cài đặt chính thức của từng tool. Link ở
các bảng bên dưới.

> Thứ tự cài đặt quan trọng: cài **Homebrew** trước, rồi tới **Fish → Fisher → nvm.fish**. Sau khi
> hoàn thành tài liệu này, làm theo [INSTALLATION.vi.md](./INSTALLATION.vi.md) để set up
> repository.

## Bắt buộc

| #   | Tool                       | Guide cài đặt                                          | Để làm gì                                                                         |
| --- | -------------------------- | ------------------------------------------------------ | --------------------------------------------------------------------------------- |
| 1   | **Homebrew**               | https://brew.sh                                        | Package manager của macOS. Bạn cài mọi tool còn lại qua nó                        |
| 2   | **Ghostty**                | https://ghostty.org/docs/install                       | Terminal chuẩn của team (GPU-accelerated)                                         |
| 3   | **Fish shell**             | https://fishshell.com                                  | Shell của team. Tooling trong repository mặc định dùng nó. Set nó làm login shell |
| 4   | **Fisher**                 | https://github.com/jorgebucaran/fisher#installation    | Plugin manager cho Fish. Cần nó để cài nvm.fish                                   |
| 5   | **nvm.fish**               | https://github.com/jorgebucaran/nvm.fish#installation  | Node version manager cho Fish. Nó đọc `.nvmrc` của repository (Node **24**)       |
| 6   | **Node 24**                | qua nvm.fish (ở trên) — https://nodejs.org             | Runtime JavaScript. Chỉ dùng phiên bản 24                                         |
| 7   | **pnpm 11.9.0** (Corepack) | https://pnpm.io/installation                           | Package manager. Bật nó bằng Corepack (đi kèm Node). Không cài global             |
| 8   | **GitHub CLI** (`gh`)      | https://cli.github.com                                 | Đăng nhập và clone private repository (chọn SSH)                                  |
| 9   | **OrbStack**               | https://orbstack.dev                                   | Docker / Linux VM trên macOS — cho Postgres local và các service khác sau này     |
| 10  | **LazyGit**                | https://github.com/jesse-duffield/lazygit#installation | Git UI trên terminal — workflow mặc định của team                                 |

> Repository yêu cầu **pnpm 11.9.0** và **Node 24**. Cài đúng hai phiên bản này (xem field
> `packageManager` và file `.nvmrc`).

## Nên có (không bắt buộc)

| Tool                                 | Guide cài đặt                                                          | Để làm gì                                                                          |
| ------------------------------------ | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **direnv**                           | https://direnv.net/docs/installation.html                              | Tự động load env var của repository (`.envrc`)                                     |
| **ripgrep** (`rg`)                   | https://github.com/BurntSushi/ripgrep#installation                     | Search code nhanh                                                                  |
| **fd**                               | https://github.com/sharkdp/fd#installation                             | Tìm file nhanh                                                                     |
| **fff**                              | https://github.com/dmtrKovalenko/fff                                   | Search file/nội dung theo frecency (ưu tiên file git-dirty; nhanh hơn fzf/ripgrep) |
| **jq**                               | https://jqlang.github.io/jq/download/                                  | Xử lý JSON trên CLI                                                                |
| **eza** / **bat**                    | https://eza.rocks · https://github.com/sharkdp/bat#installation        | Bản `ls` / `cat` tốt hơn                                                           |
| **oxc VS Code extension**            | https://marketplace.visualstudio.com/items?itemName=oxc.oxc-vscode     | oxlint/oxfmt trong editor (team **không** dùng ESLint hoặc Prettier)               |
| **Expo Go / Xcode / Android Studio** | https://expo.dev/go · App Store · https://developer.android.com/studio | Chạy `sk-go` trên device hoặc simulator                                            |

---

Khi Node ở **24** và pnpm ở **11.9.0**, tiếp tục với [INSTALLATION.vi.md](./INSTALLATION.vi.md).
