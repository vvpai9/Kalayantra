# Kālayantra (कालयन्त्र)

Kālayantra is a native KDE Plasma 6 widget and offline Panchanga (Hindu Calendar) that brings precise Hindu astronomical calculations directly to your desktop.

## Features

- **Precise Lunisolar Astronomical Engine:** Powered by Swiss Ephemeris (`pyswisseph`) running locally.
- **Modern Kirigami Interface:** Fully native Plasma 6 integration with beautiful, responsive horizontal and vertical layouts.
- **Detailed Panchanga Elements:**
  - Tithi, Vaara, Nakshatra, Yoga, Karana
  - Ritu (6 seasons) and Ayana (Uttarayana/Dakshinayana)
  - Year counts for Shalivahana Shaka, Vikram Samvat, and Kali Yuga
  - Samvatsara (60-year Jovian cycle name)
- **Auspicious & Inauspicious Times:**
  - Rahu Kala, Yamaganda, Gulika, and Abhijit Muhurta
- **Daily Sun/Moon Events:** Accurate calculations for Sunrise, Sunset, Moonrise, and Moonset based on coordinates.
- **Customized Calendar Views:**
  - Select between Shalivahana Shaka, Vikram Samvat (Chaitradi), and Vikram Kartak (Kartikadi) calendar systems.
  - Choose Amavasyanta (default) or Purnimanta month systems.
  - Select Smarta or Vaishnava festival rules (affecting Ekadashi determination).
  - Clear visual distinction between Shukla Paksha (golden theme, waxing moon) and Krishna Paksha (slate theme, waning moon).
- **Multi-language Support:** Choose display language from English, IAST (Sanskrit transliteration), and Devanagari.
- **Offline & Privacy-Respecting:** Spawns no cloud connections; all calculations run 100% locally.

## Installation

### Dependencies

Ensure you have python3 and the Swiss Ephemeris package installed on your system:

- **Arch Linux:** `sudo pacman -S python-pyswisseph` or install via pip: `pip3 install pyswisseph`
- **Fedora:** `sudo dnf install python3-pyswisseph` or `pip3 install pyswisseph`
- **Ubuntu/KNeon/Kubuntu:** `pip3 install pyswisseph`

### Install script

Run the automated installer script:

```bash
chmod +x install.sh
./install.sh
```

This will:
1. Register and install the Plasmoid package using `kpackagetool6`.
2. Configure a systemd user service (`kalayantra-backend.service`) to run the Python calculations engine on port `8642`.
3. Enable and start the background service.

## License

GPL-3.0 License.
