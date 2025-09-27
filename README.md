# 🥛🐄 Pesticide Residues in Dairy Products (Milk & Butter)

This repository contains **data transformation, statistical analysis, and visualization** of pesticide residues in dairy products.  
The project is part of **Justyna Para's PhD research** at Institute of Animal Breeding, Wroclaw University of Environmental and Life Sciences.

---

## 📌 Introduction

Food safety is one of the most important public health concerns. Dairy products such as **milk** and **butter** are widely consumed across Europe, making them critical commodities for pesticide residue monitoring.  

This repository explores **European Food Safety Authority (EFSA) monitoring data** and addresses multiple hypotheses related to pesticide contamination, frequency of detections, exceedances, and trends over time.

---

## 🎯 Purpose

The goal of this project is to:
- Assess compliance of EU member states with monitoring requirements.  
- Identify the types and frequency of pesticides detected in dairy products.  
- Explore **statistical relationships and trends** in monitoring results across years and countries.  
- Prepare visualizations and analysis for poster.
- Provide **transparent, reproducible workflows** for data transformation, statistical analysis, and visualization.  

---

## 🧪 Works Performed

- 📂 **Data preprocessing & transformation** – cleaning and structuring 172GB of raw EFSA monitoring data.  
- 📊 **Statistical analysis** – detection rates, exceedances, country-level comparisons.  
- 📈 **Visualization** – trends, country-level summaries, multi-pesticide visual representations.  


The project processed and harmonized 172 GB of EFSA pesticide monitoring data (2011–2023) through extensive cleaning, transformation, merging, and aggregation. Analytical workflows were implemented using Pandas, NumPy, Scikit-Learn, with both object-oriented and functional programming patterns (e.g., DataLoader, DataAggregator classes). Statistical methods included linear regression models, Pearson/Spearman correlations, and absolute/relative change analysis to assess compliance, detection patterns, and associations. Visualization pipelines were built using Matplotlib, Plotly, and Seaborn to generate geographical maps, heat maps, chord diagrams, bar charts, and pie charts. Interactive and static plots were implemented to capture both country-level and Europe-wide detection patterns. Advanced multi-residue tables highlighted complex contamination cases across years. Hypothesis solving integrated these outputs to evaluate mandatory vs. non-mandatory programs, detection trends, and cross-country associations.

---

## 📂 Repository Structure

- `analysis/` 
    - notebooks and files with data transformation pipelines, analyses and visualizations

- `data/`
    - cleaned datasets and additional data sources

- `plots/`
    - visualizations

- `poster/`
    - analyses and visualizations for research poster

- `results/`
    - results in csv tables

- `src/`
    - source code including `DataLoader` and `DataAggregator` classes as well as visualization tools



---

## 📑 Data Source

All analyses are based on **EFSA monitoring datasets** of pesticide residues in food available in Zenodo repository. Links to data sources are listed in `data_sources.txt` file.

Relevant years: 2011-2023

Countries: Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, Serbia, Slovakia, Slovenia, Spain, Sweden, United Kingdom, Northern Ireland.


---

## ❓ Research Hypotheses

The project investigates the following research questions:

1. **Compliance check**  
   - Which countries met the minimum required number of milk samples in mandatory pesticide monitoring?  

2. **Non-mandatory years**  
   - Did any countries test milk in years outside mandatory monitoring?  
   - Which pesticides were detected? 
   - In what percentage of milk samples were pesticides detected (per country & year)?  
   - Were there exceedances of Maximum Residue Levels?  
   - What is the distribution of the most frequent pesticide detections by country of sampling?  

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


---

## 🔎 Key Challenges & Problems Addressed

- **Data heterogeneity** – EFSA datasets differ across years and require careful harmonization (schema change in 2017).  
- **Sampling compliance** – detecting gaps in monitoring across EU countries.  
- **Statistical robustness** – ensuring correct interpretation of rare events and small sample sizes.  


---

Developed by [@Gaspar Sekula](https://github.com/GasparSekula) 
