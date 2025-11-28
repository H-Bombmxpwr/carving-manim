# **Seam Carving (Manim Demo)**

A full visual walkthrough of **content-aware image resizing**, produced entirely in **Manim Community Edition**.

This project explains:

* Sobel filters and gradient-based “edginess”
* Energy maps for protecting important content
* Dynamic programming for minimum-energy seams
* Why naïve resizing approaches fail
* True seam carving in action
* A complete end-to-end animated explainer

---

## **Quick Start**

### **1. Create & activate the virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# or
.venv\Scripts\Activate.ps1     # Windows PowerShell
```

### **2. Install dependencies**

```bash
pip install -r requirements.txt
```

### **3. Ensure ffmpeg is installed**

Manim requires FFmpeg:

* macOS: `brew install ffmpeg`
* Windows: Chocolatey → `choco install ffmpeg`
* Linux: `sudo apt install ffmpeg`

---

# **Rendering Any Scene**

Below are one-click command snippets for **all scenes in order**.

> Each command renders at **quick, low-quality** settings (`-pqh`).

### **Title**

```bash
manim -pqh src/seamcarving_manim/scenes/s00_title.py TitleScene
```

### **Problem & Baselines**

```bash
manim -pqh src/seamcarving_manim/scenes/s10_problem_and_baselines.py BaselinesScene
```

### **Intro Demo**

```bash
manim -pqh src/seamcarving_manim/scenes/s15_intro_demo.py IntroDemoScene
```

### **Sobel Filters Intro**

```bash
manim -pqh src/seamcarving_manim/scenes/s17_sobel_intro.py SobelIntroScene
```

### **Energy Map**

```bash
manim -pqh src/seamcarving_manim/scenes/s20_energy_map.py EnergyMapScene
```

### **Edge Detection on Memory Image**

```bash
manim -pqh src/seamcarving_manim/scenes/s25_edge_on_memory.py EdgeOnMemoryScene
```

### **Dynamic Programming**

```bash
manim -pqh src/seamcarving_manim/scenes/s30_dynamic_programming.py DynamicProgrammingScene
```

### **Min Energy on Memory**

```bash
manim -pqh src/seamcarving_manim/scenes/s35_min_energy_memory.py MinEnergyMemoryScene
```

### **Dual Seam Carving (Original + Orange)**

```bash
manim -pqh src/seamcarving_manim/scenes/s40_purple_seam_demo.py DualSeamCarvingScene
```

### **Failure Modes**

```bash
manim -pqh src/seamcarving_manim/scenes/s45_failure_modes.py FailureModesScene
```

### **Final Credits**

```bash
manim -pqh src/seamcarving_manim/scenes/s50_final_scene.py FinalCreditsScene
```

---

# **Project Structure**

Fully matching your screenshot layout:

```
carving-manim/
│
├── media/                      # Manim output (gitignored)
│
├── src/
│   └── seamcarving_manim/
│       ├── __init__.py
│       │
│       ├── scenes/
│       │   ├── s00_title.py
│       │   ├── s10_problem_and_baselines.py
│       │   ├── s15_intro_demo.py
│       │   ├── s17_sobel_intro.py
│       │   ├── s20_energy_map.py
│       │   ├── s25_edge_on_memory.py
│       │   ├── s30_dynamic_programming.py
│       │   ├── s35_min_energy_memory.py
│       │   ├── s40_purple_seam_demo.py
│       │   ├── s45_failure_modes.py
│       │   └── s50_final_scene.py
│       │
│       ├── utils/
│       │   ├── energy.py
│       │   ├── sobel.py
│       │   └── dp.py
│       │
│       └── assets/
│           └── images/
│               ├── memory.jpg
│               ├── memory_edges/
│               │   └── memory_edge_mag.png
│               ├── memory_dual/
│               │   ├── orig/frame_*.png
│               │   └── dp/frame_*.png
│               ├── failure_modes/
│               │   ├── column/frame_*.png
│               │   ├── pixel/frame_*.png
│               │   ├── optimal/frame_*.png
│               │   └── seam/frame_*.png
│               └── final_scene/
│                   ├── mit.png
│                   ├── paper.png
│                   ├── python.png
│                   └── wikipedia.png
│
├── requirements.txt
└── README.md
```

---

# **References**

Here are all the sources used in this project, in the order they informed the animations:

### **1. MIT – Intro to Computational Thinking**

Core explanations of energy maps and DP
🔗 [https://computationalthinking.mit.edu/Fall20/](https://computationalthinking.mit.edu/Fall20/)

### **2. Original Seam Carving Paper (ACM)**

By Shai Avidan & Ariel Shamir (2007)
🔗 [https://dl.acm.org/doi/pdf/10.1145/1275808.1276390](https://dl.acm.org/doi/pdf/10.1145/1275808.1276390)

### **3. Python Seam-Carving Package**

Simple reference implementation
🔗 [https://pypi.org/project/seam-carving/](https://pypi.org/project/seam-carving/)

### **4. Wikipedia – Seam Carving**

General algorithm background
🔗 [https://en.wikipedia.org/wiki/Seam_carving](https://en.wikipedia.org/wiki/Seam_carving)
