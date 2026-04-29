# DoubleSlit_Simulator_V12.6
V12.6: Interactive double-slit simulation with temporal thread model, phase visualization (φ₁, φ₂, Δφ), Jönsson 1961 validation, CSV export, and white light RGB. Perfect for teaching quantum complementarity.
# Double‑Slit Simulator V12.6 – Temporal Thread Model

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/DoubleSlit_Simulator_V12.6/blob/main/DoubleSlit_Simulator_V12_6.ipynb)

**بالعربية**  
محاكاة تفاعلية لتجربة الشق المزدوج (إلكترون، فوتون، ضوء أبيض) مع نموذج **"الخيط الزمني"** (Temporal Thread). تُظهر المحاكاة كيف أن المراقبة (القياس) تقطع الترابط الطوري بين مساري الجسيم (`φ₁` و `φ₂`)، مما يفسر اختفاء نمط التداخل. تشمل واجهة بصرية لـ `φ₁, φ₂, Δφ` ومنحنى سلامة الخيط، مع تحقق من تجربة Jönsson 1961 وتصدير البيانات.

**English**  
Interactive double‑slit simulation (electrons, photons, white light) featuring the **Temporal Thread** model. Observation (measurement) cuts the phase correlation between the two paths (`φ₁` and `φ₂`), causing interference to vanish. Includes visual phase maps, thread integrity curve, Jönsson 1961 validation, and CSV export.

---

## ✨ Key Features | الميزات الرئيسية

- **Three modes** – Electron (de Broglie), monochromatic photon, white light (RGB mixing).
- **Temporal Thread model** – See how phase correlation between `φ₁` and `φ₂` degrades with measurement strength.
- **Phase visualisation** – Live plots of `φ₁`, `φ₂`, and `Δφ`.
- **Thread integrity curve** – Shows how the thread decays exponentially (`exp(-decay × strength)`).
- **Jönsson 1961 comparison** – Table compares simulated fringe spacing and first minimum with the famous electron experiment.
- **CSV export** – Save intensity data for further analysis.
- **Interactive sliders** – Control distance `L`, slit width (µm), slit separation (µm), velocity spread, temperature noise, decay rate, and random seed.
- **Available in Arabic & English** (interface in English, comments/philosophical notes in both).

---

## 🚀 Quick Start | التشغيل السريع

1. **Open in Google Colab** (recommended):  
   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/DoubleSlit_Simulator_V12.6/blob/main/DoubleSlit_Simulator_V12_6.ipynb)

2. **Or run locally** (Jupyter Notebook):
   ```bash
   pip install numpy matplotlib ipywidgets scipy pandas
   jupyter notebook DoubleSlit_Simulator_V12_6.ipynb
