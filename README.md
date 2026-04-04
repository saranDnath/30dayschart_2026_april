# 30DayChartChallenge: Public Health & Health Economics 📊

This repository contains five reproducible data visualization scripts designed for the **#30DayChartChallenge**. It leverages the global **WHO World Health Statistics 2022** open dataset to explore health economics, quality of care, maternal mortality, workforce gaps, and childhood malnutrition. 

The visualizations feature a custom-built, unified beige-cream aesthetic architecture across both Python and R to create professional, presentation-ready infographics highlighting the performance of Bangladesh among global benchmarks.

## Visual Design Architecture

The project drops standard boilerplate themes in favor of natively styling matplotlib and ggplot2:
* **Background & Frame:** A cream (`#F7F3EE`) canvas with muted beige (`#E0D9D0`) gridlines.
* **Palette:**
  * Background countries: soft gray (`#C8BFB5`)
  * Highlighted countries: dark navy dot (`#2C6FA6`), bold text (`#1A3D5C`)
  * Bangladesh: dominant red dot (`#D62828`) with glowing radius, bold green text (`#006A4E`)
* **Layering & Offsets:** Labels are deliberately placed across all layers with a white glowing path-effect to absolutely minimize overlapping.

## Visualizations Built
* **Day 1:** The cost of care: OOP Expenditure vs UHC
* **Day 2:** Quality of Life Gap: Life Expectancy vs Healthy Life Expectancy
* **Day 3:** Maternal Mortality vs Skilled Birth Attendance
* **Day 4:** Health Workforce: Doctors vs Nurses Density
* **Day 5:** Childhood Malnutrition: Wasting vs Stunting (% Under-5s) Diverging Bar Chart

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
