# 30DayChartChallenge: Public Health & Health Economics 📊

This repository contains 30 reproducible data visualization scripts designed for the **#30DayChartChallenge**.

The visualizations feature a custom-built, unified beige-cream aesthetic architecture across both Python and R to create professional, presentation-ready infographics highlighting the performance of Bangladesh among global benchmarks.

## How to Run Python Scripts

1. **Create and Activate a Virtual Environment:**

   ```bash
   python -m venv .venv

   # For Windows:
   .venv\Scripts\activate
   # For macOS/Linux:
   source .venv/bin/activate
   ```
2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
3. **Generate the Charts:**
   Execute scripts for any day out of their respective folders. The script will automatically fetch the WHO dataset spreadsheet directly from Microsoft Azure if it does not already exist locally.

   ```bash
   python Day_1/day_1.py
   ```

## How to Run R Scripts

1. **Prerequisites:**
   Ensure `R` is installed on your computer.
2. **Run the Script:**
   Open any `.R` script in RStudio and run natively.

   ```R
   # Example manually running via Rscript engine
   Rscript Day_2/day_2.R
   ```
   *Note: The script is designed to elegantly set your working directory to its location dynamically using `rstudioapi`.*
