# Hierarchy Analysis Summary - TC001 Balance

## Overview

This document summarizes the analysis of the expenditure category hierarchy to determine which items should be included to balance with **TC001 (Total Current Consumption)**. The goal was to create the most detailed breakdown possible while staying within **Level 4** of the hierarchy and ensuring the sum of components equals (or approximately equals) TC001.

## Hierarchy Structure

The expenditure hierarchy has the following levels:
- **Level 0**: TE001 (Total Expenditure)
- **Level 1**: TC001 (Total Current Consumption), TX010, EP011, MG001
- **Level 2**: Major categories (FD001, SH001, HO001, etc.) - 14 items
- **Level 3**: Subcategories - 43 items
- **Level 4**: Detailed subcategories - 51 items
- **Level 5-9**: More detailed breakdowns (excluded per requirements)

## Strategy

To ensure maximum detail while balancing with TC001:

1. **Include Level 4 items** where they exist (most detailed)
2. **Include Level 3 items** where no Level 4 children exist
3. **Include Level 2 items** where no Level 3 children exist
4. **Exclude parent totals** to avoid double-counting

## Items Included (72 total)

### Level 4 Items (43 items) - Most Detailed
These are included where available to provide maximum detail:

**Food (10 items):**
- FD100: Bakery products
- FD200: Cereal grains and cereal products
- FD300: Fruit, fruit preparations and nuts
- FD400: Vegetables and vegetable preparations
- FD500: Dairy products and eggs
- FD600: Meat
- FD700: Fish and seafood
- FD800: Non-alcoholic beverages and other food products
- FD991: Restaurant meals
- FD995: Restaurant snacks and beverages

**Clothing (2 items):**
- CL014: Clothing services
- CL015: Clothing services

**Health Care (2 items):**
- HC025: Accident or disability insurance premiums
- HC061: Private health and dental plan premiums

**Household Operations (3 items):**
- HO004: Pet food
- HO005: Purchase of pets and pet-related goods
- HO006: Veterinarian and other services

**Recreation (14 items):**
- RE006: Video game systems and accessories
- RE007: Art and craft materials
- RE010: Computer equipment and supplies
- RE016: Photographic goods and services
- RE022: Collectors' items
- RE032: Other recreational equipment
- RE041: Home entertainment equipment
- RE052: Home entertainment services
- RE061: Entertainment
- RE074: Package trips
- RE090: Use of recreational facilities and fees
- RE124: Sports, athletic and recreational equipment
- RE140: Other recreational services
- RE990: Outdoor play equipment and children's toys

**Shelter (6 items):**
- SH003: Rented living quarters
- SH010: Owned living quarters
- SH030: Water, fuel and electricity for principal accommodation
- SH041: Owned secondary residences
- SH047: Other owned properties
- SH050: Accommodation away from home

**Tobacco and Alcohol (3 items):**
- TA006: Alcoholic beverages served on licensed premises
- TA007: Alcoholic beverages purchased from stores
- TA008: Self-made alcoholic beverages

**Transportation (3 items):**
- TR003: Private use automobiles, vans and trucks
- TR020: Rented automobiles, vans and trucks
- TR030: Automobile, van and truck operations

### Level 3 Items (28 items)
Included where no Level 4 children exist:

- CL016: Clothing services
- CL017: Clothing material, yarn, thread and other notions
- CL023: Children's wear (under 14 years)
- CL026: Men's and boys' wear (14 years and over)
- CL990: Accessories, watches, jewellery and athletic footwear
- ED003: Tuition fees
- ED030: Textbooks and school supplies
- HC022: Private health insurance plan premiums
- HF002: Household furnishings
- HO003: Pet expenses
- HO010: Household cleaning supplies and equipment
- HO014: Paper, plastic and foil supplies
- HO018: Garden supplies and services
- HO022: Other household supplies
- ME039: Financial services
- ME040: Other miscellaneous goods and services
- PC002: Personal care products
- PC020: Personal care services
- RE040: Home entertainment equipment and services
- RE060: Recreational services
- RO002: Newspapers
- RO003: Magazines and periodicals
- RO004: Books and E-Books (excluding school books)
- RO005: Maps, sheet music and other printed matter
- RO010: Services related to reading materials
- SH040: Other accommodation
- TA005: Alcoholic beverages
- TR070: Public transportation

### Level 2 Items (1 item)
Included where no Level 3 children exist:

- GC001: Games of chance

### Totals (2 items)
Always included:

- TC001: Total Current Consumption
- TE001: Total Expenditure

## Items Excluded (9 parent totals)

These parent totals are excluded to avoid double-counting since their children are included:

1. **CL029**: Women's and girls' wear (sum of CL014, CL015)
2. **FD003**: Food purchased from stores (sum of FD100, FD200, FD300, FD400, FD500, FD600, FD700, FD800)
3. **FD990**: Food purchased from restaurants (sum of FD991, FD995)
4. **HC002**: Direct costs to household (sum of HC025, HC061)
5. **HO002**: Domestic and other custodial services (sum of HO004, HO005, HO006)
6. **RE002**: Recreational equipment and related services (sum of 14 Level 4 items)
7. **SH002**: Principal accommodation (sum of SH003, SH010, SH030, SH041, SH047, SH050)
8. **TA990**: Tobacco products, smokers' supplies and cannabis (sum of TA006, TA007, TA008)
9. **TR002**: Private transportation (sum of TR003, TR020, TR030)

## Implementation

The application (`app.py`) has been updated to:

1. Use `ITEMS_FOR_TC001_BALANCE` set instead of the previous Level 3 only filter
2. Exclude `PARENT_TOTALS_TO_EXCLUDE` to prevent double-counting
3. Process 72 detailed items (43 Level 4, 28 Level 3, 1 Level 2) plus TC001 and TE001

## Expected Result

When these 72 items are summed, they should equal (or approximately equal) **TC001 (Total Current Consumption)**. This provides:

- **Maximum detail** within the Level 4 constraint
- **No double-counting** (parent totals excluded)
- **Balanced totals** that match TC001

## Notes

- Some items may be estimated using both diary file and interview file data
- The hierarchy structure ensures proper parent-child relationships
- Level 5-9 items are excluded per requirements
- The breakdown is as detailed as possible while maintaining balance with TC001

## Files Modified

- `app.py`: Updated to use the new item set for TC001 balance
- `analyze_hierarchy_final.py`: Analysis script used to determine the structure
- `hierarchy_balance_recommendations.json`: JSON file with recommendations

