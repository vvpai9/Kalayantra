# Kālayantra (कालयन्त्र)

Kālayantra is a native KDE Plasma 6 widget and offline Panchanga (Hindu Calendar) that brings precise Hindu astronomical calculations directly to your desktop.

<img width="303" height="43" alt="Screenshot_20260626_093019" src="https://github.com/user-attachments/assets/63e6a0cd-0e1f-483d-8b98-ea5a1e14972e" />

<img width="1253" height="872" alt="Screenshot_20260626_093050" src="https://github.com/user-attachments/assets/0d7e535f-6ca6-4898-9cdc-75e54f44d65c" />

<img width="1022" height="817" alt="Screenshot_20260626_093122" src="https://github.com/user-attachments/assets/3c2cfeb4-cee1-4b17-9a19-7789cbb45e97" />

## Features

- **Precise Lunisolar Astronomical Engine:** Powered by the local **Kālachakra** backend calculations engine using the Swiss Ephemeris (`pyswisseph`).
- **Modern Kirigami Interface:** Fully native Plasma 6 integration with beautiful, responsive layouts.
- **Swipe Transitions:** Smooth monthly calendar navigation with slide/swipe animations.
- **Detailed Panchanga Elements:**
  - Tithi, Vaara, Nakshatra, Yoga, Karana (along with their exact transit end times)
  - Ritu (6 seasons) and Ayana (Uttarayana/Dakshinayana)
  - Year counts for Shalivahana Shaka, Vikram Samvat, and Kali Yuga
  - Samvatsara (60-year Jovian cycle name, dynamically calculated for the chosen era)
- **High-Precision Ghadi/Vipal Clock:** Microsecond UTC calculations for accurate Ghadi and Vipal tracking.
- **Auspicious & Inauspicious Times:**
  - Rahu Kala (🔴 inauspicious), Yamaghanta (🔴 inauspicious), Gulika (🟡 moderate), and Abhijit Muhurta (🟢 auspicious)
  - **Brahma Muhurta** calculation and display
  - **Choghadiya Muhurtas** (both Daytime and Nighttime segments color-coded: 🟢 Auspicious, 🟡 Neutral, 🔴 Inauspicious)
- **Vedic Transition Formatting:** Times falling after local midnight but before the next day's sunrise are formatted using the 24+h style (e.g., 27:07) to avoid Gregorian date confusion.
- **Daily Sun/Moon Events:** Accurate calculations for Sunrise, Sunset, Moonrise, and Moonset based on coordinates.
- **Festivals & Sankrantis:** Dynamic calculation of all 12 Rashi Sankrantis, monthly Sankashti Chaturthi, and major lunisolar festivals with localized multi-language translations.
- **Customized Calendar Views:**
  - Select between Shalivahana Shaka, Vikram Samvat (Chaitradi), and Vikram Kartak (Kartikadi) calendar systems.
  - Choose Amavasyanta (default) or Purnimanta month systems.
  - Select Smarta or Vaishnava festival rules (affecting Ekadashi determination).
  - Clear visual distinction between Shukla Paksha (golden theme, waxing moon) and Krishna Paksha (slate theme, waning moon).
- **Multi-language Support:** Choose display language from English, IAST (Sanskrit transliteration), and Devanagari.
- **Reactive Settings Synchronization:** Fully functional configuration panel with bidirectional bindings that propagate settings to the backend instantly.
- **Offline & Privacy-Respecting:** Spawns no cloud connections; all calculations run 100% locally.

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
2. Configure a systemd user service (`kalachakra.service`) to run the Python **Kālachakra** calculations engine on port `8642`.
3. Enable and start the background service.

## License

GPL-3.0 License.
