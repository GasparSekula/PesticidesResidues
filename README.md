# 🥛🐄 Pesticide Residues in Dairy Products (Milk & Butter)

This repository contains **data transformation, statistical analysis, and visualization** of pesticide residues in dairy products.  
The project is part of **Justyna Para's PhD research** at Wroclaw University of Environmental and Life Sciences.

Scientific support: Justyna Para and Prof. Anna Zielak-Steciwko from  Wroclaw University of Environmental and Life Sciences.

---

## 📌 Introduction

Food safety is one of the most important public health concerns. Dairy products such as **milk** and **butter** are widely consumed across Europe, making them critical commodities for pesticide residue monitoring.  

This repository explores **European Food Safety Authority (EFSA) monitoring data** and addresses multiple hypotheses related to pesticide contamination, frequency of detections, exceedances, and trends over time.

---

## 🎯 Purpose

The goal of this project is to:
- Assess compliance of EU member (as well as other European countries) states with monitoring requirements.  
- Identify the types and frequency of pesticides detected in dairy products.  
- Explore relationships and trends in monitoring results across years and countries.  
- Provide transparent, reproducible workflows for data transformation, statistical analysis, and visualization.  

---

## 🧪 Works Performed

- 📂 **Data preprocessing & transformation** – cleaning and structuring EFSA monitoring data (172 GB of raw data).  
- 📊 **Statistical analysis** – detection rates, exceedances, country-level comparisons, correlations & linear models.  
- 📈 **Visualization** – trends, country-level summaries, multi-pesticide visual representations.  
- 📝 **Hypothesis testing** – structured review of compliance and contamination levels.  

---

## 📂 Repository Structure

- **`data/`**  
  Contains datasets used in project.

- **`scr/`**  
Core components for loading, transforming and analysing data. `DataLoader` and `DataAggregator` classes implemented.

- **`analysis/`**  
  Analysis and visualisation. Jupyter notebooks labeled with with part number (analysis_x.ipynb) or hypothesis ID (visualization_x.ipynb).

- **`results/`**  
  Placeholder for analysis results. Files are labeled with number of hypothesis they solve (e.g. .csv files).

- **`plots/`**  
  Visualisations (e.g. .png files).

---

## 📑 Data Source

All analyses are based on **EFSA monitoring datasets** of pesticide residues in food.  
Relevant years: **2011-2024**. 

Countries: Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, Serbia, Slovakia, Slovenia, Spain, Sweden, United Kingdom, Northern Ireland.

All data sources are listed in `./data_sources.txt` file.

---

## ❓ Research Hypotheses

The project investigates the following research questions:

1. **Compliance check**  
   - Which countries met the minimum required number of milk samples in mandatory pesticide monitoring in: *2013, 2016, 2019 and 2022* for milk and in *2012, 2015* for butter?  

2. **Non-mandatory years**  
   - Did any countries test milk in years outside mandatory monitoring?  
   - Which pesticides were detected?
   - In what percentage of milk samples were pesticides detected (per country & year)?  
   - Were there exceedances of Maximum Residue Levels?  
   - What is the distribution of the most frequent pesticide detections by country?  

3. **Sample size vs. detection count**  
   - What is the relationship between the total number of analyzed samples and the number of identified substances in the mandatory monitoring years?  

4. **Trends in detection**  
   - What are the tendencies in pesticide detection rates (detections / total samples) in milk & butter across Europe for the mandatory years?  

5. **Country with most detections**  
   - Which country reported the highest number of pesticide detections in milk and butter?  

6. **Multiple residues visualization**  
   - How can multiple pesticide residues in samples (2012, 2013, 2015, 2016, 2019, 2022) be visualized?  

7. **Country–pesticide association**  
   - Are there any observable relationships between specific pesticides and the countries where they were detected?  

8. **Highest detections over time**
   - Which countries recorded the highest number of pesticide detections (and possible exceedances of maximum residue limits) in the MANCP between 2011 and 2023, and how does their ranking change over time?

9. **Non-mandatory programme sampling**
   - How many samples were collected under non-mandatory programmes, and what patterns can be observed?

10. **Non-mandatory milk sampling in 2023**  
   - What were the characteristics and outcomes of non-mandatory milk sampling in 2023?

11. **Non-Mandatory Programs Analysis:** How are the results distributed across non-mandatory pesticide testing programs? *(Visualized via horizontal bar charts)*

12. **Multiple Residues:** What is the frequency and distribution of multiple pesticide residues within the tested samples? *(Visualized via bar and pie charts)*

13. **Additional Testing Scope:** Which pesticides were tested additionally beyond those mandated by official guidelines (i.e., substances without a limit specified in regulations)?

14. **Program Variances:** Do the specific detected pesticides differ significantly across different testing programs? 

15. **Substance Co-occurrence:** How do different pesticide residues interrelate and co-occur within the dataset? *(Visualized via chord diagrams)*

16. **Regional Specifics:** What are the historical testing and usage trends for DDT, Hexachlorobenzene, and Indoxacarb specifically in Italy, France, Germany, and the Netherlands?

17. **Geographic & Temporal Distribution:** Where were the most pesticides detected across different years? *(Analyzing pesticide names, sample quantities, percentage of samples with residues, and concentration levels (mean ± SD), categorized into alert/violation columns).*

18. **Multivariate Correlations:** How can the relationships between pesticide concentrations, frequencies, and locations be multidimensionally mapped? *(Exploratory bubble charts)*

19. **Country of Origin Contamination:** Which countries produced the most contaminated products based on the total number of limit exceedances mapped from 2011 to 2024?

20. **Extreme Values:** What were the highest recorded residue values over the years specifically for non-mandatory testing programs?
---

## 🔎 Key Challenges & Problems Addressed

- **Data heterogeneity** – EFSA datasets differ across years as standards have changed in 2016 and therefore require careful harmonization.  
- **Statistical robustness** – ensuring correct interpretation of rare events and small sample sizes.  
- **Comparative analysis** – balancing per-country insights with European-wide trends.  

---

Developed by [@Gaspar Sekula](https://github.com/GasparSekula).
