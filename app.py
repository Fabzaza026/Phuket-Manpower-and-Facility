import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sqlite3

try:
    from streamlit_autorefresh import st_autorefresh
except ModuleNotFoundError:
    def st_autorefresh(interval, key):
        return None



# ==============================================================================
# 🎨 PAGE CONFIGURATION & THAI AIRWAYS ROYAL ORCHID THEME CSS
# ==============================================================================
st.set_page_config(
    page_title="Thai Airways Phuket Station - Flight & Manpower Operations System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Thai Airways Branding Elements (Purple Text Sidebar Edition)
st.markdown("""
<style>
    /* Google Font Setup */
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');

    /* Main Background & Base Styling */
    .stApp {
        background: linear-gradient(180deg, #F8F5FA 0%, #F1ECF5 100%);
        font-family: 'Prompt', 'Inter', sans-serif;
    }
    
    /* Top Brand Banner Header */
    .brand-header {
        display: flex;
        align-items: center;
        gap: 18px;
        padding: 16px 24px;
        background: linear-gradient(135deg, #2B0A42 0%, #3B1358 60%, #511A72 100%);
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0px 8px 20px rgba(43, 10, 66, 0.25);
        border-bottom: 3px solid #EAA023;
    }
    .brand-header img {
        height: 48px;
        object-fit: contain;
        filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.3));
    }
    .brand-header-text h2 {
        color: #FFFFFF !important;
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        padding: 0 !important;
        letter-spacing: 0.5px;
        line-height: 1.2;
    }
    .brand-header-text p {
        color: #F3C973 !important;
        font-size: 0.88rem !important;
        font-weight: 400 !important;
        margin: 2px 0 0 0 !important;
        padding: 0 !important;
        letter-spacing: 0.3px;
    }

    /* -------------------------------------------------------------------------
       💜 SIDEBAR STYLING (PURPLE TEXT EDITION)
       ------------------------------------------------------------------------- */
    [data-testid="stSidebar"] {
        background-color: #F4EFFA !important; /* พื้นหลังสีสว่างเพื่อให้ตัวหนังสือม่วงเด่น */
        border-right: 1px solid rgba(81, 26, 114, 0.15);
    }
    
    /* บังคับตัวหนังสือ หัวข้อ ไอคอน และข้อความทั้งหมดใน Sidebar ให้เป็นสีม่วง */
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #3B1358 !important;
        font-weight: 600;
    }

    /* ตกแต่ง Selectbox ใน Sidebar ให้เป็นโทนสีม่วง */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
        background-color: #FFFFFF !important;
        color: #3B1358 !important;
        border: 2px solid #511A72 !important;
        border-radius: 10px !important;
    }

    .sidebar-brand {
        text-align: center;
        padding: 15px 0 10px 0;
    }
    .sidebar-brand img {
        width: 150px;
        margin-bottom: 8px;
        filter: drop-shadow(0px 2px 4px rgba(43, 10, 66, 0.15));
    }

    /* Metric Cards Style */
    [data-testid="stMetricValue"] {
        font-size: 1.9rem !important;
        font-weight: 700 !important;
        color: #2B0A42 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #6C5B7B !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    [data-testid="stMetricContainer"] {
        background-color: #FFFFFF;
        border: 1px solid #EADEEF;
        border-top: 4px solid #EAA023;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0px 4px 12px rgba(43, 10, 66, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetricContainer"]:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 16px rgba(43, 10, 66, 0.1);
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #EADEEF;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px;
        background-color: transparent;
        color: #511A72;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B1358 0%, #511A72 100%) !important;
        color: #F3C973 !important;
        box-shadow: 0px 4px 10px rgba(59, 19, 88, 0.25);
    }

    /* Form & Container Borders */
    [data-testid="stForm"], div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: #FFFFFF;
        border-radius: 14px !important;
        border: 1px solid #EADEEF !important;
        box-shadow: 0px 4px 12px rgba(43, 10, 66, 0.03);
    }

    /* Buttons Styling */
    .stButton > button {
        background: linear-gradient(135deg, #EAA023 0%, #D48806 100%) !important;
        color: #2B0A42 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0px 4px 10px rgba(234, 160, 35, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #F3C973 0%, #EAA023 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0px 6px 14px rgba(234, 160, 35, 0.4) !important;
    }

    /* Typography */
    h1, h2, h3 {
        color: #2B0A42 !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# THAI AIRWAYS LOGO URL
THAI_AIRWAYS_LOGO = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRhM8flXc45jVMih04D-lvtqbOvOVkMxdCjGXH2xOlwLA&s=10"

LICENSE_DATABASE_FILE = "manpower_license_data 2.db"
EXCEL_LICENSE_FILE = "manpower_license_data 2.xlsx"
STORE_DATABASE_FILE = "store_inventory.db"
SCHEDULE_DATABASE_FILE = "flight_schedule.db"
LICENSE_COLUMNS = [
    "Personal ID", "Full Name", "Department", "Position", "Employment Status",
    "Privilages", "License No.", "Issue Date", "Expiry Date"
]

# Mapping Aircraft Type -> Required License Privilege
AIRCRAFT_PRIVILEGE_MAP = {
    "A320": "A320",
    "A321": "A320",
    "A32N": "A320",
    "B738": "B737",
    "B7M8": "B737"
}

DEFAULT_CONTRACTS = {
    "TG": "On Call",
    "SQ": "FULL",
    "EY": "FULL",
    "QR": "FULL",
    "MH": "FULL",
    "UO": "FULL",
    "FM": "FULL",
    "TR": "On Call"
}    
# ==============================================================================
# ⚙️ HELPER FUNCTIONS FOR LICENSE SYSTEM
# ==============================================================================
@st.cache_data(ttl=1)
def load_license_data():
    database_exists = os.path.exists(LICENSE_DATABASE_FILE)
    with sqlite3.connect(LICENSE_DATABASE_FILE) as connection:
        connection.execute(f"""
            CREATE TABLE IF NOT EXISTS manpower_license_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                "Personal ID" TEXT NOT NULL,
                "Full Name" TEXT NOT NULL,
                "Department" TEXT,
                "Position" TEXT,
                "Employment Status" TEXT,
                "Privilages" TEXT,
                "License No." TEXT,
                "Issue Date" TEXT,
                "Expiry Date" TEXT
            )
        """)

        if not database_exists and os.path.exists(EXCEL_LICENSE_FILE):
            legacy_df = pd.read_excel(EXCEL_LICENSE_FILE, sheet_name="Manpower_Licenses")
            legacy_df = legacy_df.reindex(columns=LICENSE_COLUMNS)
            legacy_df.to_sql("manpower_license_data", connection, if_exists="append", index=False)

        df = pd.read_sql_query(
            'SELECT "Personal ID", "Full Name", "Department", "Position", '
            '"Employment Status", "Privilages", "License No.", "Issue Date", "Expiry Date" '
            'FROM manpower_license_data ORDER BY id',
            connection,
        )

    for column in ["Issue Date", "Expiry Date"]:
        df[column] = pd.to_datetime(df[column], errors="coerce").dt.date
    return df

def save_license_data(df):
    df_to_save = df.reindex(columns=LICENSE_COLUMNS).copy()
    for column in ["Issue Date", "Expiry Date"]:
        df_to_save[column] = pd.to_datetime(df_to_save[column], errors="coerce").dt.strftime("%Y-%m-%d")

    with sqlite3.connect(LICENSE_DATABASE_FILE) as connection:
        connection.execute("DELETE FROM manpower_license_data")
        df_to_save.to_sql("manpower_license_data", connection, if_exists="append", index=False)
    st.cache_data.clear()

def calculate_status(expiry_date, warning_days=90):
    if pd.isna(expiry_date):
        return "No Expiry"
    today = datetime.now().date()
    warning_date = today + timedelta(days=warning_days)
    
    if expiry_date < today:
        return "Expired"
    elif today <= expiry_date <= warning_date:
        return "Expiring Soon"
    else:
        return "Active"

def color_status_badges(val):
    if val == "Active":
        return 'background-color: #E6F4EA; color: #137333; font-weight: 600; border-radius: 6px; padding: 4px 8px; text-align: center;'
    elif val == "Expiring Soon":
        return 'background-color: #FEF3C7; color: #B45309; font-weight: 600; border-radius: 6px; padding: 4px 8px; text-align: center;'
    elif val == "Expired":
        return 'background-color: #FCE8E6; color: #C5221F; font-weight: 600; border-radius: 6px; padding: 4px 8px; text-align: center;'
    return ''

# ==============================================================================
# ⚙️ HELPER FUNCTIONS FOR STORE EXPIRY ALERTS
# ==============================================================================
def calculate_store_status(val_str, warning_days=90):
    if pd.isna(val_str) or str(val_str).strip().upper() in ["-", "", "ACTIVE", "N/A"]:
        return "Active"
    
    val_upper = str(val_str).strip().upper()
    if val_upper == "UNSERVICEABLE":
        return "UNSERVICEABLE"
        
    try:
        exp_date = pd.to_datetime(val_str).date()
        today = datetime.now().date()
        warning_date = today + timedelta(days=warning_days)
        
        if exp_date < today:
            return "Expired / Overdue"
        elif today <= exp_date <= warning_date:
            return "Expiring Soon"
        else:
            return "Active"
    except Exception:
        return "Active"

def color_store_status(val):
    if val == "Active":
        return 'background-color: #E6F4EA; color: #137333; font-weight: 600;'
    elif val == "Expiring Soon":
        return 'background-color: #FEF3C7; color: #B45309; font-weight: 600;'
    elif val == "Expired / Overdue":
        return 'background-color: #FCE8E6; color: #C5221F; font-weight: 600;'
    elif val == "UNSERVICEABLE":
        return 'background-color: #F1F5F9; color: #475569; font-weight: 600;'
    return ''

@st.cache_data
def get_default_store_data():
    raw_data = [
        {"Item": 1, "Description": "AXLE JACK 95 TONS#AB-73 Malabar", "P/N": "95P10-AR:94861", "S/N": "7360191202", "EQ Code": "30051181", "QTY": "1 EA", "Location": "EQA3", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 2, "Description": "AXLE JACK 95 TONS#AB-70 Malabar", "P/N": "95P10-AR:94861", "S/N": "8178190901", "EQ Code": "30051060", "QTY": "1 EA", "Location": "EQAM", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 3, "Description": "WHEEL&BRAKE CHANGERWB#-13", "P/N": "551340", "S/N": "WTA500:D2020", "EQ Code": "30044508", "QTY": "1 EA", "Location": "EQA5", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 4, "Description": "WHEEL&BRAKE CHANGERWB#-18", "P/N": "16679", "S/N": "175M:W0862", "EQ Code": "30046489", "QTY": "1 EA", "Location": "EQAS", "Next Inspection / Status": "18-Oct-2026", "Source": "Equipment List"},
        {"Item": 5, "Description": "Fine extinguisher cart #36", "P/N": "FC-36", "S/N": "LTDOS", "EQ Code": "40002738", "QTY": "1 EA", "Location": "EQAT", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 6, "Description": "CO-2 FIRE EXTINGUISHER #36/1", "P/N": "CO2-25LBS:TG000", "S/N": "-", "EQ Code": "30037105", "QTY": "1 EA", "Location": "EQAT", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 7, "Description": "CO-2 FIRE EXTINGUISHER #36/2", "P/N": "CO2-25LBS:TG000", "S/N": "-", "EQ Code": "30037106", "QTY": "1 EA", "Location": "EQA3", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 8, "Description": "NITROGEN WITH AXLE JACK#NA-06 (CART)", "P/N": "LTD06", "S/N": "HKTOM-C-06", "EQ Code": "40000334", "QTY": "1 EA", "Location": "EQA3", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 9, "Description": "NITROGEN WITH AXLE JACK#NA-03 (CART)", "P/N": "HKTOM-C-05", "S/N": "-", "EQ Code": "40000331", "QTY": "1 EA", "Location": "EQAA", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 10, "Description": "NITROGEN HIGH PRESS CART", "P/N": "HKTOM-C-03", "S/N": "-", "EQ Code": "40000325", "QTY": "1 EA", "Location": "EQA2", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 11, "Description": "WHEEL ASSY CART", "P/N": "HKTOM-C-02", "S/N": "HKTC02", "EQ Code": "-", "QTY": "1 EA", "Location": "HKTLB-A EQUIPMENT AREA", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 12, "Description": "BRAKE COOLING UNIT CART", "P/N": "HKTOM-C-01", "S/N": "HKTC01", "EQ Code": "-", "QTY": "1 EA", "Location": "HKTLB-A EQUIPMENT AREA", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 13, "Description": "BRAKE COOLING UNIT", "P/N": "BCU-69", "S/N": "-", "EQ Code": "40002647", "QTY": "1 EA", "Location": "HKTLB-A EQUIPMENT AREA", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 14, "Description": "BRAKE COOLING UNIT", "P/N": "BCU-58", "S/N": "-", "EQ Code": "40002636", "QTY": "1 EA", "Location": "HKTLB-A EQUIPMENT AREA", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 15, "Description": "BRAKE COOLING UNIT", "P/N": "BCU-68", "S/N": "-", "EQ Code": "40002650", "QTY": "1 EA", "Location": "HKTLB-A EQUIPMENT AREA", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 16, "Description": "BRAKE COOLING UNIT", "P/N": "BCU-70", "S/N": "-", "EQ Code": "40002652", "QTY": "1 EA", "Location": "HKTLB-A EQUIPMENT AREA", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 17, "Description": "6-Step Aluminum Stepladder", "P/N": "HKT-STEP-02", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "STEP ZONE", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 18, "Description": "5-Step Aluminum Stepladder", "P/N": "HKT-STEP-01", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "STEP ZONE", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 19, "Description": "4-Step Aluminum Stepladder", "P/N": "HKT-STEP-03", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "STEP ZONE", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 20, "Description": "3-Step Aluminum Stepladder", "P/N": "HKT-STEP-04", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "STEP ZONE", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 21, "Description": "MAINT STEP 1M", "P/N": "LT03", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "EQUIPMENT AREA", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 22, "Description": "MAINT STEP 1M", "P/N": "LTOS", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "EQUIPMENT AREA", "Next Inspection / Status": "1-Sep-2026", "Source": "Equipment List"},
        {"Item": 23, "Description": "MAINT STEP 2M", "P/N": "HKTOM-C-13", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "UNSERVICEABLE", "Next Inspection / Status": "UNSERVICEABLE", "Source": "Equipment List"},
        {"Item": 24, "Description": "MAINT STEP 2M", "P/N": "HKTOM-C-14", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "UNSERVICEABLE", "Next Inspection / Status": "UNSERVICEABLE", "Source": "Equipment List"},
        {"Item": 25, "Description": "MAINT STEP 2.5M", "P/N": "HKTOM-C-12", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "UNSERVICEABLE", "Next Inspection / Status": "UNSERVICEABLE", "Source": "Equipment List"},
        {"Item": 26, "Description": "MAINT STEP 3M", "P/N": "HKTOM-C-10", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "UNSERVICEABLE", "Next Inspection / Status": "UNSERVICEABLE", "Source": "Equipment List"},
        {"Item": 27, "Description": "MAINT STEP 3M", "P/N": "HKTOM-C-11", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "UNSERVICEABLE", "Next Inspection / Status": "UNSERVICEABLE", "Source": "Equipment List"},
        {"Item": 28, "Description": "Axle Jack-NLGA320/A321Neo/B737", "P/N": "RH 1606A 1A0A01", "S/N": "1157042", "EQ Code": "30053073", "QTY": "1 EA", "Location": "TOOL STORE/B5", "Next Inspection / Status": "20 NOV 2026", "Source": "Equipment List"},
        {"Item": 29, "Description": "RE-OILING GUN #JET OIL II", "P/N": "UZ/71606//5:TG000", "S/N": "LTJ006", "EQ Code": "30043732", "QTY": "1 EA", "Location": "TOOL STORE/A1", "Next Inspection / Status": "29 NOV 2026", "Source": "Equipment List"},
        {"Item": 30, "Description": "RE-OILING GUN TURBOOIL2197", "P/N": "UZ/7/1606/5 TG000", "S/N": "LT3021", "EQ Code": "30044496", "QTY": "1 EA", "Location": "TOOL STORE/A1", "Next Inspection / Status": "04 MAY 2027", "Source": "Equipment List"},
        {"Item": 31, "Description": "HYD FLUID DISPENSER OIL 2380 Hydraulic Pump", "P/N": "8166", "S/N": "PF53361-BPWS", "EQ Code": "30000840", "QTY": "1 EA", "Location": "TOOL STORE/A2", "Next Inspection / Status": "17 NOV 2026", "Source": "Equipment List"},
        {"Item": 32, "Description": "HEADSET", "P/N": "12506G-07", "S/N": "-", "EQ Code": "-", "QTY": "6 EA", "Location": "HEADSET ZONE", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 33, "Description": "ADJUSTABLE JOINT PLIER", "P/N": "AWP160", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/E", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 34, "Description": "ADJUSTABLE JOINT PLIER", "P/N": "HL120P", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/E", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 35, "Description": "CHAIN WRENCHES", "P/N": "CW15", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/E", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 36, "Description": "Strap wrench 1\" to 5\" Capacity, 22\" lon", "P/N": "YA826A:55719", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/E", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 37, "Description": "AIR PRESSURE", "P/N": "N/A", "S/N": "-", "EQ Code": "-", "QTY": "3 EA", "Location": "TOOL STORE/D", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 38, "Description": "ADAPTER JACK", "P/N": "N/A", "S/N": "-", "EQ Code": "-", "QTY": "2 EA", "Location": "TOOL STORE/D", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 39, "Description": "SPEED DRIVER 1/4", "P/N": "TMS4E", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/E", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 40, "Description": "SPEED HANDLE 3/8", "P/N": "F4LB", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/E", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 41, "Description": "SPEED HANDLE 1/2", "P/N": "S4", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/E", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 42, "Description": "BRAKER BAR 18 INCH 1/2 SQUARE DRIVE", "P/N": "SN18A", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/E", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 43, "Description": "Corwfoot wrench open end 1 1/8\"", "P/N": "SC036", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/E", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 44, "Description": "3/8 IMPACT WRENCH", "P/N": "6151909521", "S/N": "0713K", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/C1", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 45, "Description": "PNEUMATIC HAMMER", "P/N": "T022962:W1291", "S/N": "49C2005-2008", "EQ Code": "30033351", "QTY": "1 EA", "Location": "TOOL STORE/C1", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 46, "Description": "ADAPTER 3/8\"", "P/N": "AIMF", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/C2", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 47, "Description": "DEEP SOCKET 3/8\" DRIVE 13/16\"", "P/N": "SF261", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/C2", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 48, "Description": "DEEP SOCKET 7/8\" DRIVE 1/2\"", "P/N": "S281:TG000", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/C2", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 49, "Description": "BIT HOLDER 1/4\"", "P/N": "FBS8", "S/N": "-", "EQ Code": "-", "QTY": "2 EA", "Location": "TOOL STORE/C2", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 50, "Description": "BIT HOLDER 5/16\"", "P/N": "FBS9", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/C2", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 51, "Description": "BIT HEAD B787", "P/N": "-", "S/N": "-", "EQ Code": "-", "QTY": "1 SET", "Location": "TOOL STORE/C1", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 52, "Description": "BIT, TORX PLUS 15 IP", "P/N": "15IP", "S/N": "-", "EQ Code": "-", "QTY": "19 EA", "Location": "TOOL STORE/C1", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 53, "Description": "BIT, TORX PLUS 25 IP", "P/N": "25IP", "S/N": "-", "EQ Code": "-", "QTY": "21 EA", "Location": "TOOL STORE/C1", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 54, "Description": "BIT, TORX PLUS 30 IP", "P/N": "30IP", "S/N": "-", "EQ Code": "-", "QTY": "20 EA", "Location": "TOOL STORE/C1", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 55, "Description": "MOR TORQ BITS ZMT-1 (440MT1)", "P/N": "MT-1", "S/N": "-", "EQ Code": "-", "QTY": "10 EA", "Location": "TOOL STORE/C1", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 56, "Description": "Bit Screw Driver", "P/N": "AT480-4", "S/N": "-", "EQ Code": "-", "QTY": "10 EA", "Location": "TOOL STORE/C1", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 57, "Description": "Rectangular mirror 2\" x 3\", length 11\"", "P/N": "GA294:W1195", "S/N": "-", "EQ Code": "-", "QTY": "2 EA", "Location": "TOOL STORE/H4", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 58, "Description": "Protecta Shock Absorbing Rope Lanyard", "P/N": "1390370:TG000", "S/N": "006750", "EQ Code": "30054208", "QTY": "1 EA", "Location": "TOOL STORE/C2", "Next Inspection / Status": "10 Jun 2027", "Source": "Common Tool"},
        {"Item": 59, "Description": "Protecta Shock Absorbing Rope Lanyard", "P/N": "1390370:TG000", "S/N": "006833", "EQ Code": "30054212", "QTY": "1 EA", "Location": "TOOL STORE/C2", "Next Inspection / Status": "10 Jun 2027", "Source": "Common Tool"},
        {"Item": 60, "Description": "TOOL BOX AP", "P/N": "HKTOM01", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/A5", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 61, "Description": "TOOL BOX AP", "P/N": "HKTOM03", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/A5", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 62, "Description": "TOOL BOX REI", "P/N": "RE1009/HKTOM", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/A5", "Next Inspection / Status": "Active", "Source": "Common Tool"},
        {"Item": 63, "Description": "OXYGEN TOOL BOX", "P/N": "LT-J/HKTOM", "S/N": "-", "EQ Code": "-", "QTY": "1 EA", "Location": "TOOL STORE/H4", "Next Inspection / Status": "Active", "Source": "Common Tool"}
    ]
    return pd.DataFrame(raw_data)

STORE_COLUMNS = [
    "Item", "Description", "P/N", "S/N", "EQ Code", "QTY", "Location",
    "Next Inspection / Status", "Source"
]

@st.cache_data
def load_store_data():
    database_exists = os.path.exists(STORE_DATABASE_FILE)
    with sqlite3.connect(STORE_DATABASE_FILE) as connection:
        connection.execute('''
            CREATE TABLE IF NOT EXISTS store_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                "Item" INTEGER,
                "Description" TEXT,
                "P/N" TEXT,
                "S/N" TEXT,
                "EQ Code" TEXT,
                "QTY" TEXT,
                "Location" TEXT,
                "Next Inspection / Status" TEXT,
                "Source" TEXT
            )
        ''')

        if not database_exists:
            get_default_store_data().reindex(columns=STORE_COLUMNS).to_sql(
                "store_inventory", connection, if_exists="append", index=False
            )

        return pd.read_sql_query(
            'SELECT "Item", "Description", "P/N", "S/N", "EQ Code", "QTY", '
            '"Location", "Next Inspection / Status", "Source" '
            'FROM store_inventory ORDER BY id',
            connection,
        )

def save_store_data(df):
    df_to_save = df.reindex(columns=STORE_COLUMNS).copy()
    with sqlite3.connect(STORE_DATABASE_FILE) as connection:
        connection.execute("DELETE FROM store_inventory")
        df_to_save.to_sql("store_inventory", connection, if_exists="append", index=False)
    st.cache_data.clear()

# ==============================================================================
# ⚙️ HELPER FUNCTIONS FOR FLIGHT ASSIGNMENT SYSTEM
# ==============================================================================
def parse_flight_assignment_excel(uploaded_file):
    excel_file = pd.ExcelFile(uploaded_file)
    if not excel_file.sheet_names:
        raise ValueError("The uploaded Excel workbook contains no worksheets.")

    latest_sheet = None
    df_raw = None
    header_idx = None
    for sheet_name in reversed(excel_file.sheet_names):
        candidate = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        for idx, row in candidate.iterrows():
            row_str = " ".join(str(val).strip().upper() for val in row.values)
            if "FLT" in row_str and "A/L" in row_str:
                latest_sheet = sheet_name
                df_raw = candidate
                header_idx = idx
                break
        if latest_sheet is not None:
            break

    if latest_sheet is None or df_raw is None or header_idx is None:
        raise ValueError("Could not find a flight schedule sheet with FLT and A/L headers.")

    df_flight = df_raw.iloc[header_idx + 1:, 0:14].copy()
    df_flight.columns = [
        'NO', 'AIRLINE', 'FLIGHT', 'REG', 'STA', 'ATA', 
        'STD', 'ATD', 'AIRCRAFT TYPE', 'MECH 1', 'MECH 2', 'LAE', 'LOG NO', 'THF NO'
    ]
    df_flight = df_flight[pd.to_numeric(df_flight['NO'], errors='coerce').notna()]
    
    df_flight['AIRCRAFT TYPE'] = df_flight['AIRCRAFT TYPE'].astype(str).str.strip().replace({'nan': None, 'None': None, '': None, '-': None, 'N/A': None})
    for col in ['MECH 1', 'MECH 2', 'LAE']:
        df_flight[col] = df_flight[col].astype(str).str.strip().replace({'nan': None, 'None': None, '': None, '-': None})

    df_staff = df_raw.iloc[header_idx + 1:, 18:25].copy()
    df_staff.columns = ['NO', 'NAME', 'PERS ID', 'SKD', 'CD', 'SHIFT IN', 'SHIFT OUT']
    df_staff = df_staff[pd.to_numeric(df_staff['PERS ID'], errors='coerce').notna()]
    df_staff['NAME'] = df_staff['NAME'].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)

    return df_flight, df_staff
def map_aircraft_to_privilege(ac_type):
    if not ac_type or pd.isna(ac_type): return "Unknown"
    ac_clean = str(ac_type).strip().upper()
    return AIRCRAFT_PRIVILEGE_MAP.get(ac_clean, ac_clean)

def extract_hour(time_val):
    if pd.isna(time_val):
        return None
    s = str(time_val).split('.')[0].strip().zfill(4)
    if len(s) >= 4 and s[:2].isdigit():
        hr = int(s[:2])
        if 0 <= hr <= 23:
            return hr
    return None

def get_unique_mechanics_count(df_flight):
    m1 = df_flight['MECH 1'].dropna().tolist()
    m2 = df_flight['MECH 2'].dropna().tolist()
    lae = df_flight['LAE'].dropna().tolist()
    
    unique_mechs = set(m1 + m2 + lae)
    return len(unique_mechs), sorted(list(unique_mechs))

def save_schedule_data(df_flight, df_staff, source_file):
    with sqlite3.connect(SCHEDULE_DATABASE_FILE) as connection:
        df_flight.to_sql("flight_schedule", connection, if_exists="replace", index=False)
        df_staff.to_sql("schedule_staff", connection, if_exists="replace", index=False)
        connection.execute(
            "CREATE TABLE IF NOT EXISTS schedule_metadata "
            "(id INTEGER PRIMARY KEY CHECK (id = 1), source_file TEXT, uploaded_at TEXT)"
        )
        connection.execute("DELETE FROM schedule_metadata")
        connection.execute(
            "INSERT INTO schedule_metadata (id, source_file, uploaded_at) VALUES (1, ?, ?)",
            (source_file, datetime.now().isoformat(timespec="seconds")),
        )

def load_schedule_data():
    if not os.path.exists(SCHEDULE_DATABASE_FILE):
        return None, None, None

    with sqlite3.connect(SCHEDULE_DATABASE_FILE) as connection:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'", connection
        )["name"].tolist()
        required_tables = {"flight_schedule", "schedule_staff", "schedule_metadata"}
        if not required_tables.issubset(tables):
            return None, None, None
        df_flight = pd.read_sql_query("SELECT * FROM flight_schedule", connection)
        df_staff = pd.read_sql_query("SELECT * FROM schedule_staff", connection)
        metadata = pd.read_sql_query(
            "SELECT source_file, uploaded_at FROM schedule_metadata WHERE id = 1",
            connection,
        )

    schedule_info = None
    if not metadata.empty:
        schedule_info = (metadata.iloc[0]["source_file"], metadata.iloc[0]["uploaded_at"])
    return df_flight, df_staff, schedule_info

# ==============================================================================
# 📌 SIDEBAR NAVIGATION (RESTORED SELECTBOX & PURPLE TEXT)
# ==============================================================================
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand">
        <img src="{THAI_AIRWAYS_LOGO}" alt="Thai Airways Logo">
    </div>
    """, unsafe_allow_html=True)
    
    st.title("Phuket Operations")
    st.caption("Technical Department Management")
    st.markdown("---")

    # กลับมาใช้ selectbox ตามเดิม
    system_mode = st.selectbox(
        "📌 Module Selection:",
        [
            "✈️ Flight & Work Assignment", 
            "📜 Manpower & License Management",
            "📦 Store & Inventory Management"
        ]
    )

    st.markdown("---")

# TOP BANNER
st.markdown(f"""
<div class="brand-header">
    <img src="{THAI_AIRWAYS_LOGO}" alt="Thai Airways Logo">
    <div class="brand-header-text">
        <h2>THAI AIRWAYS INTERNATIONAL</h2>
        <p>Integrated Technical & Flight Operations Management System</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# ✈️ MODE 1: FLIGHT & WORK ASSIGNMENT SYSTEM
# ==============================================================================
if system_mode == "✈️ Flight & Work Assignment":
    st.title("✈️ Flight Schedule & Work Assignment System")
    st.caption("Extract and analyze flight schedules, aircraft types, assigned mechanics, and shift distribution.")
    st_autorefresh(interval=10000, key="schedule_refresh")
    
    with st.container(border=True):
        uploaded_files = st.file_uploader(
            "📂 Upload Daily Schedule Excel File(s) (e.g., TUE 28 JUL 2026.xlsx)",
            type=["xlsx", "xls"],
            accept_multiple_files=True,
        )

    if uploaded_files or os.path.exists(SCHEDULE_DATABASE_FILE):
        try:
            if uploaded_files:
                uploaded_file = uploaded_files[-1]
                st.caption(f"Reading latest uploaded file: {uploaded_file.name}")
                df_flight, df_staff = parse_flight_assignment_excel(uploaded_file)
                save_schedule_data(df_flight, df_staff, uploaded_file.name)
            else:
                df_flight, df_staff, schedule_info = load_schedule_data()
                if df_flight is None:
                    raise ValueError("The saved schedule database is not available.")
                source_file, uploaded_at = schedule_info
                st.caption(f"Latest shared schedule: {source_file} (uploaded {uploaded_at})")
            unique_mech_count, unique_mech_list = get_unique_mechanics_count(df_flight)

            valid_flights = len(df_flight[df_flight['AIRLINE'].notna() & (df_flight['AIRLINE'].astype(str).str.strip() != '')])
            
            valid_ac_types = df_flight['AIRCRAFT TYPE'].dropna()
            valid_ac_types = valid_ac_types[~valid_ac_types.isin(['N/A', 'None', '-'])]
            
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("✈️ Total Flights", f"{valid_flights}")
            m2.metric("🛩️ Aircraft Types", f"{valid_ac_types.nunique()}")
            m3.metric("👷 STAFF on Duty", f"{unique_mech_count}")
            m4.metric("👥 Total Staff", f"{len(df_staff)}")
            m5.metric("🛠️ LAE Flights", f"{len(df_flight[df_flight['LAE'].notna()])}")

            st.write("##")

            tab_flight, tab_workload, tab_chart, tab_staff, tab_search = st.tabs([
                "📋 Flight Schedule", 
                "📊 Workload Distribution",
                "📈 Peak Hours Analysis",
                "👥 Duty Roster", 
                "🔍 Search Assignment"
            ])

            with tab_flight:
                with st.container(border=True):
                    col_filter1, col_filter2 = st.columns([1, 2])
                    with col_filter1:
                        unique_ac_list = sorted(list(valid_ac_types.unique()))
                        all_ac_types = ["All Types"] + unique_ac_list
                        selected_ac = st.selectbox("🛩️ Filter Aircraft Type:", all_ac_types)
                    
                    filtered_flight_df = df_flight.copy()
                    filtered_flight_df = filtered_flight_df[
                        filtered_flight_df['AIRLINE'].notna() | filtered_flight_df['FLIGHT'].notna()
                    ]

                    if selected_ac != "All Types":
                        filtered_flight_df = filtered_flight_df[filtered_flight_df['AIRCRAFT TYPE'] == selected_ac]
                    
                    display_df = filtered_flight_df.fillna("-")

                    st.write(f"Showing **{len(display_df)}** flights")
                    st.dataframe(display_df, use_container_width=True, hide_index=True)

            with tab_workload:
                workload_data = []
                for mech in unique_mech_list:
                    mech_flights = df_flight[
                        (df_flight['MECH 1'] == mech) | 
                        (df_flight['MECH 2'] == mech) | 
                        (df_flight['LAE'] == mech)
                    ]
                    
                    workload_data.append({
                        "Name": mech,
                        "Total Flight Duty": len(mech_flights),
                        "MECH 1": len(df_flight[df_flight['MECH 1'] == mech]),
                        "MECH 2": len(df_flight[df_flight['MECH 2'] == mech]),
                        "LAE": len(df_flight[df_flight['LAE'] == mech])
                    })
                
                df_workload = pd.DataFrame(workload_data).sort_values(by="Total Flight Duty", ascending=False)
                
                with st.container(border=True):
                    col_wl1, col_wl2 = st.columns([2, 3])
                    with col_wl1:
                        st.subheader("Mechanic Duty Summary")
                        st.dataframe(df_workload, use_container_width=True, hide_index=True)
                    with col_wl2:
                        st.subheader("Workload Chart")
                        st.bar_chart(df_workload.set_index("Name")["Total Flight Duty"], color="#3B1358")

            with tab_chart:
                df_flight['STA_Hour'] = df_flight['STA'].apply(extract_hour)
                df_flight['STD_Hour'] = df_flight['STD'].apply(extract_hour)

                hours = [f"{h:02d}:00" for h in range(24)]
                sta_counts = [df_flight['STA_Hour'].value_counts().get(h, 0) for h in range(24)]
                std_counts = [df_flight['STD_Hour'].value_counts().get(h, 0) for h in range(24)]

                chart_data = pd.DataFrame({
                    "Time Slot": hours,
                    "Arrivals (STA)": sta_counts,
                    "Departures (STD)": std_counts,
                    "Total Operations": [sta + std for sta, std in zip(sta_counts, std_counts)]
                }).set_index("Time Slot")

                with st.container(border=True):
                    st.bar_chart(chart_data[["Arrivals (STA)", "Departures (STD)"]], color=["#511A72", "#EAA023"])

                    max_ops = chart_data["Total Operations"].max()
                    peak_hours = chart_data[chart_data["Total Operations"] == max_ops].index.tolist()
                    peak_str = ", ".join(peak_hours) if peak_hours else "N/A"

                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.info(f"🔥 **Peak Traffic Hours:** {peak_str} ({max_ops} Total Ops)")
                    with col_info2:
                        st.success("💡 **Roster Optimization:** Ensure extra technical staff are allocated during peak hours.")

            with tab_staff:
                with st.container(border=True):
                    col_skd1, _ = st.columns([1, 2])
                    with col_skd1:
                        skd_filter = st.selectbox("📌 Filter Shift Pattern:", ["ALL STAFF", "DAY SHIFT", "NIGHT SHIFT"])
                    
                    df_staff_show = df_staff.copy()
                    if skd_filter == "DAY SHIFT":
                        df_staff_show = df_staff_show[df_staff_show['SKD'] == 'D']
                    elif skd_filter == "NIGHT SHIFT":
                        df_staff_show = df_staff_show[df_staff_show['SKD'] == 'N']
                    elif skd_filter == "ALL STAFF":
                        df_staff_show = df_staff_show[df_staff_show['SKD'].isin(['D', 'N', 'OT', '63', '64', '41', '13', '21'])]

                    st.dataframe(df_staff_show, use_container_width=True, hide_index=True)

            with tab_search:
                with st.container(border=True):
                    tech_code = st.selectbox("Select or Search Mechanic Initial:", [""] + unique_mech_list)
                    if tech_code:
                        query = tech_code.strip().upper()
                        matched = df_flight[
                            df_flight['MECH 1'].astype(str).str.contains(query, case=False, na=False) |
                            df_flight['MECH 2'].astype(str).str.contains(query, case=False, na=False) |
                            df_flight['LAE'].astype(str).str.contains(query, case=False, na=False)
                        ]
                        st.success(f"Assigned to **{len(matched)}** flights:")
                        st.dataframe(matched[['NO', 'AIRLINE', 'FLIGHT', 'AIRCRAFT TYPE', 'STA', 'STD', 'MECH 1', 'MECH 2', 'LAE']], use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Error parsing file structure: {e}")
    else:
        st.info("👋 Please upload a daily flight schedule Excel file to display data.")

# ==============================================================================

    

# ==============================================================================
# 📜 MODE 3: MANPOWER & LICENSE MANAGEMENT SYSTEM
# ==============================================================================
elif system_mode == "📜 Manpower & License Management":
    with st.sidebar:
        menu = st.selectbox(
            "📌 Management Menu:",
            ["📊 Dashboard Overview", "🚨 License Alerts", "🔍 Staff Directory", "➕ Add New Entry"]
        )

    df_lic = load_license_data()
    if not df_lic.empty:
        df_lic["License Status"] = df_lic["Expiry Date"].apply(lambda x: calculate_status(x))
    else:
        df_lic["License Status"] = []

    if menu == "📊 Dashboard Overview":
        st.title("📊 Manpower & License Overview")
        st.caption("Overview of personnel headcount and license status tracking.")

        if df_lic.empty:
            st.warning("No license records found. Please add entries in the 'Add New Entry' tab.")
        else:
            total_emp = df_lic["Personal ID"].nunique()
            privilege_values = df_lic["Privilages"].fillna("").astype(str).str.strip().str.upper()
            excluded_privileges = {"", "NONE", "N/A", "-", "NULL", "NAN"}
            total_licenses = (~privilege_values.isin(excluded_privileges)).sum()
            active_cnt = sum(df_lic["License Status"] == "Active")
            expiring_cnt = sum(df_lic["License Status"] == "Expiring Soon")
            expired_cnt = sum(df_lic["License Status"] == "Expired")

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("👥 Total Staff", f"{total_emp}")
            c2.metric("📜 Licenses", f"{total_licenses}")
            c3.metric("✅ Active", f"{active_cnt}")
            c4.metric("⚠️ Expiring Soon", f"{expiring_cnt}")
            c5.metric("❌ Expired", f"{expired_cnt}")

            st.write("##")

            with st.container(border=True):
                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    st.subheader("🏢 Headcount by Position")
                    dept_counts = df_lic.groupby("Position")["Personal ID"].nunique().reset_index()
                    st.bar_chart(dept_counts.set_index("Position"), color="#511A72")
                with col_chart2:
                    st.subheader("📌 License Status Breakdown")
                    st.dataframe(
                        df_lic["License Status"].value_counts().reset_index(),
                        use_container_width=True, hide_index=True
                    )

            st.write("### 📜 Recent License Records")
            st.caption("Edit personnel or license information directly, then save your changes.")
            editable_license_df = df_lic[LICENSE_COLUMNS].copy()
            edited_license_df = st.data_editor(
                editable_license_df,
                use_container_width=True,
                hide_index=True,
                key="recent_license_records_editor",
                column_config={
                    "Issue Date": st.column_config.DateColumn("Issue Date"),
                    "Expiry Date": st.column_config.DateColumn("Expiry Date"),
                },
            )
            if st.button("💾 Save License Updates", use_container_width=True):
                save_license_data(edited_license_df)
                st.success("License information updated successfully.")
                st.rerun()

    elif menu == "🚨 License Alerts":
        st.title("🚨 License Expiry Monitoring")
        
        with st.container(border=True):
            days_threshold = st.slider("Select Warning Threshold (Days Prior to Expiry):", 15, 180, 90, 15)
        
        df_lic["Dynamic_Status"] = df_lic["Expiry Date"].apply(lambda x: calculate_status(x, warning_days=days_threshold))
        expired_df = df_lic[df_lic["Dynamic_Status"] == "Expired"]
        expiring_df = df_lic[df_lic["Dynamic_Status"] == "Expiring Soon"]

        tab1, tab2 = st.tabs([f"⚠️ Expiring within {days_threshold} Days ({len(expiring_df)})", f"❌ Expired ({len(expired_df)})"])
        
        with tab1:
            with st.container(border=True):
                st.warning(f"Found **{len(expiring_df)}** licenses requiring urgent renewal.")
                styled_expiring = expiring_df[["Personal ID", "Full Name", "Department", "Position", "Privilages", "License No.", "Expiry Date", "Dynamic_Status"]].style.map(
                    color_status_badges, subset=["Dynamic_Status"]
                )
                st.dataframe(styled_expiring, use_container_width=True, hide_index=True)
            
        with tab2:
            with st.container(border=True):
                st.error(f"Found **{len(expired_df)}** expired licenses.")
                styled_expired = expired_df[["Personal ID", "Full Name", "Department", "Position", "Privilages", "License No.", "Expiry Date", "Dynamic_Status"]].style.map(
                    color_status_badges, subset=["Dynamic_Status"]
                )
                st.dataframe(styled_expired, use_container_width=True, hide_index=True)

    elif menu == "🔍 Staff Directory":
        st.title("🔍 Staff Directory & Search")
        
        with st.container(border=True):
            search_term = st.text_input("🔎 Search by Name, Personal ID, or Privilege:")
            
        filtered_df = df_lic.copy()
        if search_term:
            term = search_term.lower()
            filtered_df = filtered_df[
                filtered_df["Full Name"].astype(str).str.lower().str.contains(term) |
                filtered_df["Personal ID"].astype(str).str.lower().str.contains(term) |
                filtered_df["Privilages"].astype(str).str.lower().str.contains(term)
            ]
            
        styled_filtered = filtered_df.style.map(color_status_badges, subset=["License Status"])
        st.dataframe(styled_filtered, use_container_width=True, hide_index=True)

    elif menu == "➕ Add New Entry":
        st.title("➕ Add Personnel / License Record")
        
        with st.form("add_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                emp_id = st.text_input("Personal ID*")
                full_name = st.text_input("Full Name*")
                department = st.selectbox("Department", ["Technical Department Phuket Station", "HKTLB-A", "BKKLB-A", "BKKLC", "DL", "DT", "ADMIN"])
                position = st.text_input("Position")
                emp_status = st.selectbox("Employment Status", ["Full-Time", "Part-Time", "Contract"])
            with col_b:
                privilages = st.text_input("License Name / Privilege")
                license_no = st.text_input("License No.")
                issue_date = st.date_input("Issue Date", value=datetime.now().date())
                expiry_date = st.date_input("Expiry Date", value=datetime.now().date() + timedelta(days=365))

            submitted = st.form_submit_button("💾 Save New Record", use_container_width=True)
            if submitted and emp_id and full_name:
                new_row = {
                    "Personal ID": emp_id, "Full Name": full_name, "Department": department,
                    "Position": position, "Employment Status": emp_status, "Privilages": privilages,
                    "License No.": license_no, "Issue Date": issue_date, "Expiry Date": expiry_date
                }
                raw_df = load_license_data()
                updated_df = pd.concat([raw_df, pd.DataFrame([new_row])], ignore_index=True)
                save_license_data(updated_df)
                st.success(f"Successfully recorded data for {full_name}!")
                st.rerun()

# ==============================================================================
# 📦 MODE 4: STORE & INVENTORY MANAGEMENT
# ==============================================================================
elif system_mode == "📦 Store & Inventory Management":
    st.title("📦 Technical Store & Inspection Alert System")
    st.caption("Phuket Station Inventory Database & Expiration / Calibration Monitoring")

    df_store = load_store_data()

    with st.container(border=True):
        col_warn, _ = st.columns([1, 1])
        with col_warn:
            warning_days = st.slider("⚙️ Inspection Alert Threshold (Days Prior):", 15, 180, 90, 15)

    df_store["Inspection Status"] = df_store["Next Inspection / Status"].apply(
        lambda x: calculate_store_status(x, warning_days=warning_days)
    )

    total_items = len(df_store)
    exp_soon_count = sum(df_store["Inspection Status"] == "Expiring Soon")
    expired_count = sum(df_store["Inspection Status"] == "Expired / Overdue")
    unserv_count = sum(df_store["Inspection Status"] == "UNSERVICEABLE")
    active_count = sum(df_store["Inspection Status"] == "Active")

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("📦 Total Items", f"{total_items}")
    s2.metric("✅ Active / OK", f"{active_count}")
    s3.metric("⚠️ Expiring Soon", f"{exp_soon_count}")
    s4.metric("❌ Overdue / Expired", f"{expired_count}")
    s5.metric("🚫 Unserviceable", f"{unserv_count}")

    st.write("##")

    tab_alerts, tab_all_store, tab_filter_source, tab_search_store = st.tabs([
        f"🚨 Inspection & Expiry Alerts ({exp_soon_count + expired_count})",
        "📋 Full Inventory Master Database", 
        "📂 Filter by Category", 
        "🔍 Search Part / Equipment"
    ])

    with tab_alerts:
        expiring_df = df_store[df_store["Inspection Status"] == "Expiring Soon"]
        expired_df = df_store[df_store["Inspection Status"] == "Expired / Overdue"]

        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            with st.container(border=True):
                st.subheader(f"⚠️ Near Inspection Due ({len(expiring_df)})")
                if not expiring_df.empty:
                    st.warning(f"Items due for inspection/calibrate within {warning_days} days:")
                    styled_expiring = expiring_df[["Item", "Description", "P/N", "S/N", "Location", "Next Inspection / Status", "Inspection Status"]].style.map(
                        color_store_status, subset=["Inspection Status"]
                    )
                    st.dataframe(styled_expiring, use_container_width=True, hide_index=True)
                else:
                    st.success("No items requiring immediate inspection within the selected timeframe.")

        with col_a2:
            with st.container(border=True):
                st.subheader(f"❌ Overdue / Expired ({len(expired_df)})")
                if not expired_df.empty:
                    st.error("Items that have passed their inspection or calibration date:")
                    styled_expired = expired_df[["Item", "Description", "P/N", "S/N", "Location", "Next Inspection / Status", "Inspection Status"]].style.map(
                        color_store_status, subset=["Inspection Status"]
                    )
                    st.dataframe(styled_expired, use_container_width=True, hide_index=True)
                else:
                    st.success("No overdue equipment found.")

    with tab_all_store:
        with st.container(border=True):
            st.subheader("📦 Update Inventory Master List")
            st.caption("Edit cells or use the table menu to add and delete inventory rows.")
            editable_store_df = df_store[STORE_COLUMNS].copy()
            edited_store_df = st.data_editor(
                editable_store_df,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key="store_inventory_editor",
            )
            if st.button("💾 Save Inventory Updates", use_container_width=True):
                save_store_data(edited_store_df)
                st.success("Inventory list updated successfully.")
                st.rerun()

    with tab_filter_source:
        with st.container(border=True):
            c_f1, c_f2, c_f3 = st.columns(3)
            with c_f1:
                selected_source = st.selectbox("Select Source Document:", ["ALL", "Equipment List", "Common Tool"])
            with c_f2:
                selected_loc = st.selectbox("Select Location Zone:", ["ALL"] + sorted(list(df_store['Location'].unique())))
            with c_f3:
                selected_status = st.selectbox("Select Inspection Status:", ["ALL", "Active", "Expiring Soon", "Expired / Overdue", "UNSERVICEABLE"])

            df_filtered = df_store.copy()
            if selected_source != "ALL":
                df_filtered = df_filtered[df_filtered["Source"] == selected_source]
            if selected_loc != "ALL":
                df_filtered = df_filtered[df_filtered["Location"] == selected_loc]
            if selected_status != "ALL":
                df_filtered = df_filtered[df_filtered["Inspection Status"] == selected_status]

            st.write(f"Showing **{len(df_filtered)}** items:")
            styled_filtered = df_filtered.style.map(color_store_status, subset=["Inspection Status"])
            st.dataframe(styled_filtered, use_container_width=True, hide_index=True)

    with tab_search_store:
        with st.container(border=True):
            st.subheader("🔍 Quick Search Store Items")
            kw = st.text_input("Enter Part Number, Description, Serial No., or Location Zone:")
            if kw:
                matched_df = df_store[
                    df_store["Description"].astype(str).str.contains(kw, case=False, na=False) |
                    df_store["P/N"].astype(str).str.contains(kw, case=False, na=False) |
                    df_store["S/N"].astype(str).str.contains(kw, case=False, na=False) |
                    df_store["Location"].astype(str).str.contains(kw, case=False, na=False)
                ]
                st.success(f"Found **{len(matched_df)}** matching records:")
                styled_matched = matched_df.style.map(color_store_status, subset=["Inspection Status"])
                st.dataframe(styled_matched, use_container_width=True, hide_index=True)

else:
    st.info("👋 Select modules in the sidebar to navigate.")