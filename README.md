# 30DayChartChallenge: Public Health & Health Economics 📊

Charts for the **#30DayChartChallenge**, written in both Python and R where possible.

Most charts share the same beige-cream style and show where Bangladesh sits against other countries.

## Charts So Far

| Day | Folder | Topic | Data source | Scripts |
|-----|--------|-------|-------------|---------|
| 1 | `Day_1` | The cost of care: out-of-pocket spending vs UHC coverage | WHO World Health Statistics 2022 | Python, R |
| 2 | `Day_2` | Life expectancy vs healthy life expectancy | WHO World Health Statistics 2022 | Python, R |
| 3 | `Day_3` | Childhood malnutrition among under-5s | WHO World Health Statistics 2022 | Python, R |
| 4 | `Day_4` | Healthcare workforce gap: doctors vs nurses | WHO World Health Statistics 2022 | Python, R |
| 5 | `Day_5` | Global tuberculosis incidence map | WHO World Health Statistics 2022 | Python, R |
| 6 | `Day_6` | Do carnivores sleep more? Mammal sleep by diet | ggplot2 built-in `msleep` dataset | R |
| 7 | `Day_7` | The story of measles in Bangladesh: vaccine coverage vs outbreaks (3 versions) | WHO measles cases and vaccine coverage | Python, R |
| 8 | `Day_8` | Sugar-sweetened beverage intake by world region (circular) | Global Dietary Database 2018 | Python, R |
| 9 | `Day_9` | Regional wealth fingerprints and Bangladesh in context | World Inequality Database (WID) | Python |

## Data

You don't need to download anything by hand. Each day either fetches its data or ships it in the folder:

- **Days 1–5:** the scripts download the WHO World Health Statistics 2022 spreadsheet the first time they run and save it next to the script. The Day 4 and Day 5 R scripts do not download it, so run the Python script for that day first (or copy the spreadsheet into the folder).
- **Day 6:** uses a dataset that comes with ggplot2.
- **Day 7:** the two Excel files are included in the folder.
- **Day 8:** the dataset is included as `sugar_intake_country_wise_2018.csv.gz` (compressed to stay under GitHub's file size limit). pandas and readr read it directly, so there's no need to unzip it.
- **Day 9:** the script tries to download the WID export first and falls back to the included `WID_Data_10042026-163159.xlsx`.

## How to Run Python Scripts

1. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv

   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
3. **Run a script:**

   ```bash
   python Day_1/day_1.py
   ```

   The Day 7 scripts look for their Excel files in the current folder, so run them from inside `Day_7`.

## How to Run R Scripts

1. **Install R** and the packages the scripts use:

   ```R
   install.packages(c("tidyverse", "readxl", "ggrepel", "ggtext", "patchwork",
                      "scales", "sf", "rnaturalearth", "rstudioapi"))
   ```
2. **Run a script** in RStudio, or from the terminal:

   ```bash
   Rscript Day_2/day_2.R
   ```

   The Day 1–6 scripts use `rstudioapi` to set the working directory to the script's own folder. For the other days, run the script from inside its folder so it can find the data files.
