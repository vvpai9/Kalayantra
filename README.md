# Kālayantra (कालयन्त्र)

Kālayantra is a native KDE Plasma 6 widget and offline Panchanga (Hindu Calendar) that brings precise Hindu astronomical calculations directly to your desktop.

## Architecture (v2.0 Upgrade)

Kālayantra is built with a strictly decoupled modular design following separation of concerns:

- **Kalayantra**: The panel widget wrapper for KDE Plasma 6.
- **Kalachakra**: The core Panchanga and astronomical calculation engine.
- **Kalotsavachakra**: The traditional Dharmaśāstra festival & ritual calculation engine.
- **Kalasetu**: The backend bridge / local API service daemon. Manages memory-based caching, custom city registrations and My Tithis.
- **Kaladarshana**: The native user interface (UI) built using QML, Kirigami and QtQuick.
- **Kalakosha**: The static knowledge base (metadata, coordinates, translations).

## Features

- **Precise Lunisolar Astronomical Engine:** Powered by the local **Kalachakra** backend using the Swiss Ephemeris.
- **Traditional & Astronomical Modes:**
  - *Traditional Mode:* Panchanga elements are computed at sunrise. If an element survives past the next sunrise, only that element is shown. Otherwise, elements are shown side-by-side. (The panel widget displays the sunrise tithi and the info panel highlights the active one).
  - *Astronomical Mode:* Displays real-time elements, transitions and active highlighting.
- **Card-Based Kirigami Settings pages:** Restructured all settings interfaces using standard `Kirigami.Card` layout sheets matching native Plasma System Settings guidelines. Features subtitles and Breeze icons:
  - *General Settings:* Coordinates manual edits and searchable offline registry database.
  - *Calendar Settings:* System settings grouping (Era, Month system, ritual rules, and tithi mode).
  - *My Tithis:* Observances creator and dynamic anniversary lists cards.
  - *Reminders:* Repeating notifications creator and toggles lists cards.
  - *About Section:* Dynamic about panel fetching logo, license, authors, and system architecture.
- **Saura Solar Calendar System:** Choose `Solar Calendar (Saura)` under era systems to automatically compute traditional solar months (`Mesha` to `Mina`) based on zodiac entries (`sun_rashi`) and track solar Shaka era years.
- **Surya/Rain Nakshatra Display:** Computes high-precision Sun Nakshatras. If the Sun transitions during the day, display transitions in the side panel (e.g., `👉 Rohini 14:38 • Mrigashira`), dynamically highlighting the active sign in English, IAST, and Devanagari.
- **Editable Gregorian Date with 'Today' Shortcut:** Click the Gregorian Date sub-header in the side panel to toggle a text input accepting `DD-MM-YYYY` with real-time `Kirigami.InlineMessage` error validation, support for both alphanumeric & numpad Enter keys, and a "Today" button to return to current local time instantly.
- **Robust Navigation Lifecycle:** Navigation states are preserved while the popup is open, preventing background refreshes from resetting the view, and automatically discarded upon closing so that the popup starts on today's month next time it is opened.
- **Dynamic Hindu Month Navigation:** Navigation headers track Hindu lunar months (e.g. `Jyeshtha Masa`) and years (e.g. `Shaka 1948`) as primary labels.
- **Offline City Directory & Search:** Includes a package database of 100+ cities. Allows adding and caching custom cities.
- **My Tithis & Anniversary Support:** CRUD support via the settings panel to schedule recurring traditional lunar events (e.g. Janmadin), with birth/event year option to calculate and display the current anniversary (e.g. `21st Janmadin` or `3rd Anniversary`), with built-in **Import and Export** to local JSON files.
- **Lunar Recurring Reminders:** Configure desktop notifications via D-Bus for recurring reminders matched against Hindu Panchanga parameters (Tithis, Paksha + Tithi, Masa + Paksha + Tithi, Nakshatras, Varas + Tithis, Sankrantis, and custom Festivals) at dynamic time-targets (Brahma Muhurta, Sunrise, Offset before sunrise, or Exact time). Includes Import/Export and persistent notification caching.
- **Dynamic Color-Coded Calendar:** Larger indicator dots positioned at the top-right corner of day cells, colored dynamically based on the day's primary festival type and sorted by event hierarchy:
  - 🔵 **Ekadashis** (Blue)
  - 🟠 **Sankrantis** (Orange)
  - 🟣 **Sankashti Chaturthis** (Purple)
  - 💗 **My Tithis** (Pink)
  - 🟢 **Major Festivals/Vratas** (Green)
- **Vedic Transition Formatting:** Events occurring after midnight are denoted using 24+h style relative to today's start date (e.g. `31:39` or `40:05`), displaying transitions accurately across day boundaries.
- **Panel Tooltip Enhancements:** Hovering over the tray widget displays Sunrise, Sunset, Moonrise, Moonset, Ghadi:Vipal time, Nakshatra, Yoga, Karana and Current Festival, formatted in clean sections.
- **Auspicious & Inauspicious Times:**
  - Rahu Kala (🔴 inauspicious), Yamaghanta (🔴 inauspicious), Gulika (🟡 moderate) and Abhijit Muhurta (🟢 auspicious).
  - Brahma Muhurta calculation and display.
  - Choghadiya Muhurtas (color-coded daytime and nighttime segments).
- **Details Panel Live Highlights:** The details panel (Tithi, Nakshatra, Yoga, Karana) always shows transitions and highlights the currently active element with a `👉` indicator and greyed-out past elements under both traditional and astronomical modes.
- **Live Ghadi-Vipal Clock:** High-precision real-time display of local Vedic time (Ghadis & Vipals).
- **Multi-language Support:** Choose display language from English, IAST and Devanagari.
- **Offline & Privacy-Respecting:** Spawns no cloud connections; all calculations run 100% locally.

## Screenshots

### Panel Widget

![Panel Widget](screenshots/widget.png)

### Calendar Popup

![Calendar Popup](screenshots/popup.png)

### Settings

![Settings](screenshots/settings.png)

![Custom Observances](screenshots/custom.png)

## Installation

### Dependencies

Ensure you have python3 and the Swiss Ephemeris package installed on your system:

- **Arch Linux:** `sudo pacman -S python-pyswisseph` or install via pip: `pip3 install pyswisseph`
- **Fedora:** `sudo dnf install python3-pyswisseph` or `pip3 install pyswisseph`
- **Ubuntu/KDE Neon/Kubuntu:** `pip3 install pyswisseph`

### Clone the repository

```bash
git clone https://github.com/vvpai9/Kalayantra.git
cd Kalayantra
```

### Install script

Run the automated installer script:

```bash
chmod +x install.sh
./install.sh
```

This will:
1. Register and install the Plasmoid package using `kpackagetool6`.
2. Configure a systemd user service (`kalachakra.service`) to run the Python **Kalasetu** API bridge on port `8642`.
3. Enable and start the background service.

## License

GPL-3.0 License.
