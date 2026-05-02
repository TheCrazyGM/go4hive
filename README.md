# Go4Hive: A Gopher-like Interface for Hive

**Go4Hive** is a ultra-minimalist, text-centric frontend for the Hive blockchain. Inspired by the Gopher protocol and classic terminal interfaces, it provides a fast, distraction-free, and retro-styled experience for consuming Hive content.

---

## 📟 The Vision
"Returning Hive to its textual roots." Go4Hive strips away the heavy JavaScript, images, and complex layouts of modern social media, delivering content in a high-contrast, terminal-style interface.

### Core Principles
- **Content First:** Minimalist layout focused on readability.
- **Retro Aesthetic:** Multi-theme CRT styles with scanline effects and curated ASCII art.
- **High Performance:** Aggressive server-side caching and local-memory resolution.
- **Modern SDK:** Powered by `hive-nectar`, the superior successor to `beem`.

## 🛠 Tech Stack
- **Language:** Python 3.14+
- **Framework:** Django 6.x
- **SDK:** [hive-nectar](https://github.com/thecrazygm/hive-nectar)
- **Package Manager:** [uv](https://github.com/astral-sh/uv)
- **Frontend:** Vanilla CSS & Lightweight Vanilla JS (Universal Keyboard Navigation)

## ✨ Features
- **Global Feeds:** Browse Trending and Hot discussions.
- **Interactive Terminal:** 100% keyboard-navigable UI with a virtual terminal cursor.
- **Nano-style Terminal Editor:** A dedicated, full-screen environment for creating blockchain posts with 'Ctrl' hotkey support.
- **Custom CRT Themes:** Switch between Green, Amber, and White terminal modes.
- **Extended Exploration:**
    - **Block Explorer:** Inspect raw chain data and transaction details.
    - **Witness Leaderboard:** Live ranking of the top active Hive witnesses.
    - **Internal Market:** Real-time HIVE/HBD tickers from the internal DEX.
    - **Popular Tags:** Community-curated topics with automatic community name resolution.
- **Minimal Markdown Rendering:** Properly formatted text, lists, and blockquotes without the "raw" markdown clutter.
- **Image-to-Text Safety:** Automatically converts <img> tags into clickable `[IMAGE: URL]` links to preserve the terminal vibe.
- **Configurable Content Blacklist:** Admin-managed filtering to hide unwanted users and spam from all feeds and comments.
- **Content Polishing:** Integrated `bleach` to aggressively strip messy HTML for a pure text experience.
- **Smart Caching:** Near-instant page loads via Django local-memory cache.
- **Curated ASCII Branding:** Randomized high-quality headers powered by `figlet`.

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
uv run python manage.py runserver 8888
```
Visit `http://127.0.0.1:8888` in your browser.

## ⌨️ Keyboard Shortcuts
- **Arrow Up/Down:** Move virtual cursor between links.
- **Arrow Left/Right:** Navigate history (Back/Forward).
- **Enter:** Select/Open highlighted item.
- **1 - 8:** Quick-jump to Main Menu items.
- **'H' Key:** Instant return to Home.

## 🗺 Roadmap
- [x] Phase 1: The Foundation (Scaffolding & Terminal UI)
- [x] Phase 2: Browse Experience (Trending/Hot/Profiles)
- [x] Phase 3: Extended Exploration (Blocks/Witnesses/Market)
- [x] Phase 4: Performance & Polish (Caching/Themes/Mobile)
- [ ] Phase 5: Interactions (Voting/Commenting via Hive Keychain)

## 📜 License
This project is licensed under the MIT License.

## 🤝 Acknowledgments
- Co-Authored by [thecrazygm](https://github.com/thecrazygm) and Gemini CLI Agent.
- Built using the [hive-nectar](https://github.com/thecrazygm/hive-nectar) SDK.
- Inspired by the classic Gopher protocol and retro BBS systems.
