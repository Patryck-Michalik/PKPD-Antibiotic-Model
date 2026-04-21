## Getting Started

### 1. Download the Repository

You can download the project in one of two ways:

Open a terminal:

- **Mac/Linux:** Open *Terminal*  

- **Windows:** Open *Command Prompt* or *PowerShell*  

Then run:

```bash

git clone https://github.com/Patryck-Michalik/PKPD-Antibiotic-Model.git

cd PKPD-Antibiotic-Model

```

---

**Option B: Without Git**

- Click the green **Code** button on the GitHub page  

- Select **Download ZIP**  

- Extract the folder  

- Open a terminal in the extracted folder  

---

### 2. Install Requirements

Install all required Python packages:

```bash

pip install -r requirements.txt

```

If you do not have Python or pip installed, install Python (3.9 or newer) from:  

https://www.python.org/downloads/

---

### 3. Launch Jupyter Notebook

From inside the project folder, run:

```bash

jupyter notebook

```

This will open Jupyter in your browser.

---

### 4. Run the Example Notebook

Open:

```text

notebooks/pkpd_exploration.ipynb

```

This notebook demonstrates how to:

- run PK/PD simulations  

- perform parameter sweeps  

- generate figures  

---

## Using the Model in Your Own Code

Core model functionality is defined in:

```text

src/pkpd_model.py

```

To use it in your own notebook:

```python

import sys

import os

# Allow Python to find the src folder

sys.path.append(os.path.abspath(".."))

from src.pkpd_model import (

    create_params,

    create_sim_settings,

    run_simulation,

    run_param_sweep,

    run_sim_setting_sweep,

)

# Example usage

params = create_params()

sim_settings = create_sim_settings()

t, C, B = run_simulation(params=params, sim_settings=sim_settings)

```

---

## Requirements

Dependencies are listed in `requirements.txt`. The main packages used are:

- numpy  

- scipy  

- pandas  

- matplotlib  

- openpyxl  

- jupyter  

Install them with:

```bash

pip install -r requirements.txt

```

---
