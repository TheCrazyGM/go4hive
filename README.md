# Go4Hive: A Gopher-like Interface for Hive

**Go4Hive** is a ultra-minimalist, text-centric frontend for the Hive blockchain. Inspired by the Gopher protocol and classic terminal interfaces, it provides a fast, distraction-free, and retro-styled experience for consuming Hive content.

![Go4Hive Logo](https://raw.githubusercontent.com/thecrazygm/go4hive/main/static/gopher/images/logo_placeholder.png) *(Placeholder for future ASCII logo or screenshot)*

## 📟 The Vision
"Returning Hive to its textual roots." Go4Hive strips away the heavy JavaScript, images, and complex layouts of modern social media, delivering content in a high-contrast, terminal-style interface.

### Core Principles
- **Content First:** Minimalist layout focused on readability.
- **Retro Aesthetic:** Green-on-black terminal theme with scanline effects and ASCII art.
- **Speed:** Server-side rendered for near-instant load times.
- **Modern SDK:** Powered by `hive-nectar`, the successor to `beem`.

## 🛠 Tech Stack
- **Language:** Python 3.14+
- **Framework:** Django 6.x
- **SDK:** [hive-nectar](https://github.com/thecrazygm/hive-nectar)
- **Package Manager:** [uv](https://github.com/astral-sh/uv)
- **Frontend:** Vanilla CSS (Terminal Theme)

## ✨ Features
- **Global Feeds:** Browse Trending and Hot discussions.
- **Numbered Navigation:** Gopher-inspired numbered menus for easy keyboard navigation.
- **Post Viewer:** Deep-dive into posts with nested comment rendering.
- **User Profiles:** Look up `@user` profiles, reputation, and blog history.
- **Tag Search:** Filter the blockchain via `#tags`.
- **ASCII Branding:** Authentic retro headers and footers.

## 🚀 Getting Started

### Prerequisites
- [uv](https://github.com/astral-sh/uv) installed on your system.
- Python 3.14 (or compatible version).

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/thecrazygm/go4hive.git
   cd go4hive
   ```
2. Initialize the environment and install dependencies:
   ```bash
   uv sync
   ```
3. Run initial migrations:
   ```bash
   uv run python manage.py migrate
   ```

### Running the App
Start the development server:
```bash
uv run python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your browser.

## 🗺 Roadmap
- [x] Phase 0: Project Scaffolding & Visual Foundation
- [x] Phase 1: Browse Experience (Trending/Hot/Post View)
- [x] Phase 2: Identity & Search (Profiles/Tag Search)
- [ ] Phase 3: Interactions (Voting/Commenting via Hive Keychain)
- [ ] Phase 4: Block Explorer & Polish

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Acknowledgments
- Built by [thecrazygm](https://github.com/thecrazygm) using the [hive-nectar](https://github.com/thecrazygm/hive-nectar) SDK.
- Inspired by the classic Gopher protocol.
