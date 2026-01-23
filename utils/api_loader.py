import requests
import pandas as pd
import streamlit as st
from functools import lru_cache

class WorldBankAPILoader:
    """
    Dynamic data loader using the World Bank Open Data API
    Focuses on South Asian countries: Afghanistan, Bangladesh, Bhutan, India, Maldives, Nepal, Pakistan, Sri Lanka
    """
    
    BASE_URL = "https://api.worldbank.org/v2/"
    SOUTH_ASIA_ISOS = ["AFG", "BGD", "BTN", "IND", "MDV", "NPL", "PAK", "LKA"]
    
    # Mapping of local names to ISO codes
    COUNTRY_MAP = {
        "Afghanistan": "AFG",
        "Bangladesh": "BGD",
        "Bhutan": "BTN",
        "India": "IND",
        "Maldives": "MDV",
        "Nepal": "NPL",
        "Pakistan": "PAK",
        "Sri Lanka": "LKA"
    }
    
    # Expanded Indicator Mappings to maximize data points
    INDICATORS = {
        # --- ECONOMIC (Growth & Stability) ---
        'gdp_per_capita': 'NY.GDP.PCAP.CD',
        'gdp_growth': 'NY.GDP.MKTP.KD.ZG',
        'gni_per_capita': 'NY.GNP.PCAP.CD',
        'inflation': 'FP.CPI.TOTL.ZG',
        'fdi_inflows': 'BX.KLT.DINV.WD.GD.ZS',
        'exports_gdp': 'NE.EXP.GNFS.ZS',
        'imports_gdp': 'NE.IMP.GNFS.ZS',
        'foreign_reserves': 'FI.RES.TOTL.CD',
        'personal_remittances': 'BX.TRF.PWKR.DT.GD.ZS',
        'total_reserves': 'FI.RES.TOTL.CD',
        'debt_service': 'DT.TDS.DECT.EX.ZS',
        'central_govt_debt': 'GC.DOD.TOTL.GD.ZS',
        
        # --- POVERTY & INEQUALITY ---
        'gini_index': 'SI.POV.GINI',
        'poverty_headcount': 'SI.POV.NAHC',
        'poverty_215': 'SI.POV.DDAY',
        'poverty_365': 'SI.POV.LMIC',
        'income_lowest_20': 'SI.DST.FRST.20',
        'income_highest_20': 'SI.DST.05TH.20',
        'income_share_highest_10': 'SI.DST.10TH.10',
        'multidimensional_poverty': 'SI.POV.MDIM',
        
        # --- LABOR & SOCIAL PROTECTION ---
        'unemployment': 'SL.UEM.TOTL.ZS',
        'labor_force_total': 'SL.TLF.TOTL.IN',
        'female_labor_participation': 'SL.TLF.CACT.FE.ZS',
        'employment_agriculture': 'SL.AGR.EMPL.ZS',
        'employment_industry': 'SL.IND.EMPL.ZS',
        'employment_services': 'SL.SRV.EMPL.ZS',
        'youth_unemployment': 'SL.UEM.1524.ZS',
        'vulnerable_employment': 'SL.EMP.VULN.ZS',
        'child_labor': 'SL.TLF.0714.ZS',
        
        # --- DIGITAL & INFRASTRUCTURE ---
        'internet_usage': 'IT.NET.USER.ZS',
        'mobile_subscriptions': 'IT.CEL.SETS.P2',
        'electricity_access': 'EG.ELC.ACCS.ZS',
        'fixed_broadband': 'IT.NET.BBND.P2',
        'secure_servers': 'IT.NET.SECR.P6',
        'atm_access': 'FB.ATM.TOTL.P5',
        'rail_lines_total': 'IS.RRS.TOTL.KM',
        'air_transport_passengers': 'IS.AIR.PSGR',
        
        # --- EDUCATION & SKILLS ---
        'primary_completion': 'SE.PRM.CMPT.ZS',
        'literacy_rate': 'SE.ADT.LITR.ZS',
        'school_enrollment_secondary': 'SE.SEC.ENRL.FE.ZS',
        'tertiary_enrollment': 'SE.TER.ENRL.ZS',
        'education_expenditure': 'SE.XPD.TOTL.GD.ZS',
        'pupil_teacher_ratio_primary': 'SE.PRM.ENRL.TC.ZS',
        'female_stem_graduates': 'SE.TER.GRAD.FE.SI.ZS',
        'researchers_rd': 'SP.POP.SCIE.RD.P6',
        
        # --- HEALTH & DEMOGRAPHICS ---
        'life_expectancy': 'SP.DYN.LE00.IN',
        'population': 'SP.POP.TOTL',
        'population_growth': 'SP.POP.GROW',
        'urban_population_pct': 'SP.URB.TOTL.IN.ZS',
        'maternal_mortality': 'SH.STA.MMRT',
        'physicians_per_1000': 'SH.MED.PHYS.ZS',
        
        # --- ENVIRONMENT & ENERGY ---
        'renewable_energy_share': 'EG.FEC.RNEW.ZS',
        'pm25_pollution': 'EN.ATM.PM25.MC.M3',
        'electricity_renewables': 'EG.ELC.RNEW.ZS',
        'access_electricity_rural': 'EG.ELC.ACCS.RU.ZS',
        'forest_area': 'AG.LND.FRST.ZS',
        'arable_land': 'AG.LND.ARBL.ZS',
        
        # --- GENDER & INCLUSION ---
        'women_in_parliament': 'SG.GEN.PARL.ZS',
        'female_business_owners': 'IC.REG.COST.PC.FE.ZS',
        'nondiscrimination_law': 'SG.LAW.EQRM.WK',
        
        # --- PRIVATE SECTOR & TRADE ---
        'new_business_density': 'IC.BUS.NDNS.ZS',
        'high_tech_exports': 'TX.VAL.TECH.MF.ZS',
        'merchandise_trade': 'TG.VAL.TOTL.GD.ZS',
        'logistics_performance': 'LP.LPI.OVRL.XQ'
    }

    def _fetch_raw(self, indicator_code, countries=None, date_range="1960:2024"):
        """
        Private uncached method for fetching data.
        """
        if countries is None:
            country_string = ";".join(self.SOUTH_ASIA_ISOS)
        else:
            iso_list = [self.COUNTRY_MAP.get(c, c) for c in (countries if isinstance(countries, list) else [countries])]
            country_string = ";".join(iso_list)
            
        url = f"{self.BASE_URL}country/{country_string}/indicator/{indicator_code}"
        params = {
            "format": "json",
            "date": date_range,
            "per_page": 2000
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if len(data) < 2 or not data[1]:
                return pd.DataFrame()
            
            records = []
            for item in data[1]:
                if item['value'] is not None:
                    records.append({
                        "country": item['country']['value'],
                        "iso3": item['countryiso3code'],
                        "year": int(item['date']),
                        "value": item['value'],
                        "indicator": item['indicator']['value']
                    })
            
            return pd.DataFrame(records)
        except Exception:
            return pd.DataFrame()

    @st.cache_data(ttl=86400)
    def fetch_indicator(_self, indicator_code, countries=None, date_range="1960:2024"):
        """
        Public cached method.
        """
        return _self._fetch_raw(indicator_code, countries, date_range)

    @st.cache_data(ttl=3600)
    def get_exchange_rates(_self, base_currency="USD"):
        """
        Fetch live exchange rates for South Asian currencies
        """
        url = f"https://api.frankfurter.app/latest?from={base_currency}"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            rates = data.get('rates', {})
            relevant_rates = {k: v for k, v in rates.items() if k in ["INR", "BDT", "PKR", "LKR", "NPR"]}
            return relevant_rates
        except:
            return {"INR": 83.0, "BDT": 110.0, "PKR": 280.0, "LKR": 320.0, "NPR": 133.0}

    @st.cache_data(ttl=300)
    def get_api_summary_v2(_self):
        """
        Calculates total records available across all expanded indicators.
        Uses ThreadPoolExecutor with uncached fetch to avoid Streamlit context issues.
        """
        total_records = 0
        indicators_found = 0
        import concurrent.futures
        
        # Parallel Fetching using raw method
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Map futures to indicators
            future_to_ind = {executor.submit(_self._fetch_raw, _self.INDICATORS[k]): k for k in _self.INDICATORS.keys()}
            
            for future in concurrent.futures.as_completed(future_to_ind):
                try:
                    df = future.result()
                    if not df.empty:
                        total_records += len(df)
                        indicators_found += 1
                except Exception:
                    continue
        
        return {
            "total_records": total_records,
            "indicators": indicators_found,
            "source": "World Bank Cloud API (60+ Years Data)"
        }

@st.cache_resource
def get_api_loader():
    """
    Returns a cached instance of the API loader.
    """
    return WorldBankAPILoader()

