# Survey of Household Spending 2019 - Spending Estimates Application

This application allows users to select demographic attributes and get detailed estimates of average household spending from the Survey of Household Spending 2019, with bootstrap variance estimates.

## Features

- **Interactive Filtering**: Select attributes including:
  - Geography (Province)
  - Household Characteristics (Type, Size, Dwelling Type, Tenure)
  - Reference Person Demographics (Age, Gender, Marital Status, Education)
  - Spouse Information (Age, Education)
  - Children in Household (Presence by age groups)
  - Vehicles (Ownership)
  - Income (Major source of income)

- **Comprehensive Spending Estimates**: 
  - Estimates for all spending codes (expenditure variables)
  - Aggregated estimates by spending category
  - All estimates in dollars per year

- **Bootstrap Variance Estimation**:
  - Uses all 500 bootstrap weights (BSW1 to BSW500) for proper variance estimation
  - Provides standard errors and coefficients of variation

- **Export Options**:
  - Excel export with comprehensive results including filter criteria, category breakdown, and individual spending codes

## Installation

1. Install Python 3.8 or higher

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Ensure the data files are in the correct location:
   - `SHS_EDM_2019/Data/SAS/pumf_shs2019.sas7bdat`
   - `SHS_EDM_2019/Data/SAS/pumf_shs2019_bsw.sas7bdat`

2. Run the Streamlit application:
```bash
streamlit run app.py
```

3. The application will open in your web browser. Use the interface to:
   - Select demographic attributes
   - Click "Calculate Estimates"
   - Download results as Excel

## Data Requirements

The application requires the Survey of Household Spending 2019 datasets in SAS format (.sas7bdat). The datasets should include:
- All spending variables (expenditure codes)
- Demographic variables (PROV, HHTYPE6, RP_GENDER, etc.)
- Bootstrap weights (BSW1 to BSW500) in a separate file
- Household weight (WEIGHTD)

## Bootstrap Variance Methodology

The bootstrap variance is calculated using the standard Statistics Canada methodology:

1. Calculate the estimate using the main household weight (WEIGHTD)
2. Calculate estimates using each of the 500 bootstrap weights (BSW1 to BSW500)
3. Calculate variance as: `Variance = mean((estimate_b - estimate_full)^2)` where b ranges over all bootstrap replicates

This provides proper variance estimates that account for the complex survey design.

## Spending Categories

Spending is organized into the following major categories:
- Child Care
- Clothing
- Communications
- Education
- Personal Insurance
- Food (with many subcategories)
- Games of Chance
- Health Care
- Household Equipment
- Household Furnishings
- Household Operations
- Miscellaneous
- Gifts and Contributions
- Personal Care
- Recreation
- Reading Materials
- Recreational Vehicles
- Shelter
- Tobacco and Alcohol
- Transportation
- Income Taxes

## Notes

- Calculations may take a few minutes when processing all spending categories with bootstrap variance
- The application uses caching to speed up data loading
- Ensure sufficient memory for large datasets
- Spending estimates are in dollars per year (annual household spending)

