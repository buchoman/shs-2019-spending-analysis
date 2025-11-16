"""
Survey of Household Spending 2019 - Spending Estimates Application
This application allows users to select demographic attributes and get
detailed estimates of average household spending with bootstrap variance estimates.
"""

import streamlit as st
import pandas as pd
import numpy as np
import pyreadstat
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Survey of Household Spending 2019 - Spending Estimates",
    page_icon="💰",
    layout="wide"
)

# Data paths
DATA_DIR = Path("SHS_EDM_2019/Data/SAS")
MAIN_FILE = DATA_DIR / "pumf_shs2019.sas7bdat"
BSW_FILE = DATA_DIR / "pumf_shs2019_bsw.sas7bdat"

# Value label mappings for filter variables
VALUE_LABELS = {
    'PROV': {
        "10": "Newfoundland and Labrador",
        "11": "Prince Edward Island",
        "12": "Nova Scotia",
        "13": "New Brunswick",
        "24": "Quebec",
        "35": "Ontario",
        "46": "Manitoba",
        "47": "Saskatchewan",
        "48": "Alberta",
        "59": "British Columbia",
        "63": "Territorial capitals"
    },
    'HHTYPE6': {
        "1": "One person household",
        "2": "Couple without children",
        "3": "Couple with children",
        "4": "Couple with other related or unrelated persons",
        "5": "Lone parent family with no additional persons",
        "6": "Other household with related or unrelated persons"
    },
    'HHSIZE': {
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4 or more"
    },
    'P0TO4YN': {
        "1": "Yes",
        "2": "No"
    },
    'P5TO15YN': {
        "1": "Yes",
        "2": "No"
    },
    'P16TO29YN': {
        "1": "Yes",
        "2": "No"
    },
    'P30TO64YN': {
        "1": "Yes",
        "2": "No"
    },
    'P65TO74YN': {
        "1": "Yes",
        "2": "No"
    },
    'P75PLUSYN': {
        "1": "Yes",
        "2": "No"
    },
    'RP_AGEGRP': {
        "01": "Less than 30 years",
        "02": "30 to 39 years",
        "03": "40 to 54 years",
        "04": "55 to 64 years",
        "05": "65 to 74 years",
        "06": "75 years and over"
    },
    'RP_GENDER': {
        "1": "Male",
        "2": "Female"
    },
    'RP_MARSTAT': {
        "1": "Married or common-law",
        "2": "Single, never married",
        "3": "Separated, widowed or divorced"
    },
    'RP_EDUC': {
        "1": "Less than high school diploma or its equivalent",
        "2": "High school diploma, high school equivalency certificate, or not stated",
        "3": "Certificate or diploma from a trades school, college, CEGEP or other non-university educational institution",
        "4": "University certificate or diploma",
        "9": "Masked records (Prince Edward Island and the territorial capitals)"
    },
    'SPOUSEYN': {
        "1": "Yes",
        "2": "No"
    },
    'SP_AGEGRP': {
        "01": "Less than 30 years",
        "02": "30 to 39 years",
        "03": "40 to 54 years",
        "04": "55 to 64 years",
        "05": "65 to 74 years",
        "06": "75 years and over",
        "96": "No spouse"
    },
    'SP_GENDER': {
        "1": "Male",
        "2": "Female",
        "6": "No spouse"
    },
    'SP_EDUC': {
        "1": "Less than high school diploma or its equivalent",
        "2": "High school diploma, high school equivalency certificate, or not stated",
        "3": "Certificate or diploma from a trades school, college, CEGEP or other non-university educational institution",
        "4": "University certificate or diploma",
        "6": "No spouse",
        "9": "Masked records (Prince Edward Island and the territorial capitals)"
    },
    'DWELTYP': {
        "1": "Single detached",
        "2": "Double, row, terrace or duplex",
        "3": "Apartment or other"
    },
    'TENURE': {
        "1": "Owned with mortgage",
        "2": "Owned without mortgage",
        "3": "Rented"
    },
    'NUMBEDR': {
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4 or more"
    },
    'VEHICLEYN': {
        "1": "Yes",
        "2": "No"
    },
    'RECVEHYN': {
        "1": "Yes",
        "2": "No"
    },
    'HH_MAJINCSRC': {
        "1": "Earnings (employment income)",
        "2": "Investment income",
        "3": "Government transfer payments",
        "4": "Other income"
    }
}

def format_value(var_name, value):
    """Format a value using its label if available"""
    if var_name in VALUE_LABELS:
        # Convert to string for comparison
        str_val = str(value).strip()
        if str_val in VALUE_LABELS[var_name]:
            return VALUE_LABELS[var_name][str_val]
    return str(value)

# Parent/aggregate variables that should be excluded from category totals (to avoid double-counting)
# These are totals that include their subcategories
PARENT_TOTALS = {
    "FD001",  # Food expenditures (parent of all FD variables)
    "FD003",  # Food purchased from stores (parent of store food items)
    "FD990",  # Food purchased from restaurants (parent of FD991)
    "FD991",  # Restaurant meals (parent of FD992-FD995)
    "FD100",  # Bakery products (parent of FD101-FD108, FD112)
    "FD200",  # Cereal grains and cereal products (parent of FD201-FD212)
    "FD300",  # Fruit, fruit preparations and nuts (parent of FD301-FD316, FD330-FD382)
    "FD400",  # Vegetables and vegetable preparations (parent of FD401-FD412, FD418, FD421, FD440-FD479)
    "FD500",  # Dairy products and eggs (parent of FD501-FD505, FD520-FD525, FD540-FD541, FD550-FD555, FD570-FD572)
    "FD600",  # Meat (parent of FD601-FD607, FD650-FD660)
    "FD700",  # Fish and seafood (parent of FD701-FD706, FD720-FD724, FD730-FD732)
    "FD800",  # Non-alcoholic beverages and other food products (parent of FD801-FD802, FD806, FD814-FD815, FD821, FD827-FD829, FD833-FD889)
    "CS030",  # Communications (parent of CS003, CS004, CS005, etc.)
    "HF001",  # Household furnishings and equipment (parent of HF002)
    "HE001",  # Household equipment (parent of HE002, HE010, etc.)
    "HC001",  # Health care (parent of HC002, HC022, etc.)
    "HO001",  # Household operations (parent of HO002, HO003, etc.)
    "PC001",  # Personal care (parent of PC002, PC020)
    "RE001",  # Recreation (parent of RE002, RE003, etc.)
    "RO001",  # Reading materials (parent of RO002, RO003, etc.)
    "RV001",  # Recreational vehicles (parent of RV010, RV020)
    "SH001",  # Shelter (parent of SH002, SH003, etc.)
    "SH002",  # Shelter (another parent total)
    "TR001",  # Transportation (parent of TR002, TR003, etc.)
    "TR002",  # Transportation (another parent total)
    "ME001",  # Miscellaneous expenditures (parent of ME039, ME040)
    "TA018",  # Tobacco products, alcoholic beverages and cannabis (parent of TA005, TA006, TA007, TA008, TA990)
    "TC001",  # Total current consumption (parent of all consumption)
    "TE001"   # Total expenditure (parent of all expenditure)
}

# Spending category mappings (organized by major category prefix)
# Excludes parent totals to avoid double-counting
SPENDING_CATEGORIES = {
    "Child Care": ["CC001"],
    "Clothing": ["CL014", "CL015", "CL016", "CL017", "CL023", "CL026", "CL029", "CL030", "CL990"],
    "Communications": ["CS003", "CS004", "CS005", "CS007", "CS008", "CS020", "CS021"],  # Excluded CS030 (parent)
    "Education": ["ED002", "ED003", "ED030"],
    "Personal Insurance": ["EP011"],
    "Food": [
        # Excluded parent totals: FD001, FD003, FD990, FD991, FD100, FD200, FD300, FD400, FD500, FD600, FD700, FD800
        "FD1001", "FD1002", "FD1003", "FD1004", "FD101", "FD102", "FD103",
        "FD104", "FD105", "FD106", "FD107", "FD108", "FD112", "FD201", "FD202", "FD203",
        "FD204", "FD205", "FD206", "FD207", "FD208", "FD209", "FD212", "FD301", "FD302",
        "FD303", "FD304", "FD305", "FD308", "FD309", "FD315", "FD316", "FD330", "FD331", "FD350",
        "FD380", "FD381", "FD382", "FD401", "FD402", "FD403", "FD404", "FD405", "FD406",
        "FD407", "FD408", "FD409", "FD410", "FD411", "FD412", "FD418", "FD421", "FD440", "FD441",
        "FD442", "FD447", "FD470", "FD471", "FD478", "FD479", "FD501", "FD502", "FD503",
        "FD504", "FD505", "FD520", "FD521", "FD522", "FD525", "FD540", "FD541", "FD550", "FD551",
        "FD555", "FD570", "FD571", "FD572", "FD601", "FD602", "FD603", "FD604", "FD607",
        "FD650", "FD651", "FD660", "FD701", "FD705", "FD706", "FD720", "FD721", "FD722",
        "FD723", "FD724", "FD730", "FD731", "FD732", "FD801", "FD802", "FD806", "FD814",
        "FD815", "FD821", "FD827", "FD828", "FD829", "FD833", "FD834", "FD835", "FD836", "FD837",
        "FD838", "FD839", "FD840", "FD841", "FD842", "FD843", "FD844", "FD845", "FD846", "FD847",
        "FD850", "FD851", "FD852", "FD853", "FD854", "FD855", "FD857", "FD870", "FD871", "FD872",
        "FD873", "FD874", "FD875", "FD879", "FD880", "FD881", "FD882", "FD883", "FD884", "FD885",
        "FD889", "FD992", "FD993", "FD994", "FD995"  # Restaurant subcategories (excluded FD990, FD991)
    ],
    "Games of Chance": ["GC001"],
    "Health Care": ["HC002", "HC022", "HC025", "HC061"],  # Excluded HC001 (parent total)
    "Household Equipment": ["HE002", "HE010", "HE017", "HE020"],  # Excluded HE001 (parent total)
    "Household Furnishings": ["HF002"],  # Excluded HF001 (parent total)
    "Household Operations": ["HO002", "HO003", "HO004", "HO005", "HO006", "HO010", "HO014", "HO018", "HO022"],  # Excluded HO001 (parent total)
    "Miscellaneous": ["ME039", "ME040"],  # Excluded ME001 (parent total)
    "Gifts and Contributions": ["MG001"],
    "Personal Care": ["PC002", "PC020"],  # Excluded PC001 (parent total)
    "Recreation": [
        # Excluded RE001 (parent total)
        "RE002", "RE003", "RE006", "RE007", "RE010", "RE016", "RE020", "RE022", "RE032",
        "RE040", "RE041", "RE052", "RE060", "RE061", "RE062", "RE063", "RE066", "RE067", "RE074",
        "RE090", "RE120", "RE124", "RE127", "RE140", "RE990"
    ],
    "Reading Materials": ["RO002", "RO003", "RO004", "RO005", "RO010"],  # Excluded RO001 (parent total)
    "Recreational Vehicles": ["RV010", "RV020"],  # Excluded RV001 (parent total)
    "Shelter": [
        # Excluded SH001, SH002 (parent totals)
        "SH003", "SH004", "SH010", "SH011", "SH015", "SH016", "SH019", "SH030",
        "SH031", "SH032", "SH033", "SH034", "SH040", "SH041", "SH042", "SH044", "SH046", "SH047",
        "SH050", "SH060", "SH061", "SH062", "SH082", "SH990", "SH991", "SH992"
    ],
    "Tobacco and Alcohol": ["TA005", "TA006", "TA007", "TA008", "TA990"],  # Excluded TA018 (parent total)
    "Transportation": [
        # Excluded TR001, TR002 (parent totals)
        "TR003", "TR004", "TR008", "TR010", "TR020", "TR021", "TR022", "TR030",
        "TR031", "TR033", "TR034", "TR036", "TR038", "TR039", "TR070", "TR071", "TR085"
    ],
    "Income Taxes": ["TX010"]
}

# Spending variable descriptions (from SAS labels)
SPENDING_DESCRIPTIONS = {
    "CC001": "Child care",
    "CL014": "Laundromats, dry-cleaning and laundry services",
    "CL015": "Services for clothing, footwear and jewellery",
    "CL016": "Clothing services",
    "CL017": "Clothing material, yarn, thread and other notions",
    "CL023": "Children's wear (under 14 years)",
    "CL026": "Men's and boys' wear (14 years and over)",
    "CL029": "Women's and girls' wear (14 years and over)",
    "CL030": "Clothing and accessories",
    "CL990": "Accessories, watches, jewellery and athletic footwear",
    "CS003": "Telephone",
    "CS004": "Landline telephone services",
    "CS005": "Cell phone and pager services",
    "CS007": "Internet access services",
    "CS008": "Digital services",
    "CS020": "Postal, courier, delivery and other communication services",
    "CS021": "Telephones and equipment",
    "CS030": "Communications",
    "ED002": "Education",
    "ED003": "Tuition fees",
    "ED030": "Textbooks and school supplies",
    "EP011": "Personal insurance payments and pension contributions",
    "FD001": "Food expenditures",
    "FD003": "Food purchased from stores",
    "FD100": "Bakery products",
    "FD1001": "Frozen side dishes and other frozen prepared food",
    "FD1002": "Other ready-to-serve prepared food",
    "FD1003": "Cod, flounder, sole and haddock (fresh or frozen, uncooked)",
    "FD1004": "Other oils and fats",
    "FD101": "Bread and unsweetened rolls and buns",
    "FD102": "Bread",
    "FD103": "Unsweetened rolls and buns",
    "FD104": "Cookies and crackers",
    "FD105": "Cookies and sweet biscuits",
    "FD106": "Crackers and crisp breads",
    "FD107": "Other bakery products",
    "FD108": "Other bakery products (except frozen)",
    "FD112": "Frozen bakery products",
    "FD200": "Cereal grains and cereal products",
    "FD201": "Rice and rice mixes",
    "FD202": "Rice",
    "FD203": "Rice mixes",
    "FD204": "Pasta products",
    "FD205": "Pasta (fresh or dry)",
    "FD206": "Pasta (canned)",
    "FD207": "Pasta mixes",
    "FD208": "Other cereal grains and cereal products",
    "FD209": "Flour and flour-based mixes",
    "FD212": "Breakfast cereal and other grain products (except infant)",
    "FD300": "Fruit, fruit preparations and nuts",
    "FD301": "Fresh fruit",
    "FD302": "Apples (fresh)",
    "FD303": "Bananas and plantains (fresh)",
    "FD304": "Grapes (fresh)",
    "FD305": "Peaches and nectarines (fresh)",
    "FD308": "Pears (fresh)",
    "FD309": "Berries (fresh)",
    "FD315": "Citrus fruit (fresh)",
    "FD316": "Other fruit (fresh)",
    "FD330": "Preserved fruit and fruit preparations",
    "FD331": "Fruit juice",
    "FD350": "Other preserved fruit and fruit preparations",
    "FD380": "Nuts and seeds",
    "FD381": "Peanuts (shelled or unshelled)",
    "FD382": "Other nuts and seeds",
    "FD400": "Vegetables and vegetable preparations",
    "FD401": "Fresh vegetables",
    "FD402": "Potatoes (except sweet potatoes)",
    "FD403": "Tomatoes (fresh)",
    "FD404": "Lettuce (fresh)",
    "FD405": "Cabbage (fresh)",
    "FD406": "Carrots (fresh)",
    "FD407": "Onions (fresh)",
    "FD408": "Celery (fresh)",
    "FD409": "Cucumber (fresh)",
    "FD410": "Mushrooms (fresh)",
    "FD411": "Broccoli (fresh)",
    "FD412": "Other vegetables (fresh)",
    "FD418": "Peppers (fresh)",
    "FD421": "Fresh herbs",
    "FD440": "Frozen and dried vegetables",
    "FD441": "Potato products (frozen)",
    "FD442": "Other frozen vegetables",
    "FD447": "Dried vegetables and legumes",
    "FD470": "Canned vegetables and other vegetable preparations",
    "FD471": "Canned or bottled vegetables",
    "FD478": "Ready-to-serve or ready-to-cook prepared salads and side dishes, fruit or vegetable based",
    "FD479": "Vegetable juice (canned or bottled)",
    "FD500": "Dairy products and eggs",
    "FD501": "Cheese",
    "FD502": "Cheddar cheese",
    "FD503": "Mozzarella cheese",
    "FD504": "Processed cheese",
    "FD505": "Other cheeses",
    "FD520": "Milk",
    "FD521": "Fluid whole milk",
    "FD522": "Fluid low-fat milk",
    "FD525": "Skim and other fluid milk",
    "FD540": "Butter",
    "FD541": "Ice cream and ice milk (including novelties)",
    "FD550": "Other dairy products",
    "FD551": "Other processed milk products",
    "FD555": "Other processed dairy products",
    "FD570": "Eggs and other egg products",
    "FD571": "Eggs",
    "FD572": "Other egg products",
    "FD600": "Meat",
    "FD601": "Meat (except processed meat)",
    "FD602": "Beef",
    "FD603": "Pork",
    "FD604": "Poultry",
    "FD607": "Other meat and poultry",
    "FD650": "Processed meat",
    "FD651": "Bacon and ham",
    "FD660": "Other processed meat",
    "FD700": "Fish and seafood",
    "FD701": "Fresh or frozen fish",
    "FD705": "Salmon (fresh or frozen, uncooked)",
    "FD706": "Other fish (fresh or frozen, uncooked)",
    "FD720": "Canned fish or other preserved fish",
    "FD721": "Tuna (canned)",
    "FD722": "Salmon (canned)",
    "FD723": "Other fish (canned or bottled)",
    "FD724": "Cured fish",
    "FD730": "Seafood and other marine products",
    "FD731": "Shrimp and prawns",
    "FD732": "Other seafood and marine products",
    "FD800": "Non-alcoholic beverages and other food products",
    "FD801": "Non-alcoholic beverages and beverage mixes",
    "FD802": "Coffee and tea",
    "FD806": "Non-alcoholic beverages",
    "FD814": "Sugar and confectionery",
    "FD815": "Sugar, syrups and sugar substitutes",
    "FD821": "Candies and chocolates",
    "FD827": "Margarine, oils and fats (excluding butter)",
    "FD828": "Margarine",
    "FD829": "Cooking and salad oils",
    "FD833": "Condiments, spices and vinegars",
    "FD834": "Mayonnaise, salad dressings and dips",
    "FD835": "Pasta and pizza sauces (canned, bottled or dried)",
    "FD836": "Other sauces and gravies (canned, bottled or dried)",
    "FD837": "Dried herbs and spices",
    "FD838": "Ketchup",
    "FD839": "Other condiments (including vinegar)",
    "FD840": "Pickled vegetables (including olives)",
    "FD841": "Infant food",
    "FD842": "Infant formula",
    "FD843": "Infant cereals and biscuits",
    "FD844": "Canned or bottled infant food",
    "FD845": "Frozen prepared food",
    "FD846": "Frozen dinners and entrees",
    "FD847": "Frozen pizza",
    "FD850": "Soup (except infant soup)",
    "FD851": "Soup (chilled, frozen, canned or bottled)",
    "FD852": "Soup (dried)",
    "FD853": "Ready-to-serve prepared food",
    "FD854": "Dinners and entrees (except frozen)",
    "FD855": "Pizza (except frozen)",
    "FD857": "Fish portions (pre-cooked and frozen)",
    "FD870": "Other food preparations",
    "FD871": "Peanut butter and other nut butters",
    "FD872": "Honey",
    "FD873": "Flavoured drink powders, crystals and syrups",
    "FD874": "Non-dairy frozen ice treats",
    "FD875": "Dessert powders",
    "FD879": "Food seasonings (including table salt)",
    "FD880": "Other materials for food preparation",
    "FD881": "Tofu",
    "FD882": "Other canned, bottled or dried meals",
    "FD883": "Snack food",
    "FD884": "Potato-based snack foods",
    "FD885": "Other snack foods",
    "FD889": "Other infant food (including frozen)",
    "FD990": "Food purchased from restaurants",
    "FD991": "Restaurant meals",
    "FD992": "Restaurant dinners",
    "FD993": "Restaurant lunches",
    "FD994": "Restaurant breakfasts",
    "FD995": "Restaurant snacks and beverages",
    "GC001": "Games of chance",
    "HC001": "Health care",
    "HC002": "Direct costs to household",
    "HC022": "Private health insurance plan premiums",
    "HC025": "Accident or disability insurance premiums",
    "HC061": "Private health and dental plan premiums",
    "HE001": "Household equipment",
    "HE002": "Household appliances",
    "HE010": "Other household equipment",
    "HE017": "Maintenance, rental, repairs and services related to household furnishings and equipment",
    "HE020": "Services related to household furnishings and equipment",
    "HF001": "Household furnishings and equipment",
    "HF002": "Household furnishings",
    "HO001": "Household operations",
    "HO002": "Domestic and other custodial services (excluding child care)",
    "HO003": "Pet expenses",
    "HO004": "Pet food",
    "HO005": "Purchase of pets and pet-related goods",
    "HO006": "Veterinarian and other services",
    "HO010": "Household cleaning supplies and equipment",
    "HO014": "Paper, plastic and foil supplies",
    "HO018": "Garden supplies and services",
    "HO022": "Other household supplies",
    "ME001": "Miscellaneous expenditures",
    "ME039": "Financial services",
    "ME040": "Other miscellaneous goods and services",
    "MG001": "Gifts of money, support payments and charitable contributions",
    "PC001": "Personal care",
    "PC002": "Personal care products",
    "PC020": "Personal care services",
    "RE001": "Recreation",
    "RE002": "Recreational equipment and related services",
    "RE003": "Sports, athletic and recreation equipment",
    "RE006": "Video game systems and accessories (excluding for computers)",
    "RE007": "Art and craft materials",
    "RE010": "Computer equipment and supplies",
    "RE016": "Photographic goods and services",
    "RE020": "Photographic services",
    "RE022": "Collectors' items (e.g. stamps, coins)",
    "RE032": "Other recreational equipment",
    "RE040": "Home entertainment equipment and services",
    "RE041": "Home entertainment equipment",
    "RE052": "Home entertainment services",
    "RE060": "Recreational services",
    "RE061": "Entertainment",
    "RE062": "Movie theatres",
    "RE063": "Live sporting and performing arts events",
    "RE066": "Admission fees to museums, zoos, and other sites",
    "RE067": "Television and satellite radio services (including installation, service and pay TV charges)",
    "RE074": "Package trips",
    "RE090": "Use of recreational facilities and fees for other recreational activities",
    "RE120": "Camcorders, cameras, parts, accessories and related equipment",
    "RE124": "Sports, athletic and recreational equipment and related services",
    "RE127": "Rental, maintenance and repairs of sports, athletic and recreational equipment",
    "RE140": "Other recreational services",
    "RE990": "Outdoor play equipment and children's toys",
    "RO001": "Reading materials and other printed matter",
    "RO002": "Newspapers",
    "RO003": "Magazines and periodicals",
    "RO004": "Books and E-Books (excluding school books)",
    "RO005": "Maps, sheet music and other printed matter",
    "RO010": "Services related to reading materials (e.g. photocopying, library fees)",
    "RV001": "Recreational vehicles and associated services",
    "RV010": "Operation of recreational vehicles",
    "RV020": "Purchase of recreational vehicles",
    "SH001": "Shelter",
    "SH002": "Principal accommodation",
    "SH003": "Rented living quarters",
    "SH004": "Rent",
    "SH010": "Owned living quarters",
    "SH011": "Mortgage paid",
    "SH015": "Homeowners' insurance premiums",
    "SH016": "Other expenditures for owned living quarters",
    "SH019": "Mortgage insurance premiums",
    "SH030": "Water, fuel and electricity for principal accommodation",
    "SH031": "Water and sewage",
    "SH032": "Electricity",
    "SH033": "Natural gas",
    "SH034": "Other fuel",
    "SH040": "Other accommodation",
    "SH041": "Owned secondary residences",
    "SH042": "Mortgage paid",
    "SH044": "Insurance premiums",
    "SH046": "Other expenses for owned secondary residences",
    "SH047": "Other owned properties",
    "SH050": "Accommodation away from home",
    "SH060": "Communication and home security services (e.g. landline telephone, television, satellite radio and Internet)",
    "SH061": "Property and school taxes, water and sewage charges",
    "SH062": "Electricity and fuel (e.g. natural gas and wood)",
    "SH082": "Repairs and maintenance",
    "SH990": "Other expenses for rented living quarters",
    "SH991": "Condominium fees, property taxes and school taxes",
    "SH992": "All other expenses for the owned living quarters",
    "TA005": "Alcoholic beverages",
    "TA006": "Alcoholic beverages served on licensed premises and in restaurants",
    "TA007": "Alcoholic beverages purchased from stores",
    "TA008": "Self-made alcoholic beverages",
    "TA018": "Tobacco products, alcoholic beverages and cannabis for non-medical use",
    "TA990": "Tobacco products, smokers' supplies and cannabis for non-medical use",
    "TR001": "Transportation",
    "TR002": "Private transportation",
    "TR003": "Private use automobiles, vans and trucks",
    "TR004": "Purchase of automobiles, vans and trucks",
    "TR008": "Accessories for automobiles, vans and trucks",
    "TR010": "Fees for leased automobiles, vans and trucks",
    "TR020": "Rented automobiles, vans and trucks",
    "TR021": "Fees for rented vehicles (including insurance and mileage)",
    "TR022": "Other expenses for rented automobiles, vans and trucks",
    "TR030": "Automobile, van and truck operations",
    "TR031": "Registration fees (including insurance if part of registration)",
    "TR033": "Tires, batteries, and other parts and supplies for vehicles",
    "TR034": "Maintenance and repairs of vehicles",
    "TR036": "Gas and other fuels (all vehicles and tools)",
    "TR038": "Parking (excluding parking fees included in rent and traffic and parking tickets)",
    "TR039": "Drivers' licences and tests, and driving lessons",
    "TR070": "Public transportation",
    "TR071": "Vehicle operation, security and communication services",
    "TR085": "Public and private vehicle insurance premiums",
    "TX010": "Income taxes",
    "TC001": "Total current consumption",
    "TE001": "Total expenditure"
}

# Get all spending variables
ALL_SPENDING_VARS = []
for category, vars_list in SPENDING_CATEGORIES.items():
    ALL_SPENDING_VARS.extend(vars_list)
ALL_SPENDING_VARS = sorted(set(ALL_SPENDING_VARS))

# Items to include - only the 19 specified expenditure categories
# These are Level 2 categories plus totals that should balance with TC001
ITEMS_FOR_TC001_BALANCE = {
    # Totals
    "TE001",   # Total expenditure
    "TC001",   # Total current consumption
    
    # Level 2 expenditure categories
    "FD001",   # Food expenditures
    "SH001",   # Shelter
    "HO001",   # Household operations
    "HF001",   # Household furnishings and equipment
    "CL030",   # Clothing and accessories
    "TR001",   # Transportation
    "HC001",   # Health care
    "PC001",   # Personal care
    "RE001",   # Recreation
    "ED002",   # Education
    "RO001",   # Reading materials and other printed matter
    "TA018",   # Tobacco products, alcoholic beverages and cannabis for non-medical use
    "GC001",   # Games of chance
    "ME001",   # Miscellaneous expenditures
    "TX010",   # Income taxes
    "EP011",   # Personal insurance payments and pension contributions
    "MG001"    # Gifts of money, support payments and charitable contributions
}

# No parent totals to exclude - we're using Level 2 categories directly
PARENT_TOTALS_TO_EXCLUDE = set()

# Load hierarchy structure
@st.cache_data
def load_hierarchy():
    """Load the hierarchy structure from JSON file"""
    try:
        hierarchy_file = Path("hierarchy_structure.json")
        if hierarchy_file.exists():
            with open(hierarchy_file, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        st.warning(f"Could not load hierarchy structure: {e}")
        return None

@st.cache_data
def load_data():
    """Load the main dataset"""
    try:
        # Try reading with pyreadstat first
        df, meta = pyreadstat.read_sas7bdat(str(MAIN_FILE))
        return df, meta
    except Exception as e1:
        st.error(f"Error loading main data file: {e1}")
        return None, None

@st.cache_data
def load_bootstrap_weights():
    """Load the bootstrap weights dataset"""
    try:
        df_bsw, meta_bsw = pyreadstat.read_sas7bdat(str(BSW_FILE))
        return df_bsw, meta_bsw
    except Exception as e1:
        st.error(f"Error loading bootstrap weights file: {e1}")
        return None, None

def get_bootstrap_weights(df, df_bsw):
    """Get all bootstrap weight column names and merge with main data"""
    if df_bsw is None:
        return df, []
    
    # Merge bootstrap weights with main data on CaseID (handle case differences)
    # Main file uses 'CaseID', bootstrap file uses 'caseid'
    if 'CaseID' in df.columns:
        if 'caseid' in df_bsw.columns:
            df = df.merge(df_bsw, left_on='CaseID', right_on='caseid', how='left')
        elif 'CaseID' in df_bsw.columns:
            df = df.merge(df_bsw, left_on='CaseID', right_on='CaseID', how='left')
    
    # Get all BSW columns
    bsw_cols = [col for col in df.columns if col.startswith('BSW')]
    # Sort numerically by the number after BSW
    def sort_key(col):
        try:
            return int(col.replace('BSW', ''))
        except:
            return 0
    return df, sorted(bsw_cols, key=sort_key)

def get_variable_value(df, var):
    """Get the variable value, handling _C and _D versions.
    If both _C and _D exist, sum them. Otherwise use the available version."""
    var_c = var + '_C'
    var_d = var + '_D'
    
    has_c = var_c in df.columns
    has_d = var_d in df.columns
    
    if has_c and has_d:
        # Both exist, sum them
        return df[var_c].fillna(0) + df[var_d].fillna(0)
    elif has_c:
        # Only _C exists
        return df[var_c]
    elif has_d:
        # Only _D exists
        return df[var_d]
    elif var in df.columns:
        # Base variable exists (no _C or _D)
        return df[var]
    else:
        # Variable doesn't exist
        return pd.Series([np.nan] * len(df), index=df.index)

def calculate_weighted_mean(df, var, weight_col='WeightD'):
    """Calculate weighted mean for a variable, handling _C and _D versions"""
    # Get the variable value (handling _C and _D)
    var_values = get_variable_value(df, var)
    
    # Filter out missing values
    mask = var_values.notna() & (df[weight_col] > 0)
    if mask.sum() == 0:
        return np.nan
    
    weighted_sum = (var_values.loc[mask] * df.loc[mask, weight_col]).sum()
    total_weight = df.loc[mask, weight_col].sum()
    
    if total_weight == 0:
        return np.nan
    
    return weighted_sum / total_weight

def calculate_bootstrap_variance(df, var, weight_col='WeightD', bootstrap_cols=None):
    """Calculate bootstrap variance using bootstrap weights, handling _C and _D versions"""
    if bootstrap_cols is None or len(bootstrap_cols) == 0:
        return np.nan
    
    # Get variable values (handling _C and _D)
    var_values = get_variable_value(df, var)
    
    # Calculate estimate with main weight
    mask = var_values.notna() & (df[weight_col] > 0)
    if mask.sum() == 0:
        return np.nan
    
    weighted_sum = (var_values.loc[mask] * df.loc[mask, weight_col]).sum()
    total_weight = df.loc[mask, weight_col].sum()
    
    if total_weight == 0:
        return np.nan
    
    main_estimate = weighted_sum / total_weight
    
    if np.isnan(main_estimate):
        return np.nan
    
    # Calculate estimates with each bootstrap weight
    bootstrap_estimates = []
    for bs_col in bootstrap_cols:
        if bs_col in df.columns:
            bs_mask = var_values.notna() & (df[bs_col] > 0)
            if bs_mask.sum() > 0:
                bs_weighted_sum = (var_values.loc[bs_mask] * df.loc[bs_mask, bs_col]).sum()
                bs_total_weight = df.loc[bs_mask, bs_col].sum()
                if bs_total_weight > 0:
                    bs_estimate = bs_weighted_sum / bs_total_weight
                    if not np.isnan(bs_estimate):
                        bootstrap_estimates.append(bs_estimate)
    
    if len(bootstrap_estimates) == 0:
        return np.nan
    
    # Bootstrap variance formula: sum((estimate_b - estimate_full)^2) / B
    bootstrap_estimates = np.array(bootstrap_estimates)
    variance = np.mean((bootstrap_estimates - main_estimate) ** 2)
    
    return variance

def filter_data(df, filters, income_range=None):
    """Apply filters to the dataset"""
    filtered_df = df.copy()
    
    for var, value in filters.items():
        if value is not None and var in filtered_df.columns:
            if isinstance(value, list):
                if len(value) > 0:
                    filtered_df = filtered_df[filtered_df[var].isin(value)]
            else:
                filtered_df = filtered_df[filtered_df[var] == value]
    
    # Apply income range filter if provided
    if income_range is not None and 'HH_TotInc' in filtered_df.columns:
        min_income, max_income = income_range
        if min_income is not None:
            filtered_df = filtered_df[filtered_df['HH_TotInc'] >= min_income]
        if max_income is not None:
            filtered_df = filtered_df[filtered_df['HH_TotInc'] <= max_income]
    
    return filtered_df

def get_unique_values(df, column):
    """Get unique non-null values from a column"""
    if column not in df.columns:
        return []
    unique_vals = df[column].dropna().unique()
    return sorted([v for v in unique_vals if pd.notna(v)])

def format_option_label(var_name, value):
    """Format option label for selectbox"""
    label = format_value(var_name, value)
    return f"{label} ({value})" if label != str(value) else str(value)

def organize_hierarchical_results(results_df, hierarchy_data):
    """Organize results by hierarchy level with proper indentation"""
    if hierarchy_data is None:
        return None, None
    
    var_to_node = hierarchy_data.get('var_to_node', {})
    level_vars = hierarchy_data.get('level_vars', {})
    
    # Build ordered list based on hierarchy file order (by level, then by hierarchy position)
    # Create a mapping of var_code to results
    results_dict = {}
    for _, row in results_df.iterrows():
        var_code = row['Spending Code']
        results_dict[var_code] = {
            'var_code': var_code,
            'mean': row['Mean Dollars Per Year'],
            'variance': row['Variance'],
            'std_error': row['Standard Error'],
            'cv': row['Coefficient of Variation']
        }
    
    # Get all variables in hierarchy order (by level, maintaining file order)
    hierarchical_results = []
    for level in sorted(level_vars.keys()):
        vars_at_level = level_vars[level]
        for var_code in vars_at_level:
            if var_code in results_dict:  # Only include if we have results for it
                node = var_to_node.get(var_code, {})
                hierarchical_results.append({
                    'var_code': var_code,
                    'level': level,
                    'parent': node.get('parent'),
                    'description': SPENDING_DESCRIPTIONS.get(var_code, node.get('description', var_code)),
                    'mean': results_dict[var_code]['mean'],
                    'variance': results_dict[var_code]['variance'],
                    'std_error': results_dict[var_code]['std_error'],
                    'cv': results_dict[var_code]['cv']
                })
    
    return hierarchical_results, var_to_node

def build_hierarchical_display(hierarchical_results, var_to_node):
    """Build display data with proper indentation"""
    display_rows = []
    
    for item in hierarchical_results:
        level = int(item['level']) if item.get('level') is not None else 0
        indent = "  " * level  # 2 spaces per level
        var_code = item['var_code']
        description = item['description']
        
        display_rows.append({
            'Spending Code': var_code,
            'Spending Description': f"{indent}{description}",
            'Level': level,
            'Mean Dollars Per Year': item['mean'],
            'Variance': item['variance'],
            'Standard Error': item['std_error'],
            'Coefficient of Variation': item['cv']
        })
    
    return pd.DataFrame(display_rows)

def main():
    st.title("💰 Survey of Household Spending 2019 - Spending Estimates Application")
    st.markdown("""
    This application allows you to select demographic attributes and get detailed estimates 
    of average household spending (in dollars per year) with bootstrap variance estimates.
    """)
    
    # Load data and hierarchy
    with st.spinner("Loading data..."):
        df, meta = load_data()
        df_bsw, meta_bsw = load_bootstrap_weights()
        hierarchy_data = load_hierarchy()
    
    if df is None:
        st.error("Failed to load data. Please check that the data files are in the correct location.")
        return
    
    # Merge bootstrap weights
    df, bootstrap_cols = get_bootstrap_weights(df, df_bsw)
    
    st.success(f"Data loaded successfully! {len(df):,} records.")
    if len(bootstrap_cols) > 0:
        st.info(f"Bootstrap weights loaded: {len(bootstrap_cols)} weights available.")
    if hierarchy_data:
        st.info(f"Hierarchy structure loaded: {len(hierarchy_data.get('var_to_node', {}))} variables.")
    
    # Filters at the top of the page
    st.header("📊 Select Attributes")
    
    # Get unique values for filter variables
    filters = {}
    income_range = None  # Initialize income range
    
    # Create columns for filters: Left, Middle, Right
    col1, col2, col3 = st.columns(3)
    
    # LEFT COLUMN: Geography, Household Characteristics
    with col1:
        st.subheader("Geography")
        provinces = get_unique_values(df, 'Prov')
        if provinces:
            selected_provinces = st.multiselect(
                "Province",
                options=provinces,
                format_func=lambda x: format_option_label('PROV', x),
                help="Select one or more provinces. Leave empty to include all."
            )
            if len(selected_provinces) > 0:
                filters['Prov'] = selected_provinces
        
        st.subheader("Household Characteristics")
        hh_types = get_unique_values(df, 'HHType6')
        if hh_types:
            selected_hhtype = st.multiselect(
                "Household type",
                options=hh_types,
                format_func=lambda x: format_option_label('HHTYPE6', x),
                help="Select one or more household types. Leave empty to include all."
            )
            if len(selected_hhtype) > 0:
                filters['HHType6'] = selected_hhtype
        
        hh_sizes = get_unique_values(df, 'HHSize')
        if hh_sizes:
            selected_hhsize = st.multiselect(
                "Household size",
                options=hh_sizes,
                format_func=lambda x: format_option_label('HHSIZE', x),
                help="Select one or more household sizes. Leave empty to include all."
            )
            if len(selected_hhsize) > 0:
                filters['HHSize'] = selected_hhsize
        
        dwelling_types = get_unique_values(df, 'DwellTyp')
        if dwelling_types:
            selected_dwell = st.multiselect(
                "Type of dwelling",
                options=dwelling_types,
                format_func=lambda x: format_option_label('DWELTYP', x),
                help="Select one or more dwelling types. Leave empty to include all."
            )
            if len(selected_dwell) > 0:
                filters['DwellTyp'] = selected_dwell
        
        tenure = get_unique_values(df, 'Tenure')
        if tenure:
            selected_tenure = st.multiselect(
                "Dwelling tenure",
                options=tenure,
                format_func=lambda x: format_option_label('TENURE', x),
                help="Select one or more tenure types. Leave empty to include all."
            )
            if len(selected_tenure) > 0:
                filters['Tenure'] = selected_tenure
        
        # Household Total Income Range Slider
        if 'HH_TotInc' in df.columns:
            st.markdown("---")
            st.subheader("Household Total Income Range")
            income_min = float(df['HH_TotInc'].min())
            income_max = float(df['HH_TotInc'].max())
            # Default to full range (no filtering by default)
            income_default_min = income_min
            income_default_max = income_max
            
            income_range = st.slider(
                "Total Household Income ($)",
                min_value=int(income_min),
                max_value=int(income_max),
                value=(int(income_default_min), int(income_default_max)),
                step=1000,
                help="Select the minimum and maximum household income range. Drag the sliders to adjust. Default includes all households."
            )
            st.markdown(f"<p style='font-size: 1em; font-weight: normal;'>Selected range: <strong>${income_range[0]:,.0f}</strong> to <strong>${income_range[1]:,.0f}</strong></p>", unsafe_allow_html=True)
        else:
            income_range = None
    
    # MIDDLE COLUMN: Reference Person Demographics
    with col2:
        st.subheader("Reference Person Demographics")
        rp_age = get_unique_values(df, 'RP_AgeGrp')
        if rp_age:
            selected_rp_age = st.multiselect(
                "Reference person - Age group",
                options=rp_age,
                format_func=lambda x: format_option_label('RP_AGEGRP', x),
                help="Select one or more age groups. Leave empty to include all."
            )
            if len(selected_rp_age) > 0:
                filters['RP_AgeGrp'] = selected_rp_age
        
        rp_gender = get_unique_values(df, 'RP_Gender')
        if rp_gender:
            selected_rp_gender = st.multiselect(
                "Reference person - Gender",
                options=rp_gender,
                format_func=lambda x: format_option_label('RP_GENDER', x),
                help="Select one or more gender categories. Leave empty to include all."
            )
            if len(selected_rp_gender) > 0:
                filters['RP_Gender'] = selected_rp_gender
        
        rp_marstat = get_unique_values(df, 'RP_MarStat')
        if rp_marstat:
            selected_rp_marstat = st.multiselect(
                "Reference person - Marital status",
                options=rp_marstat,
                format_func=lambda x: format_option_label('RP_MARSTAT', x),
                help="Select one or more marital statuses. Leave empty to include all."
            )
            if len(selected_rp_marstat) > 0:
                filters['RP_MarStat'] = selected_rp_marstat
        
        rp_educ = get_unique_values(df, 'RP_Educ')
        if rp_educ:
            selected_rp_educ = st.multiselect(
                "Reference person - Education",
                options=rp_educ,
                format_func=lambda x: format_option_label('RP_EDUC', x),
                help="Select one or more education levels. Leave empty to include all."
            )
            if len(selected_rp_educ) > 0:
                filters['RP_Educ'] = selected_rp_educ
        
        st.subheader("Income")
        hh_majinc = get_unique_values(df, 'HH_MajIncSrc')
        if hh_majinc:
            selected_inc = st.multiselect(
                "Household - Major source of income",
                options=hh_majinc,
                format_func=lambda x: format_option_label('HH_MAJINCSRC', x),
                help="Select one or more income sources. Leave empty to include all."
            )
            if len(selected_inc) > 0:
                filters['HH_MajIncSrc'] = selected_inc
    
    # RIGHT COLUMN: Spouse, Children, Vehicles
    with col3:
        st.subheader("Spouse Information")
        # Check if SPOUSEYN exists, otherwise infer from SP_AgeGrp (if it has "96" = No spouse)
        sp_age = get_unique_values(df, 'SP_AgeGrp')
        if sp_age:
            selected_sp_age = st.multiselect(
                "Spouse - Age group",
                options=sp_age,
                format_func=lambda x: format_option_label('SP_AGEGRP', x),
                help="Select one or more age groups. Leave empty to include all."
            )
            if len(selected_sp_age) > 0:
                filters['SP_AgeGrp'] = selected_sp_age
        
        sp_educ = get_unique_values(df, 'SP_Educ')
        if sp_educ:
            selected_sp_educ = st.multiselect(
                "Spouse - Education",
                options=sp_educ,
                format_func=lambda x: format_option_label('SP_EDUC', x),
                help="Select one or more education levels. Leave empty to include all."
            )
            if len(selected_sp_educ) > 0:
                filters['SP_Educ'] = selected_sp_educ
        
        st.subheader("Children in Household")
        p0to4 = get_unique_values(df, 'P0to4YN')
        if p0to4:
            selected_p0to4 = st.multiselect(
                "Presence of persons aged 0 to 4 years",
                options=p0to4,
                format_func=lambda x: format_option_label('P0TO4YN', x),
                help="Select one or more options. Leave empty to include all."
            )
            if len(selected_p0to4) > 0:
                filters['P0to4YN'] = selected_p0to4
        
        p5to15 = get_unique_values(df, 'P5to15YN')
        if p5to15:
            selected_p5to15 = st.multiselect(
                "Presence of persons aged 5 to 15 years",
                options=p5to15,
                format_func=lambda x: format_option_label('P5TO15YN', x),
                help="Select one or more options. Leave empty to include all."
            )
            if len(selected_p5to15) > 0:
                filters['P5to15YN'] = selected_p5to15
        
        st.subheader("Vehicles")
        vehicle_yn = get_unique_values(df, 'VehicleYN')
        if vehicle_yn:
            selected_vehicle = st.multiselect(
                "Owned, leased or operated a vehicle",
                options=vehicle_yn,
                format_func=lambda x: format_option_label('VEHICLEYN', x),
                help="Select one or more options. Leave empty to include all."
            )
            if len(selected_vehicle) > 0:
                filters['VehicleYN'] = selected_vehicle
    
    # Update session state with current filters for real-time updates
    st.session_state.filters = filters
    st.session_state.income_range = income_range
    
    # Calculate and display matching records count in real-time
    filtered_df = filter_data(df, filters, income_range=st.session_state.income_range)
    filtered_count = len(filtered_df)
    
    # Display matching records count box
    if filtered_count == 0:
        st.warning("**0 records** match your selected criteria. Please adjust your selections.")
    else:
        st.info(f"**{filtered_count:,} records** match your selected criteria.")
    
    # Store filtered count in session state
    st.session_state.filtered_count = filtered_count
    
    # Main content area
    st.header("📈 Spending Estimates")
    
    if len(filtered_df) == 0:
        return
    
    # Calculate estimates
    if st.button("Calculate Estimates", type="primary"):
        if len(bootstrap_cols) == 0:
            st.error("No bootstrap weights found in the dataset. Cannot calculate variance estimates.")
            return
        
        # Ensure we're using the filtered data with income range
        filtered_df = filter_data(df, st.session_state.filters, income_range=st.session_state.income_range)
        
        st.info(f"Using {len(bootstrap_cols)} bootstrap weights for variance estimation.")
        
        # Overall progress tracking
        overall_progress_bar = st.progress(0)
        overall_status_text = st.empty()
        
        # Phase 1: Calculate individual spending estimates (70% of progress)
        overall_status_text.text("Phase 1 of 2: Calculating individual spending estimates...")
        results = []
        
        # Get spending variables that exist in the data AND are in the TC001 balance set
        # Check ITEMS_FOR_TC001_BALANCE directly (not filtered through ALL_SPENDING_VARS)
        # Handle _C and _D versions: check if base variable or _C/_D versions exist
        def variable_exists(df, var):
            """Check if variable exists in any form (base, _C, or _D)"""
            return (var in df.columns or 
                   (var + '_C') in df.columns or 
                   (var + '_D') in df.columns)
        
        # Check all items in ITEMS_FOR_TC001_BALANCE directly
        available_spending_vars = [
            var for var in ITEMS_FOR_TC001_BALANCE
            if variable_exists(filtered_df, var)
        ]
        
        # Exclude parent totals to avoid double-counting (should be empty set, but keeping for safety)
        available_spending_vars = [
            var for var in available_spending_vars 
            if var not in PARENT_TOTALS_TO_EXCLUDE
        ]
        
        if len(available_spending_vars) == 0:
            st.error("No spending variables found in the dataset.")
            overall_progress_bar.empty()
            overall_status_text.empty()
            return
        
        # Pre-build category lookup dictionary for faster lookups
        var_to_category = {}
        for cat, vars_list in SPENDING_CATEGORIES.items():
            for var in vars_list:
                var_to_category[var] = cat
        
        # Calculate for each spending variable (optimized with vectorized operations where possible)
        progress_bar = st.progress(0)
        status_text = st.empty()
        total_vars = len(available_spending_vars)
        
        for idx, var in enumerate(available_spending_vars):
            status_text.text(f"Processing {var} ({idx + 1}/{total_vars})...")
            
            mean_est = calculate_weighted_mean(filtered_df, var)
            variance = calculate_bootstrap_variance(filtered_df, var, bootstrap_cols=bootstrap_cols)
            std_error = np.sqrt(variance) if not np.isnan(variance) else np.nan
            
            # Find category (using pre-built lookup)
            category = var_to_category.get(var, "Other")
            
            # Get spending description
            spending_desc = SPENDING_DESCRIPTIONS.get(var, "Spending description not available")
            
            results.append({
                'Spending Code': var,
                'Spending Description': spending_desc,
                'Spending Category': category,
                'Mean Dollars Per Year': mean_est,
                'Variance': variance,
                'Standard Error': std_error,
                'Coefficient of Variation': (std_error / mean_est * 100) if not np.isnan(mean_est) and mean_est != 0 else np.nan
            })
            
            # Update both progress bars
            progress_bar.progress((idx + 1) / total_vars)
            overall_progress_bar.progress(0.7 * (idx + 1) / total_vars)
        
        st.session_state.results = pd.DataFrame(results)
        st.session_state.hierarchy_data = hierarchy_data  # Store hierarchy for later use
        progress_bar.empty()
        status_text.empty()
        
        # Phase 2: Calculate Level 2 category totals (30% of progress)
        overall_status_text.text("Phase 2 of 2: Calculating Level 2 category totals...")
        level2_totals = []
        
        if hierarchy_data:
            var_to_node = hierarchy_data.get('var_to_node', {})
            level_vars = hierarchy_data.get('level_vars', {})
            
            # Get Level 2 variables (main expenditure categories)
            level2_vars = level_vars.get('2', [])
            
            for level2_var in level2_vars:
                if not variable_exists(filtered_df, level2_var):
                    continue
                
                # Get all descendants of this Level 2 variable
                def get_all_descendants(var_code, var_to_node):
                    """Recursively get all descendant variable codes"""
                    descendants = []
                    node = var_to_node.get(var_code, {})
                    children = node.get('children', [])
                    for child in children:
                        if child in available_spending_vars and variable_exists(filtered_df, child):
                            descendants.append(child)
                            # Recursively get descendants of children
                            descendants.extend(get_all_descendants(child, var_to_node))
                    return descendants
                
                descendants = get_all_descendants(level2_var, var_to_node)
                
                # If we have descendants, sum them; otherwise use the Level 2 variable itself
                if len(descendants) > 0:
                    # Sum all descendants (handling _C and _D versions)
                    descendant_values = []
                    for desc_var in descendants:
                        desc_values = get_variable_value(filtered_df, desc_var)
                        descendant_values.append(desc_values)
                    
                    if descendant_values:
                        filtered_df['_LEVEL2_SUM'] = pd.concat(descendant_values, axis=1).sum(axis=1)
                        mean_est = calculate_weighted_mean(filtered_df, '_LEVEL2_SUM')
                        variance = calculate_bootstrap_variance(filtered_df, '_LEVEL2_SUM', bootstrap_cols=bootstrap_cols)
                    else:
                        continue
                else:
                    # Use the Level 2 variable directly if it exists in results (handles _C and _D)
                    if level2_var in available_spending_vars:
                        mean_est = calculate_weighted_mean(filtered_df, level2_var)
                        variance = calculate_bootstrap_variance(filtered_df, level2_var, bootstrap_cols=bootstrap_cols)
                    else:
                        continue
                
                std_error = np.sqrt(variance) if not np.isnan(variance) else np.nan
                
                node = var_to_node.get(level2_var, {})
                description = SPENDING_DESCRIPTIONS.get(level2_var, node.get('description', level2_var))
                
                level2_totals.append({
                    'Spending Code': level2_var,
                    'Spending Description': description,
                    'Mean Dollars Per Year': mean_est,
                    'Variance': variance,
                    'Standard Error': std_error,
                    'Coefficient of Variation': (std_error / mean_est * 100) if not np.isnan(mean_est) and mean_est != 0 else np.nan
                })
        
        st.session_state.level2_totals = pd.DataFrame(level2_totals) if level2_totals else None
        overall_progress_bar.progress(1.0)
        
        # Calculate average household income and current consumption
        avg_household_income = calculate_weighted_mean(filtered_df, 'HH_TotInc')
        avg_income_variance = calculate_bootstrap_variance(filtered_df, 'HH_TotInc', bootstrap_cols=bootstrap_cols)
        avg_income_se = np.sqrt(avg_income_variance) if not np.isnan(avg_income_variance) else np.nan
        
        # Calculate TC001 (Total Current Consumption) - handles _C and _D versions
        tc001_values = get_variable_value(filtered_df, 'TC001')
        if tc001_values.notna().any():
            avg_current_consumption = calculate_weighted_mean(filtered_df, 'TC001')
            avg_consumption_variance = calculate_bootstrap_variance(filtered_df, 'TC001', bootstrap_cols=bootstrap_cols)
            avg_consumption_se = np.sqrt(avg_consumption_variance) if not np.isnan(avg_consumption_variance) else np.nan
        else:
            avg_current_consumption = np.nan
            avg_consumption_se = np.nan
        
        st.session_state.avg_household_income = avg_household_income
        st.session_state.avg_income_se = avg_income_se
        st.session_state.avg_current_consumption = avg_current_consumption
        st.session_state.avg_consumption_se = avg_consumption_se
        
        overall_progress_bar.progress(1.0)
        overall_progress_bar.empty()
        overall_status_text.empty()
        st.success("Calculations complete!")
    
    # Calculate by Income Quintile feature
    st.markdown("---")
    st.subheader("📊 Calculate by Income Quintile")
    
    if st.button("Calculate by Income Quintile", type="primary"):
        if len(bootstrap_cols) == 0:
            st.error("No bootstrap weights found in the dataset. Cannot calculate variance estimates.")
        else:
            # Ensure we're using the filtered data with income range
            filtered_df = filter_data(df, st.session_state.filters, income_range=st.session_state.income_range)
            
            if 'HH_TotInc' not in filtered_df.columns:
                st.error("Household total income (HH_TotInc) not found in the dataset.")
            else:
                # Remove any income range filter for quintile calculation (use full filtered sample)
                quintile_df = filtered_df.copy()
                
                # Calculate income quintiles based on weighted percentiles
                # Use weighted quantiles to determine quintile boundaries
                income_col = 'HH_TotInc'
                weight_col = 'WeightD'
                
                # Filter out missing income values
                valid_income = quintile_df[income_col].notna() & (quintile_df[weight_col] > 0)
                quintile_df = quintile_df[valid_income].copy()
                
                if len(quintile_df) == 0:
                    st.error("No valid income data found in the filtered sample.")
                else:
                    # Calculate weighted percentiles for quintile boundaries
                    # Sort by income
                    sorted_df = quintile_df.sort_values(income_col).copy()
                    sorted_df['cumsum_weight'] = sorted_df[weight_col].cumsum()
                    total_weight = sorted_df[weight_col].sum()
                    
                    # Find quintile boundaries (20th, 40th, 60th, 80th percentiles)
                    quintile_boundaries = []
                    for percentile in [20, 40, 60, 80]:
                        target_weight = total_weight * (percentile / 100)
                        # Find the index where cumulative weight reaches or exceeds target
                        mask = sorted_df['cumsum_weight'] >= target_weight
                        if mask.any():
                            boundary_idx = mask.idxmax()
                            boundary_value = sorted_df.loc[boundary_idx, income_col]
                            quintile_boundaries.append(boundary_value)
                        else:
                            # If target weight is beyond all data, use max income
                            quintile_boundaries.append(sorted_df[income_col].max())
                    
                    # Assign quintiles
                    def assign_quintile(income):
                        if pd.isna(income):
                            return None
                        if income <= quintile_boundaries[0]:
                            return 1
                        elif income <= quintile_boundaries[1]:
                            return 2
                        elif income <= quintile_boundaries[2]:
                            return 3
                        elif income <= quintile_boundaries[3]:
                            return 4
                        else:
                            return 5
                    
                    quintile_df['Income_Quintile'] = quintile_df[income_col].apply(assign_quintile)
                    
                    # Get available spending variables
                    def variable_exists(df, var):
                        """Check if variable exists in any form (base, _C, or _D)"""
                        return (var in df.columns or 
                               (var + '_C') in df.columns or 
                               (var + '_D') in df.columns)
                    
                    available_spending_vars = [
                        var for var in ITEMS_FOR_TC001_BALANCE
                        if variable_exists(quintile_df, var)
                    ]
                    
                    # Calculate statistics for each quintile and each spending category
                    quintile_results = []
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    total_calculations = len(available_spending_vars) * 5
                    current_calc = 0
                    
                    for var in available_spending_vars:
                        var_desc = SPENDING_DESCRIPTIONS.get(var, var)
                        
                        for quintile in range(1, 6):
                            current_calc += 1
                            status_text.text(f"Processing {var} - Quintile {quintile} ({current_calc}/{total_calculations})...")
                            progress_bar.progress(current_calc / total_calculations)
                            
                            # Filter to this quintile
                            quintile_data = quintile_df[quintile_df['Income_Quintile'] == quintile]
                            
                            if len(quintile_data) == 0:
                                continue
                            
                            # Calculate weighted mean
                            mean_est = calculate_weighted_mean(quintile_data, var)
                            
                            # Calculate bootstrap variance
                            variance = calculate_bootstrap_variance(quintile_data, var, bootstrap_cols=bootstrap_cols)
                            std_error = np.sqrt(variance) if not np.isnan(variance) else np.nan
                            
                            # Calculate CV (Coefficient of Variation)
                            cv = (std_error / mean_est * 100) if not np.isnan(mean_est) and mean_est != 0 else np.nan
                            
                            quintile_results.append({
                                'Spending Code': var,
                                'Spending Description': var_desc,
                                'Income Quintile': quintile,
                                'Average ($)': mean_est,
                                'Coefficient of Variation (%)': cv
                            })
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    if quintile_results:
                        quintile_df_results = pd.DataFrame(quintile_results)
                        
                        # Round numeric columns
                        quintile_df_results['Average ($)'] = quintile_df_results['Average ($)'].round(2)
                        quintile_df_results['Coefficient of Variation (%)'] = quintile_df_results['Coefficient of Variation (%)'].round(2)
                        
                        # Store in session state
                        st.session_state.quintile_results = quintile_df_results
                        
                        # Display quintile boundaries
                        st.info(f"""
                        **Income Quintile Boundaries:**
                        - Quintile 1 (Lowest): ≤ ${quintile_boundaries[0]:,.0f}
                        - Quintile 2: ${quintile_boundaries[0]:,.0f} - ${quintile_boundaries[1]:,.0f}
                        - Quintile 3: ${quintile_boundaries[1]:,.0f} - ${quintile_boundaries[2]:,.0f}
                        - Quintile 4: ${quintile_boundaries[2]:,.0f} - ${quintile_boundaries[3]:,.0f}
                        - Quintile 5 (Highest): > ${quintile_boundaries[3]:,.0f}
                        """)
                        
                        # Display results in a pivot table format
                        st.subheader("Spending by Income Quintile")
                        
                        # Calculate Total (all quintiles combined) for each variable
                        total_results = []
                        for var in available_spending_vars:
                            # Calculate weighted mean for all quintiles combined
                            total_mean = calculate_weighted_mean(quintile_df, var)
                            total_variance = calculate_bootstrap_variance(quintile_df, var, bootstrap_cols=bootstrap_cols)
                            total_std_error = np.sqrt(total_variance) if not np.isnan(total_variance) else np.nan
                            total_cv = (total_std_error / total_mean * 100) if not np.isnan(total_mean) and total_mean != 0 else np.nan
                            
                            total_results.append({
                                'var': var,
                                'total_avg': total_mean,
                                'total_cv': total_cv
                            })
                        
                        total_dict = {r['var']: {'avg': r['total_avg'], 'cv': r['total_cv']} for r in total_results}
                        
                        # Create pivot table: rows = spending categories, columns = quintiles + Total
                        pivot_data = []
                        for var in available_spending_vars:
                            var_desc = SPENDING_DESCRIPTIONS.get(var, var)
                            row = {'Spending Code': var, 'Spending Description': var_desc}
                            
                            # Add quintile columns
                            for quintile in range(1, 6):
                                quintile_data = quintile_df_results[
                                    (quintile_df_results['Spending Code'] == var) & 
                                    (quintile_df_results['Income Quintile'] == quintile)
                                ]
                                
                                if len(quintile_data) > 0:
                                    avg = quintile_data.iloc[0]['Average ($)']
                                    cv = quintile_data.iloc[0]['Coefficient of Variation (%)']
                                    row[f'Q{quintile} Avg ($)'] = avg
                                    row[f'Q{quintile} CV (%)'] = cv
                                else:
                                    row[f'Q{quintile} Avg ($)'] = np.nan
                                    row[f'Q{quintile} CV (%)'] = np.nan
                            
                            # Add Total column
                            if var in total_dict:
                                row['Total Avg ($)'] = total_dict[var]['avg']
                                row['Total CV (%)'] = total_dict[var]['cv']
                            else:
                                row['Total Avg ($)'] = np.nan
                                row['Total CV (%)'] = np.nan
                            
                            pivot_data.append(row)
                        
                        pivot_df = pd.DataFrame(pivot_data)
                        # Round numeric columns
                        for col in pivot_df.columns:
                            if 'Avg' in col or 'CV' in col:
                                pivot_df[col] = pd.to_numeric(pivot_df[col], errors='coerce').round(2)
                        
                        st.dataframe(pivot_df, use_container_width=True, height=600)
                        
                        st.success(f"Calculated spending estimates for {len(available_spending_vars)} categories across 5 income quintiles.")
                        
                        # Export quintile results to Excel
                        st.subheader("📥 Export Quintile Results")
                        try:
                            from io import BytesIO
                            from openpyxl import load_workbook
                            from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
                            from openpyxl.utils import get_column_letter
                            
                            output = BytesIO()
                            
                            # Get all available filter variables and their options
                            all_filter_vars = {
                                'PROV': get_unique_values(df, 'Prov'),
                                'HHTYPE6': get_unique_values(df, 'HHType6'),
                                'HHSIZE': get_unique_values(df, 'HHSize'),
                                'DWELTYP': get_unique_values(df, 'DwellTyp'),
                                'TENURE': get_unique_values(df, 'Tenure'),
                                'RP_AGEGRP': get_unique_values(df, 'RP_AgeGrp'),
                                'RP_GENDER': get_unique_values(df, 'RP_Gender'),
                                'RP_MARSTAT': get_unique_values(df, 'RP_MarStat'),
                                'RP_EDUC': get_unique_values(df, 'RP_Educ'),
                                'SP_AGEGRP': get_unique_values(df, 'SP_AgeGrp'),
                                'SP_EDUC': get_unique_values(df, 'SP_Educ'),
                                'P0TO4YN': get_unique_values(df, 'P0to4YN'),
                                'P5TO15YN': get_unique_values(df, 'P5to15YN'),
                                'VEHICLEYN': get_unique_values(df, 'VehicleYN'),
                                'HH_MAJINCSRC': get_unique_values(df, 'HH_MajIncSrc')
                            }
                            
                            # Create Excel file
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                all_data = []
                                
                                # TOP SECTION: Source and Filters
                                all_data.append(["Survey of Household Spending 2019 - Spending Estimates by Income Quintile"])
                                all_data.append([""])
                                all_data.append(["Source:"])
                                all_data.append(["Statistics Canada. Survey of Household Spending, 2019. " +
                                                "Public Use Microdata File. Statistics Canada Catalogue no. 62M0004X. " +
                                                "This does not constitute an endorsement by Statistics Canada of this product."])
                                all_data.append([""])
                                all_data.append(["Generated:", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")])
                                all_data.append([""])
                                all_data.append(["Filter Criteria:"])
                                all_data.append(["Variable", "Selected Value", "All Available Options"])
                                
                                # Add filter information
                                filter_labels = {
                                    'PROV': 'Province',
                                    'HHTYPE6': 'Household type',
                                    'HHSIZE': 'Household size',
                                    'DWELTYP': 'Type of dwelling',
                                    'TENURE': 'Dwelling tenure',
                                    'RP_AGEGRP': 'Reference person - Age group',
                                    'RP_GENDER': 'Reference person - Gender',
                                    'RP_MARSTAT': 'Reference person - Marital status',
                                    'RP_EDUC': 'Reference person - Education',
                                    'SP_AGEGRP': 'Spouse - Age group',
                                    'SP_EDUC': 'Spouse - Education',
                                    'P0TO4YN': 'Presence of persons aged 0 to 4 years',
                                    'P5TO15YN': 'Presence of persons aged 5 to 15 years',
                                    'VEHICLEYN': 'Owned, leased or operated a vehicle',
                                    'HH_MAJINCSRC': 'Household - Major source of income'
                                }
                                
                                var_name_map = {
                                    'PROV': 'Prov',
                                    'HHTYPE6': 'HHType6',
                                    'HHSIZE': 'HHSize',
                                    'DWELTYP': 'DwellTyp',
                                    'TENURE': 'Tenure',
                                    'RP_AGEGRP': 'RP_AgeGrp',
                                    'RP_GENDER': 'RP_Gender',
                                    'RP_MARSTAT': 'RP_MarStat',
                                    'RP_EDUC': 'RP_Educ',
                                    'SP_AGEGRP': 'SP_AgeGrp',
                                    'SP_EDUC': 'SP_Educ',
                                    'P0TO4YN': 'P0to4YN',
                                    'P5TO15YN': 'P5to15YN',
                                    'VEHICLEYN': 'VehicleYN',
                                    'HH_MAJINCSRC': 'HH_MajIncSrc'
                                }
                                
                                for var, label in filter_labels.items():
                                    if var in all_filter_vars and all_filter_vars[var]:
                                        actual_var = var_name_map.get(var, var)
                                        selected_val = st.session_state.filters.get(actual_var, None)
                                        if selected_val is not None:
                                            if isinstance(selected_val, list):
                                                if len(selected_val) > 0:
                                                    selected_labels = []
                                                    for val in selected_val:
                                                        lbl = format_value(var, val)
                                                        selected_labels.append(f"{lbl} ({val})")
                                                    selected_display = "; ".join(selected_labels)
                                                else:
                                                    selected_display = "All"
                                            else:
                                                selected_label = format_value(var, selected_val)
                                                selected_display = f"{selected_label} ({selected_val})"
                                        else:
                                            selected_display = "All"
                                        
                                        options_list = []
                                        for val in sorted(all_filter_vars[var]):
                                            opt_label = format_value(var, val)
                                            options_list.append(f"{opt_label} ({val})")
                                        options_str = "; ".join(options_list[:10])
                                        if len(options_list) > 10:
                                            options_str += f"; ... ({len(options_list)} total options)"
                                        
                                        all_data.append([label, selected_display, options_str])
                                
                                # Add income range filter if applied
                                if st.session_state.get('income_range') is not None:
                                    income_range = st.session_state.income_range
                                    all_data.append(["Household Total Income Range:", f"${income_range[0]:,.0f} to ${income_range[1]:,.0f}"])
                                
                                all_data.append([""])
                                all_data.append(["Number of Records Matching Criteria:", st.session_state.get('filtered_count', 'N/A')])
                                
                                # Add quintile boundaries
                                all_data.append([""])
                                all_data.append(["Income Quintile Boundaries:"])
                                all_data.append(["Quintile", "Income Range"])
                                all_data.append(["Quintile 1 (Lowest)", f"≤ ${quintile_boundaries[0]:,.0f}"])
                                all_data.append(["Quintile 2", f"${quintile_boundaries[0]:,.0f} - ${quintile_boundaries[1]:,.0f}"])
                                all_data.append(["Quintile 3", f"${quintile_boundaries[1]:,.0f} - ${quintile_boundaries[2]:,.0f}"])
                                all_data.append(["Quintile 4", f"${quintile_boundaries[2]:,.0f} - ${quintile_boundaries[3]:,.0f}"])
                                all_data.append(["Quintile 5 (Highest)", f"> ${quintile_boundaries[3]:,.0f}"])
                                
                                all_data.append([""])
                                all_data.append([""])
                                
                                # BOTTOM SECTION: Quintile Results
                                all_data.append(["Spending by Income Quintile"])
                                
                                # Create header row
                                header_row = ["Spending Code", "Spending Description"]
                                for q in range(1, 6):
                                    header_row.append(f"Q{q} Avg ($)")
                                    header_row.append(f"Q{q} CV (%)")
                                header_row.append("Total Avg ($)")
                                header_row.append("Total CV (%)")
                                all_data.append(header_row)
                                
                                # Add data rows
                                for _, row in pivot_df.iterrows():
                                    data_row = [
                                        row['Spending Code'],
                                        row['Spending Description']
                                    ]
                                    for q in range(1, 6):
                                        avg_col = f'Q{q} Avg ($)'
                                        cv_col = f'Q{q} CV (%)'
                                        data_row.append(round(row[avg_col], 2) if pd.notna(row[avg_col]) else "")
                                        data_row.append(round(row[cv_col], 2) if pd.notna(row[cv_col]) else "")
                                    data_row.append(round(row['Total Avg ($)'], 2) if pd.notna(row['Total Avg ($)']) else "")
                                    data_row.append(round(row['Total CV (%)'], 2) if pd.notna(row['Total CV (%)']) else "")
                                    all_data.append(data_row)
                                
                                # Convert to DataFrame and write
                                export_df = pd.DataFrame(all_data)
                                export_df.to_excel(writer, sheet_name='Quintile Results', index=False, header=False)
                            
                            # Format the Excel file
                            output.seek(0)
                            wb = load_workbook(output)
                            ws = wb['Quintile Results']
                            
                            # Set print area and page setup
                            max_row = ws.max_row
                            max_col = ws.max_column
                            ws.print_area = f'A1:{get_column_letter(max_col)}{max_row}'
                            ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
                            ws.page_setup.fitToWidth = 1
                            ws.page_setup.fitToHeight = 0
                            
                            # Style headers
                            header_font = Font(bold=True, size=11)
                            title_font = Font(bold=True, size=12)
                            
                            # Format title row
                            ws['A1'].font = title_font
                            ws.merge_cells(f'A1:{get_column_letter(max_col)}1')
                            
                            # Format section headers
                            for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=max_row), 1):
                                cell_value = str(row[0].value) if row[0].value else ""
                                
                                is_header = any(keyword in cell_value for keyword in ["Source:", "Filter Criteria:", "Income Quintile Boundaries:", 
                                                                                     "Spending by Income Quintile", "Household Total Income Range:"])
                                if is_header:
                                    for cell in row:
                                        cell.font = Font(bold=True, size=11)
                                        cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
                            
                            # Auto-adjust column widths
                            for col in ws.columns:
                                max_length = 0
                                col_letter = get_column_letter(col[0].column)
                                for cell in col:
                                    try:
                                        if cell.value:
                                            max_length = max(max_length, len(str(cell.value)))
                                    except:
                                        pass
                                adjusted_width = min(max_length + 2, 50)
                                ws.column_dimensions[col_letter].width = adjusted_width
                            
                            # Save formatted workbook
                            output = BytesIO()
                            wb.save(output)
                            output.seek(0)
                            excel_data = output.read()
                            
                            st.download_button(
                                label="Download Quintile Results (Excel)",
                                data=excel_data,
                                file_name="spending_estimates_by_quintile.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key="excel_quintile",
                                type="primary",
                                use_container_width=True
                            )
                        except ImportError:
                            st.warning("Excel export requires openpyxl. Install with: pip install openpyxl")
                        except Exception as e:
                            st.error(f"Error creating Excel file: {e}")
                            import traceback
                            st.text(traceback.format_exc())
                    else:
                        st.warning("No results calculated. Please check your data filters.")
    
    # Display results
    if 'results' in st.session_state and st.session_state.results is not None:
        results_df = st.session_state.results.copy()
        
        # Round numeric columns
        numeric_cols = ['Mean Dollars Per Year', 'Variance', 'Standard Error', 'Coefficient of Variation']
        for col in numeric_cols:
            if col in results_df.columns:
                results_df[col] = results_df[col].round(2)
        
        # Add CSS for subtle table shading and column alignment
        st.markdown("""
        <style>
        /* Subtle shading for dataframes */
        div[data-testid="stDataFrame"] > div {
            background-color: #f8f9fa !important;
        }
        div[data-testid="stDataFrame"] table {
            background-color: #fafbfc !important;
        }
        div[data-testid="stDataFrame"] thead tr th {
            background-color: #f0f1f2 !important;
        }
        </style>
        <script>
        // Right-justify specific column headers and cells
        function alignNumericColumns() {
            const tables = document.querySelectorAll('div[data-testid="stDataFrame"] table');
            const numericHeaders = ['Mean Dollars Per Year', 'Variance', 'Standard Error', 'Coefficient of Variation'];
            
            tables.forEach(table => {
                const headers = Array.from(table.querySelectorAll('thead th'));
                headers.forEach((th, colIndex) => {
                    const headerText = th.textContent.trim();
                    if (numericHeaders.includes(headerText)) {
                        th.style.textAlign = 'right';
                        // Also align all cells in this column
                        const rows = table.querySelectorAll('tbody tr');
                        rows.forEach(row => {
                            const cell = row.querySelectorAll('td')[colIndex];
                            if (cell) {
                                cell.style.textAlign = 'right';
                            }
                        });
                    }
                });
            });
        }
        
        // Run immediately and after a delay to catch dynamically loaded tables
        alignNumericColumns();
        setTimeout(alignNumericColumns, 200);
        setTimeout(alignNumericColumns, 500);
        </script>
        """, unsafe_allow_html=True)
        
        # Display by expenditure category
        st.subheader("By Expenditure Category")
        # Organize results hierarchically
        hierarchy_data_display = st.session_state.get('hierarchy_data', hierarchy_data)
        hierarchical_results, var_to_node = organize_hierarchical_results(results_df, hierarchy_data_display)
        if hierarchical_results:
            display_df = build_hierarchical_display(hierarchical_results, var_to_node)
            # Reorder columns
            display_cols = ['Spending Code', 'Spending Description'] + [c for c in display_df.columns if c not in ['Spending Code', 'Spending Description', 'Level']]
            display_df = display_df[[c for c in display_cols if c in display_df.columns]]
            st.dataframe(display_df, use_container_width=True, height=400)
        else:
            # Fallback to original display if hierarchy not available
            display_cols = ['Spending Code', 'Spending Description', 'Spending Category'] + [c for c in results_df.columns if c not in ['Spending Code', 'Spending Description', 'Spending Category']]
            display_df = results_df[[c for c in display_cols if c in results_df.columns]]
            st.dataframe(display_df, use_container_width=True, height=400)
        
        # Export options - Single download button
        st.subheader("📥 Export Results")
        
        try:
            from io import BytesIO
            from openpyxl import load_workbook
            from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
            from openpyxl.utils import get_column_letter
            
            output = BytesIO()
            
            # Get all available filter variables and their options
            all_filter_vars = {
                'PROV': get_unique_values(df, 'Prov'),
                'HHTYPE6': get_unique_values(df, 'HHType6'),
                'HHSIZE': get_unique_values(df, 'HHSize'),
                'DWELTYP': get_unique_values(df, 'DwellTyp'),
                'TENURE': get_unique_values(df, 'Tenure'),
                'RP_AGEGRP': get_unique_values(df, 'RP_AgeGrp'),
                'RP_GENDER': get_unique_values(df, 'RP_Gender'),
                'RP_MARSTAT': get_unique_values(df, 'RP_MarStat'),
                'RP_EDUC': get_unique_values(df, 'RP_Educ'),
                'SP_AGEGRP': get_unique_values(df, 'SP_AgeGrp'),
                'SP_EDUC': get_unique_values(df, 'SP_Educ'),
                'P0TO4YN': get_unique_values(df, 'P0to4YN'),
                'P5TO15YN': get_unique_values(df, 'P5to15YN'),
                'VEHICLEYN': get_unique_values(df, 'VehicleYN'),
                'HH_MAJINCSRC': get_unique_values(df, 'HH_MajIncSrc')
            }
            
            # Create single sheet with all sections
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Create empty dataframe to start
                all_data = []
                
                # TOP SECTION: Source and Filters
                all_data.append(["Survey of Household Spending 2019 - Spending Estimates"])
                all_data.append([""])
                all_data.append(["Source:"])
                all_data.append(["Statistics Canada. Survey of Household Spending, 2019. " +
                                "Public Use Microdata File. Statistics Canada Catalogue no. 62M0004X. " +
                                "This does not constitute an endorsement by Statistics Canada of this product."])
                all_data.append([""])
                all_data.append(["Generated:", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")])
                all_data.append([""])
                all_data.append(["Filter Criteria:"])
                all_data.append(["Variable", "Selected Value", "All Available Options"])
                
                # Add filter information
                filter_labels = {
                    'PROV': 'Province',
                    'HHTYPE6': 'Household type',
                    'HHSIZE': 'Household size',
                    'DWELTYP': 'Type of dwelling',
                    'TENURE': 'Dwelling tenure',
                    'RP_AGEGRP': 'Reference person - Age group',
                    'RP_GENDER': 'Reference person - Gender',
                    'RP_MARSTAT': 'Reference person - Marital status',
                    'RP_EDUC': 'Reference person - Education',
                    'SP_AGEGRP': 'Spouse - Age group',
                    'SP_EDUC': 'Spouse - Education',
                    'P0TO4YN': 'Presence of persons aged 0 to 4 years',
                    'P5TO15YN': 'Presence of persons aged 5 to 15 years',
                    'VEHICLEYN': 'Owned, leased or operated a vehicle',
                    'HH_MAJINCSRC': 'Household - Major source of income'
                }
                
                # Map from display labels to actual column names
                var_name_map = {
                    'PROV': 'Prov',
                    'HHTYPE6': 'HHType6',
                    'HHSIZE': 'HHSize',
                    'DWELTYP': 'DwellTyp',
                    'TENURE': 'Tenure',
                    'RP_AGEGRP': 'RP_AgeGrp',
                    'RP_GENDER': 'RP_Gender',
                    'RP_MARSTAT': 'RP_MarStat',
                    'RP_EDUC': 'RP_Educ',
                    'SP_AGEGRP': 'SP_AgeGrp',
                    'SP_EDUC': 'SP_Educ',
                    'P0TO4YN': 'P0to4YN',
                    'P5TO15YN': 'P5to15YN',
                    'VEHICLEYN': 'VehicleYN',
                    'HH_MAJINCSRC': 'HH_MajIncSrc'
                }
                
                for var, label in filter_labels.items():
                    if var in all_filter_vars and all_filter_vars[var]:
                        actual_var = var_name_map.get(var, var)
                        selected_val = st.session_state.filters.get(actual_var, None)
                        if selected_val is not None:
                            # Handle both single values and lists
                            if isinstance(selected_val, list):
                                if len(selected_val) > 0:
                                    selected_labels = []
                                    for val in selected_val:
                                        lbl = format_value(var, val)
                                        selected_labels.append(f"{lbl} ({val})")
                                    selected_display = "; ".join(selected_labels)
                                else:
                                    selected_display = "All"
                            else:
                                selected_label = format_value(var, selected_val)
                                selected_display = f"{selected_label} ({selected_val})"
                        else:
                            selected_display = "All"
                        
                        # Get all available options
                        options_list = []
                        for val in sorted(all_filter_vars[var]):
                            opt_label = format_value(var, val)
                            options_list.append(f"{opt_label} ({val})")
                        options_str = "; ".join(options_list[:10])  # Limit to first 10 for display
                        if len(options_list) > 10:
                            options_str += f"; ... ({len(options_list)} total options)"
                        
                        all_data.append([label, selected_display, options_str])
                
                # Add income range filter if applied
                if st.session_state.get('income_range') is not None:
                    income_range = st.session_state.income_range
                    all_data.append(["Household Total Income Range:", f"${income_range[0]:,.0f} to ${income_range[1]:,.0f}"])
                
                all_data.append([""])
                all_data.append(["Number of Records Matching Criteria:", st.session_state.get('filtered_count', 'N/A')])
                
                all_data.append([""])
                all_data.append([""])
                
                # BOTTOM SECTION: Expenditure Categories
                all_data.append(["By Expenditure Category"])
                all_data.append(["Spending Code", "Spending Description", 
                               "Mean Dollars Per Year", "Variance", "Standard Error", "Coefficient of Variation (%)"])
                
                # Use hierarchical structure if available
                hierarchy_data_export = st.session_state.get('hierarchy_data', hierarchy_data)
                hierarchical_results_export, var_to_node_export = organize_hierarchical_results(results_df, hierarchy_data_export)
                
                if hierarchical_results_export:
                    # Build hierarchical display with indentation
                    for item in hierarchical_results_export:
                        level = int(item['level']) if item.get('level') is not None else 0
                        indent = "  " * level  # 2 spaces per level (matching Excel hierarchy)
                        var_code = item['var_code']
                        description = item['description']
                        
                        all_data.append([
                            var_code,
                            f"{indent}{description}",
                            round(item['mean'], 2),
                            round(item['variance'], 2),
                            round(item['std_error'], 2),
                            round(item['cv'], 2) if not pd.isna(item['cv']) else ""
                        ])
                else:
                    # Fallback to original structure
                    display_cols = ['Spending Code', 'Spending Description', 
                                  'Mean Dollars Per Year', 'Variance', 'Standard Error', 'Coefficient of Variation']
                    results_export = results_df[[c for c in display_cols if c in results_df.columns]].copy()
                    
                    for _, row in results_export.iterrows():
                        all_data.append([
                            row['Spending Code'],
                            row['Spending Description'],
                            round(row['Mean Dollars Per Year'], 2),
                            round(row['Variance'], 2),
                            round(row['Standard Error'], 2),
                            round(row['Coefficient of Variation'], 2) if not pd.isna(row['Coefficient of Variation']) else ""
                        ])
                
                # Convert to DataFrame and write
                export_df = pd.DataFrame(all_data)
                export_df.to_excel(writer, sheet_name='Spending Estimates', index=False, header=False)
            
            # Format the Excel file
            output.seek(0)
            wb = load_workbook(output)
            ws = wb['Spending Estimates']
            
            # Set print area and page setup
            max_row = ws.max_row
            max_col = ws.max_column
            ws.print_area = f'A1:{get_column_letter(max_col)}{max_row}'
            ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
            ws.page_setup.fitToWidth = 1
            ws.page_setup.fitToHeight = 0
            
            # Style headers and important rows
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=11)
            title_font = Font(bold=True, size=12)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Format title row
            ws['A1'].font = title_font
            ws.merge_cells(f'A1:{get_column_letter(max_col)}1')
            
            # Format section headers
            for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=max_row), 1):
                cell_value = str(row[0].value) if row[0].value else ""
                
                # Format section headers
                is_header = any(keyword in cell_value for keyword in ["Source:", "Filter Criteria:", 
                                                             "By Expenditure Category", "Spending Category Breakdown", "Individual Spending Code Breakdown", "TOTAL", "Household Total Income Range:"])
                if is_header:
                    for cell in row:
                        cell.font = Font(bold=True, size=11)
                        cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
            
            # Auto-adjust column widths
            for col in ws.columns:
                max_length = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[col_letter].width = adjusted_width
            
            # Save formatted workbook
            output = BytesIO()
            wb.save(output)
            output.seek(0)
            excel_data = output.read()
            
            col_left, col_right = st.columns([1, 3])
            with col_left:
                st.download_button(
                    label="Download All Results (Excel)",
                    data=excel_data,
                    file_name="spending_estimates_all.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="excel_all",
                    type="primary",
                    use_container_width=True
                )
        except ImportError:
            st.warning("Excel export requires openpyxl and Pillow. Install with: pip install openpyxl pillow")
        except Exception as e:
            st.error(f"Error creating Excel file: {e}")
            import traceback
            st.text(traceback.format_exc())

if __name__ == "__main__":
    main()

