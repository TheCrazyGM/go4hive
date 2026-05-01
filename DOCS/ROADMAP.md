# Project Roadmap

## ✅ Sprint 1: The Foundation (COMPLETED)

- [x] Initialize `uv` project with Python 3.14+ / Django 6.x.
- [x] Scaffold Django application with `gopher` app.
- [x] Establish "Gopher-like" Terminal UI (CSS/ASCII Art).
- [x] Integrate `hive-nectar` SDK.
- [x] Implement robust Payout and Vote data extraction.
- [x] Core Views: Home, Trending, Hot, Post Details, User Profiles.
- [x] Basic Search functionality (@user and #tag).
- [x] CI/CD Ready: `prek` / `ruff` / Linting cleanup.

## ✅ Phase 3: Extended Exploration (COMPLETED)
- [x] **Block Explorer:** View latest raw blocks and transaction details.
- [x] **Witness Leaderboard:** See the top 20 witnesses and their status.
- [x] **Market Data:** Live HIVE/HBD prices and simple ticker.
- [x] **Tag Cloud:** A text-based "Gopher-hole" for browsing popular tags.
- [x] **Content Polishing:** Integrated `bleach` to strip messy HTML from blockchain posts.


## Phase 4: Performance & Polish

- [ ] **Caching Layer:** Implement Django caching to make page loads instantaneous.
- [ ] **ASCII Art Refinements:** More randomized terminal headers and ASCII dividers.
- [ ] **Mobile Responsive:** Ensuring the "Terminal" looks great on phone screens.
- [ ] **Custom Themes:** CSS toggles for Green/Amber/White CRT modes.

## Phase 5: Interaction (Future)

- [ ] Minimal HiveAuth/Keychain integration.
- [ ] Basic voting/commenting actions.
