# Comprehensive Page Analysis

## **1. Income Simulator Page (`5_Income_Simulator.py`)**

### **Purpose & Philosophical Objective**
The Income Simulator is the platform's most personalized analytical tool. Its primary goal is to **democratize economic data** by allowing users to see themselves within the abstract statistics of South Asian inequality. It shifts the perspective from "Macro Statistics" to "Micro Reality."

### **Key Features & Functionality**
*   **Personalized Economic Modeling:** Users input their demographic and professional details (Country, Education, Digital Skills, Gender, Location, Occupation, Credit Access, Age).
*   **Relative Standing Percentile:** The core output is a calculated percentile indicating how the user ranks compared to the rest of the population in their chosen country.
*   **Thematic Insight Engine:** A sophisticated feedback system that provides 5-7 detailed, thematic insights based on the user's inputs (e.g., "Educational Elite Status," "Systemic Gender Disparity," "Rural Economy Constraints").
*   **AI-Powered Recommendations:** Tailored "High Priority" and "Medium Priority" actions users can take to improve their economic mobility.
*   **Historical Benchmarking:** Allows users to compare their current standing against historical data (e.g., "Where would I stand in 2005?").

### **Technical Logic & Methodology**
*   **Dynamic Scarcity-Weighted Algorithm:** The simulator uses a multi-factor weighting engine. For example, if a user has tertiary education in a country with low tertiary enrollment (retrieved from the World Bank API), the `edu_mult` increases significantly, reflecting the "status premium" of that degree in a developing economy.
*   **Percentile Calculation:** The percentile is determined by comparing user inputs against a log-normal distribution $(\mu, \sigma)$ simulated from regional income means.
*   **Live Poverty Benchmarking:** It fetches the `SI.POV.GINI` (Gini) and `SI.POV.DDAY` (Poverty Gap) indicators to calculate a "Resilience Score," which quantifies how far the user is from the poverty threshold in their specific regional context.
*   **Cyberpunk Visualization:** Uses a high-frequency spline interpolation to render a "neon" population curve, where the user's position is marked by a dynamic "Laser Beam" marker.

---

## **2. Data Quality Page (`6_Data_Quality.py`)**

### **Purpose & Methodological Transparency**
The Data Quality page serves as the platform's **transparency layer**. It addresses the critical academic problem of "Data Gaps" in South Asia by explicitly showing what we know, what we don't know, and how reliable our conclusions are.

### **Key Features & Functionality**
*   **Completeness Monitoring:** Dynamically calculates the "percentage of completeness" for every country-indicator pair based on a 25-year historical target.
*   **Live API Validation:** A toggle-able feature that connects to the World Bank API in real-time to cross-check if "missing" local data is available in the latest global releases.
*   **Multi-Dimensional Quality metrics:**
    *   **Bubble Map:** Visualizes geographic patterns of data density.
    *   **Sankey Diagram:** Traces the "Data Flow" from initial sources to countries and finally to quality classifications (High/Medium/Low).
    *   **Ridgeline Plots:** Shows the "Probability Density" of data quality per country using Kernel Density Estimation (KDE).
*   **Critical Gap Identification:** A dedicated "Alarm" section that highlights countries or indicators with less than 60% data coverage, warning researchers to treat these findings with caution.

### **Technical Logic & Methodology**
*   **Dynamic Data Audit:** Performs a vectorized `groupby` operation on the entire 20,000+ record dataset to calculate completeness percentages $(\frac{Actual}{Expected} \times 100)$ in milliseconds.
*   **Ridgeline Density estimation:** Uses `scipy.stats.gaussian_kde` (Kernel Density Estimation) to visualize the "distribution of reliability." This allows researchers to see at a glance if data gaps are uniform or concentrated in specific years/indicator blocks.
*   **Sankey Flow Modeling:** Implements a directed graph showing the "leaks" in the data pipeline from primary sources like World Bank KIDB to the local analytical engine.
*   **Indicator Filtering:** Implements a "Searchability Matrix" that hides or warns about indicators with zero cross-country overlap, preventing users from attempting invalid comparisons.
