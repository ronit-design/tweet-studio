# utils/data.py
# All static data: categories, countries, calendar releases

US_CATEGORIES = [
    {
        "id": "regional-fed", "icon": "🏦", "name": "Regional Fed Surveys",
        "ex": "KC, Richmond, Dallas, Philly",
        "releases": [
            "Kansas City Fed Manufacturing", "Kansas City Fed Services",
            "Richmond Fed Manufacturing", "Philadelphia Fed Manufacturing",
            "Dallas Fed Manufacturing", "Empire State Manufacturing"
        ],
        "subcomps": ["employment", "new orders", "capex plans", "input prices",
                     "hours worked", "shipments", "inventories", "six-month outlook"]
    },
    {
        "id": "consumer-sentiment", "icon": "📊", "name": "Consumer Sentiment",
        "ex": "UMich, Conference Board",
        "releases": [
            "UMich Consumer Sentiment (final)", "UMich Consumer Sentiment (preliminary)",
            "Conference Board Consumer Confidence", "UMich 1yr Inflation Expectations",
            "UMich 5yr Inflation Expectations"
        ],
        "subcomps": ["current conditions", "expectations index", "1yr inflation expectations",
                     "5yr inflation expectations", "buying conditions", "personal finances"]
    },
    {
        "id": "mortgage-rates", "icon": "🏠", "name": "Mortgage & Housing",
        "ex": "MBA apps, rates, starts",
        "releases": [
            "MBA Mortgage Applications", "30yr Fixed Mortgage Rate", "Housing Starts",
            "Existing Home Sales", "Case-Shiller Home Price Index", "NAHB Housing Market Index"
        ],
        "subcomps": ["purchase index", "refinance index", "rate level vs prior week",
                     "single-family vs multi-family", "affordability index"]
    },
    {
        "id": "import-prices", "icon": "📦", "name": "Import Prices & Inflation",
        "ex": "Import prices, PPI, PCE",
        "releases": [
            "Import Price Index", "Export Price Index", "PPI Final Demand",
            "Core PCE Deflator", "CPI ex food & energy", "Sticky CPI (Atlanta Fed)"
        ],
        "subcomps": ["ex-petroleum", "ex-food & fuel", "goods vs services",
                     "YoY vs MoM", "fuel vs non-fuel", "capital goods prices"]
    },
    {
        "id": "energy-commodities", "icon": "⚡", "name": "Energy & Commodities",
        "ex": "EIA, petroleum, prices",
        "releases": [
            "EIA Petroleum Status Report", "U.S. Net Petroleum Export Position",
            "Natural Gas Storage (EIA)", "Electricity Rates (EIA)", "Baker Hughes Rig Count"
        ],
        "subcomps": ["crude inventories", "net exports vs imports", "production levels",
                     "refinery utilization", "price vs prior week"]
    },
    {
        "id": "manufacturing-capex", "icon": "🏭", "name": "Manufacturing & Capex",
        "ex": "ISM, skills gap, capex",
        "releases": [
            "ISM Manufacturing PMI", "ISM Services PMI", "Industrial Production",
            "Capacity Utilization", "Durable Goods Orders", "Factory Orders"
        ],
        "subcomps": ["new orders", "production", "employment", "supplier deliveries",
                     "inventories", "prices paid", "capex plans", "backlog"]
    },
    {
        "id": "sector-breadth", "icon": "📈", "name": "Sector Performance",
        "ex": "Breadth, rotation, factor",
        "releases": [
            "S&P 500 Sector Performance", "NYSE Advance/Decline",
            "New Highs vs New Lows", "Equal-Weight vs Cap-Weight Spread",
            "Factor Performance", "VIX & volatility surface"
        ],
        "subcomps": ["energy", "utilities", "staples", "financials", "tech",
                     "healthcare", "breadth ratio", "participation rate"]
    },
    {
        "id": "fiscal-debt", "icon": "💸", "name": "Fiscal & Debt",
        "ex": "National debt, deficit, CBO",
        "releases": [
            "U.S. National Debt Level", "Monthly Budget Statement (Treasury)",
            "CBO Budget Outlook", "Treasury Auction Results",
            "Federal Deficit YTD", "Interest Expense on Debt"
        ],
        "subcomps": ["debt as % of GDP", "net interest expense", "auction bid-to-cover",
                     "foreign holdings", "deficit vs prior year"]
    },
]

INTL_CATEGORIES = {
    "CN": {
        "id": "cn-macro", "icon": "🇨🇳", "name": "China", "ex": "Caixin PMI, CPI, trade",
        "releases": [
            "China Caixin Manufacturing PMI", "China Caixin Services PMI",
            "China Official NBS PMI", "China CPI & PPI",
            "China Trade Balance", "China Retail Sales",
            "China Industrial Production", "China GDP"
        ],
        "subcomps": ["new export orders", "input prices", "output prices", "employment",
                     "NBS vs Caixin divergence", "property sector drag"]
    },
    "JP": {
        "id": "jp-macro", "icon": "🇯🇵", "name": "Japan", "ex": "Tankan, CPI, BoJ policy",
        "releases": [
            "Japan Tankan Survey (BoJ)", "Japan CPI (National)",
            "Japan Core CPI ex food & energy", "Japan Industrial Production",
            "Japan Trade Balance", "Bank of Japan Policy Rate Decision", "Japan GDP"
        ],
        "subcomps": ["large manufacturers index", "capex plans", "yen impact",
                     "import prices", "service inflation", "wage growth"]
    },
    "KR": {
        "id": "kr-macro", "icon": "🇰🇷", "name": "South Korea", "ex": "Trade, exports, BoK",
        "releases": [
            "South Korea Exports (monthly)", "South Korea Semiconductor Exports",
            "Bank of Korea Policy Rate Decision", "South Korea CPI",
            "South Korea Industrial Production", "South Korea GDP"
        ],
        "subcomps": ["chip exports YoY", "auto exports", "current account balance",
                     "export orders", "capacity utilization"]
    },
    "IN": {
        "id": "in-macro", "icon": "🇮🇳", "name": "India", "ex": "PMI, CPI, RBI policy",
        "releases": [
            "India Manufacturing PMI (S&P Global)", "India Services PMI",
            "India CPI Inflation", "India Industrial Production",
            "RBI Policy Rate Decision", "India GDP",
            "India Trade Balance", "India FX Reserves"
        ],
        "subcomps": ["new orders", "output prices", "employment",
                     "rural vs urban inflation", "food inflation", "core inflation"]
    },
    "EU": {
        "id": "eu-macro", "icon": "🇪🇺", "name": "European Union", "ex": "PMI, CPI, ECB",
        "releases": [
            "Eurozone Manufacturing PMI (flash)", "Eurozone Services PMI (flash)",
            "Eurozone CPI (flash)", "Eurozone Core CPI",
            "ECB Policy Rate Decision", "Eurozone GDP",
            "Germany IFO Business Climate", "Germany ZEW Sentiment", "Eurozone Unemployment"
        ],
        "subcomps": ["Germany vs France divergence", "input costs", "output prices",
                     "new export orders", "employment", "services vs manufacturing split"]
    },
    "UK": {
        "id": "uk-macro", "icon": "🇬🇧", "name": "United Kingdom", "ex": "PMI, CPI, BoE",
        "releases": [
            "UK Manufacturing PMI", "UK Services PMI", "UK CPI", "UK Core CPI",
            "Bank of England Policy Rate Decision", "UK GDP",
            "UK Employment Report", "UK Retail Sales", "UK Trade Balance"
        ],
        "subcomps": ["input vs output prices", "wage growth", "services CPI",
                     "housing costs", "consumer confidence", "public sector borrowing"]
    },
}

COUNTRIES = [
    {"id": "CN", "flag": "🇨🇳", "name": "China",       "color": "#c23b22"},
    {"id": "JP", "flag": "🇯🇵", "name": "Japan",       "color": "#8b1a1a"},
    {"id": "KR", "flag": "🇰🇷", "name": "South Korea", "color": "#003580"},
    {"id": "IN", "flag": "🇮🇳", "name": "India",       "color": "#ff7900"},
    {"id": "EU", "flag": "🇪🇺", "name": "EU",          "color": "#003399"},
    {"id": "UK", "flag": "🇬🇧", "name": "UK",          "color": "#012169"},
]

# Calendar: recurring release schedule (approximate, for planning)
CALENDAR_RELEASES = [
    # US
    {"name": "Initial Jobless Claims",          "country": "US", "flag": "🇺🇸", "freq": "weekly",    "note": "Every Thursday 8:30am ET",         "weekday": 3},
    {"name": "MBA Mortgage Applications",        "country": "US", "flag": "🇺🇸", "freq": "weekly",    "note": "Every Wednesday",                  "weekday": 2},
    {"name": "EIA Petroleum Status Report",      "country": "US", "flag": "🇺🇸", "freq": "weekly",    "note": "Every Wednesday",                  "weekday": 2},
    {"name": "UMich Consumer Sentiment (prelim)","country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "2nd Friday of month",              "day_offset": 8},
    {"name": "UMich Consumer Sentiment (final)", "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "Last Friday of month",             "day_offset": 22},
    {"name": "ISM Manufacturing PMI",            "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "1st business day of month",        "day_offset": 1},
    {"name": "ISM Services PMI",                 "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "3rd business day of month",        "day_offset": 3},
    {"name": "Nonfarm Payrolls",                 "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "1st Friday of month 8:30am ET",    "day_offset": 5},
    {"name": "CPI",                              "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "~2nd week of month",               "day_offset": 11},
    {"name": "Core PCE Deflator",                "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "Last week of month",               "day_offset": 26},
    {"name": "PPI Final Demand",                 "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "~2nd week of month",               "day_offset": 13},
    {"name": "Retail Sales",                     "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "~2nd week of month",               "day_offset": 15},
    {"name": "Import Price Index",               "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "~2nd week of month",               "day_offset": 14},
    {"name": "Industrial Production",            "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "~3rd week of month",               "day_offset": 17},
    {"name": "Durable Goods Orders",             "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "~4th week of month",               "day_offset": 24},
    {"name": "Housing Starts",                   "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "~3rd week of month",               "day_offset": 18},
    {"name": "Philadelphia Fed Manufacturing",   "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "3rd Thursday of month",            "day_offset": 16},
    {"name": "Kansas City Fed Manufacturing",    "country": "US", "flag": "🇺🇸", "freq": "monthly",   "note": "Last Thursday of month",           "day_offset": 27},
    {"name": "GDP Advance Estimate",             "country": "US", "flag": "🇺🇸", "freq": "quarterly", "note": "~4 weeks after quarter end",        "day_offset": 28},
    {"name": "FOMC Meeting / Rate Decision",     "country": "US", "flag": "🇺🇸", "freq": "6-weekly",  "note": "8 meetings per year",              "day_offset": 42},
    # International
    {"name": "China Caixin Manufacturing PMI",   "country": "CN", "flag": "🇨🇳", "freq": "monthly",   "note": "1st business day of month",        "day_offset": 1},
    {"name": "China Caixin Services PMI",        "country": "CN", "flag": "🇨🇳", "freq": "monthly",   "note": "~3rd business day of month",       "day_offset": 3},
    {"name": "China Official NBS PMI",           "country": "CN", "flag": "🇨🇳", "freq": "monthly",   "note": "Last day of month",                "day_offset": 30},
    {"name": "China CPI & PPI",                  "country": "CN", "flag": "🇨🇳", "freq": "monthly",   "note": "~2nd week of month",               "day_offset": 10},
    {"name": "China Trade Balance",              "country": "CN", "flag": "🇨🇳", "freq": "monthly",   "note": "~2nd week of month",               "day_offset": 12},
    {"name": "Japan Tankan Survey",              "country": "JP", "flag": "🇯🇵", "freq": "quarterly", "note": "1st business day after quarter end","day_offset": 2},
    {"name": "Japan CPI (National)",             "country": "JP", "flag": "🇯🇵", "freq": "monthly",   "note": "3rd week of month",                "day_offset": 20},
    {"name": "Bank of Japan Policy Decision",    "country": "JP", "flag": "🇯🇵", "freq": "6-weekly",  "note": "~8 meetings per year",             "day_offset": 38},
    {"name": "Japan Industrial Production",      "country": "JP", "flag": "🇯🇵", "freq": "monthly",   "note": "Last week of month",               "day_offset": 29},
    {"name": "South Korea Exports",              "country": "KR", "flag": "🇰🇷", "freq": "monthly",   "note": "1st day of month",                 "day_offset": 1},
    {"name": "South Korea Semiconductor Exports","country": "KR", "flag": "🇰🇷", "freq": "monthly",   "note": "1st day of month",                 "day_offset": 1},
    {"name": "Bank of Korea Rate Decision",      "country": "KR", "flag": "🇰🇷", "freq": "6-weekly",  "note": "~6 meetings per year",             "day_offset": 35},
    {"name": "India Manufacturing PMI",          "country": "IN", "flag": "🇮🇳", "freq": "monthly",   "note": "1st business day of month",        "day_offset": 1},
    {"name": "India CPI Inflation",              "country": "IN", "flag": "🇮🇳", "freq": "monthly",   "note": "~2nd week of month",               "day_offset": 12},
    {"name": "RBI Policy Rate Decision",         "country": "IN", "flag": "🇮🇳", "freq": "6-weekly",  "note": "~6 meetings per year",             "day_offset": 30},
    {"name": "Eurozone Manufacturing PMI (flash)","country": "EU","flag": "🇪🇺", "freq": "monthly",   "note": "~3rd week of month",               "day_offset": 21},
    {"name": "Eurozone Services PMI (flash)",    "country": "EU", "flag": "🇪🇺", "freq": "monthly",   "note": "~3rd week of month",               "day_offset": 21},
    {"name": "Eurozone CPI (flash)",             "country": "EU", "flag": "🇪🇺", "freq": "monthly",   "note": "Last week of month",               "day_offset": 28},
    {"name": "ECB Policy Rate Decision",         "country": "EU", "flag": "🇪🇺", "freq": "6-weekly",  "note": "~6 meetings per year",             "day_offset": 44},
    {"name": "Germany IFO Business Climate",     "country": "EU", "flag": "🇪🇺", "freq": "monthly",   "note": "~3rd week of month",               "day_offset": 22},
    {"name": "UK Manufacturing PMI",             "country": "UK", "flag": "🇬🇧", "freq": "monthly",   "note": "1st business day of month",        "day_offset": 1},
    {"name": "UK CPI",                           "country": "UK", "flag": "🇬🇧", "freq": "monthly",   "note": "~3rd week of month",               "day_offset": 19},
    {"name": "Bank of England Rate Decision",    "country": "UK", "flag": "🇬🇧", "freq": "8-per-year","note": "~8 meetings per year",             "day_offset": 40},
    {"name": "UK GDP (monthly)",                 "country": "UK", "flag": "🇬🇧", "freq": "monthly",   "note": "~6 weeks after reference month",   "day_offset": 42},
]

COUNTRY_COLORS = {
    "US": "#1a4a8a",
    "CN": "#c23b22",
    "JP": "#8b1a1a",
    "KR": "#003580",
    "IN": "#ff7900",
    "EU": "#003399",
    "UK": "#012169",
}
