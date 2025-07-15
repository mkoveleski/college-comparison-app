import requests
import json

# Separate API keys for College Scorecard and Census APIs
COLLEGE_API_KEY = "S8nxjia7h7bNPA7HJLQT1AGk8CjsoQEKrDO8fqxg"
CENSUS_API_KEY = "84f45660e9fce52a95861d32a41cb0429634058e"

BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"
CENSUS_BASE_URL = "https://api.census.gov/data/2022/acs/acs5/profile"

CENSUS_VARIABLES = {
    "population": "DP05_0001E",
    "median_income": "DP03_0062E",
    "poverty_rate": "DP03_0088PE"
}

FIPS_STATE_CODES = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06", "CO": "08", "CT": "09", "DE": "10",
    "FL": "12", "GA": "13", "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19", "KS": "20",
    "KY": "21", "LA": "22", "ME": "23", "MD": "24", "MA": "25", "MI": "26", "MN": "27", "MS": "28",
    "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34", "NM": "35", "NY": "36",
    "NC": "37", "ND": "38", "OH": "39", "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45",
    "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50", "VA": "51", "WA": "53", "WV": "54",
    "WI": "55", "WY": "56"
}

def search_college(query):
    is_id = query.isdigit()

    params = {
        "api_key": COLLEGE_API_KEY,
        "fields": ",".join([
            "id", "school.name", "school.city", "school.state", 
            "school.school_url", "school.carnegie_basic",
            "school.degrees_awarded.highest", "school.ownership",
            "latest.student.size", "latest.student.demographics.race_ethnicity.white",
            "latest.student.demographics.race_ethnicity.black",
            "latest.student.demographics.race_ethnicity.hispanic",
            "latest.student.demographics.race_ethnicity.asian",
            "latest.student.demographics.female",
            "latest.student.demographics.female_share",
            "latest.student.demographics.men",
            "latest.student.share_firstgeneration",
            "latest.student.share_pell",
            "latest.completion.completion_rate_4yr_150nt",
            "latest.completion.retention_rate.four_year.full_time",
            "latest.completion.retention_rate.four_year.part_time"
        ]),
        "per_page": 1
    }

    if is_id:
        params["id"] = query
    else:
        params["school.name"] = query

    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        results = response.json().get("results")
        if results:
            data = results[0]

            ownership_map = {1: "Public", 2: "Private Nonprofit", 3: "Private For-Profit"}
            degree_map = {
                0: "Non-Degree Granting", 1: "Certificate", 2: "Associate's",
                3: "Bachelor's", 4: "Graduate", 5: "Doctoral"
            }
            carnegie_map = {
                1: "Associate's - Public Rural-Serving Small",
                15: "Research Universities - Very High Research Activity",
                16: "Research Universities - High Research Activity",
                18: "Doctoral/Professional Universities",
                21: "Master's Colleges & Universities: Larger Programs"
            }

            data["school.ownership_label"] = ownership_map.get(data.get("school.ownership"), "Unknown")
            data["school.degrees_awarded.highest_label"] = degree_map.get(data.get("school.degrees_awarded.highest"), "Unknown")
            data["school.carnegie_basic_label"] = carnegie_map.get(data.get("school.carnegie_basic"), "Unknown")

            if "latest.student.size" in data and isinstance(data["latest.student.size"], int):
                data["latest.student.size"] = f"{data['latest.student.size']:,}"

            percent_fields = [
                "latest.student.demographics.race_ethnicity.white",
                "latest.student.demographics.race_ethnicity.black",
                "latest.student.demographics.race_ethnicity.hispanic",
                "latest.student.demographics.race_ethnicity.asian",
                "latest.student.demographics.female_share",
                "latest.student.demographics.men",
                "latest.student.share_firstgeneration",
                "latest.student.share_pell",
                "latest.completion.completion_rate_4yr_150nt",
                "latest.completion.retention_rate.four_year.full_time",
                "latest.completion.retention_rate.four_year.part_time"
            ]

            for key in percent_fields:
                if key in data and isinstance(data[key], float):
                    data[key] = f"{data[key] * 100:.1f}%"

            return data
        else:
            return None
    else:
        raise Exception(f"API error: {response.status_code}")

def get_location_snapshot(college_data):
    city = college_data.get("school.city", "")
    state = college_data.get("school.state", "")
    state_fips = FIPS_STATE_CODES.get(state.upper())
    if not city or not state_fips:
        return None

    params = {
        "get": ",".join(CENSUS_VARIABLES.values()),
        "for": "place:*",
        "in": f"state:{state_fips}",
        "key": CENSUS_API_KEY
    }

    response = requests.get(CENSUS_BASE_URL, params=params)
    if response.status_code != 200:
        return None

    try:
        data = response.json()
        headers = data[0]
        rows = data[1:]
        match = next((row for row in rows if city.lower() in row[0].lower()), None)
        if not match:
            return None

        index_map = {k: headers.index(v) for k, v in CENSUS_VARIABLES.items()}
        return {
            "population": match[index_map["population"]],
            "median_income": match[index_map["median_income"]],
            "poverty_rate": match[index_map["poverty_rate"]]
        }
    except Exception:
        return None
