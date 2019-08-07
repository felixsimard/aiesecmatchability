'''

Matchability - API Processing and Predictions
Returns the model outputs.

'''

import json
import pickle
import re
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


# Returns the difference between two dates
def dateDiff(date1, date2):  # date1 and date2 come in as Strings
    diff = pd.to_datetime(date1) - pd.to_datetime(date2)
    diff = diff / np.timedelta64(1, 'D')
    if str(diff) == "nan" or str(diff) == "NaN":
        return 0
    else:
        return diff


def hasValue(x):
    if x != None and x != 0 and type(x) != float and str(x) != "" and str(x) != "NaN" and str(x) != "nan":
        return 1
    else:
        return 0


def ifStringEmpty(x):
    if x == None or x == "":
        return ""
    else:
        return x


def ifNull(x):
    if x == None:
        return 0
    else:
        return x


def replaceWords(x):
    mapping = [('Not compulsory', 'replaced_words'), ('not compulsory', 'replaced_words'),
               ('Not mandatory', 'replaced_words'), ('not mandatory', 'replaced_words'),
               ('Not needed', 'replaced_words'), ('not_needed', 'replaced_words')]
    for k, v in mapping:
        x = x.replace(k, v)
    return x


def setTransportationCovered(x):
    txt = x.strip()
    if txt == "One way" or txt == "Return trip":
        return 1
    else:
        return 0


def setNumMeals(x):
    if type(x) == float or str(x) == "" or x == "Not covered" or x == "0":
        return 0
    else:
        num = re.findall(r'\b\d+\b', x)
        if len(num) > 0:
            return int(num[0])
        else:
            return 0


# Setting up a dictionnary of countries and their respective 3-digit country codes
lookup_country = {}
lookup_country['Peru'] = ['Latin America', 'PER']
lookup_country['India'] = ['India', 'IND']
lookup_country['Mexico'] = ['North America', 'MEX']
lookup_country['Asia Pacific'] = ['South Asia', 'IDN']
lookup_country['Costa Rica'] = ['Latin America', 'CRI']
lookup_country['Brazil'] = ['Brazil', 'BRA']
lookup_country['Paraguay'] = ['Latin America', 'PRY']
lookup_country['Poland'] = ['East Europe', 'POL']
lookup_country['Greece'] = ['West Europe', 'GRC']
lookup_country['Tanzania'] = ['Africa', 'TZA']
lookup_country['Egypt'] = ['Africa', 'EGY']
lookup_country['Burkina Faso'] = ['Africa', 'BFA']
lookup_country['Middle East and Africa'] = ['Africa', 'IRN']
lookup_country['Argentina'] = ['Argentina', 'ARG']
lookup_country['Romania'] = ['East Europe', 'ROU']
lookup_country['Germany'] = ['West Europe', 'DEU']
lookup_country['Chile'] = ['Latin America', 'CHL']
lookup_country['Colombia'] = ['Latin America', 'COL']
lookup_country['Russia'] = ['West Europe', 'RUS']
lookup_country['Malta'] = ['West Europe', 'MLT']
lookup_country['Singapore'] = ['North Asia', 'SGP']
lookup_country['Italy'] = ['West Europe', 'ITA']
lookup_country['Thailand'] = ['South Asia', 'THA']
lookup_country['South Korea'] = ['North Asia', 'KOR']
lookup_country['Panama'] = ['Latin America', 'PAN']
lookup_country['Hong Kong'] = ['China', 'HKG']
lookup_country['China, Mainland'] = ['China', 'CHN']
lookup_country['Philippines'] = ['South Asia', 'PHL']
lookup_country['Indonesia'] = ['South Asia', 'IDN']
lookup_country['Portugal'] = ['West Europe', 'PRT']
lookup_country['Botswana'] = ['Africa', 'BWA']
lookup_country['Uganda'] = ['Africa', 'UGA']
lookup_country['Hungary'] = ['East Europe', 'HUN']
lookup_country['Ghana'] = ['Africa', 'GHA']
lookup_country['Tunisia'] = ['Africa', 'TUN']
lookup_country['Bulgaria'] = ['East Europe', 'BGR']

lookup_country['Sri Lanka'] = ['South Asia', 'LKA']
lookup_country['Taiwan'] = ['South Asia', 'TWN']
lookup_country['Americas'] = ['Latin America', 'CRI']
lookup_country['Czech Republic'] = ['East Europe', 'CZE']
lookup_country['Ecuador'] = ['Latin America', 'ECU']
lookup_country['United States'] = ['United States', 'USA']
lookup_country['Guatemala'] = ['Latin America', 'GTM']
lookup_country['Canada'] = ['Canada', 'CAN']
lookup_country['Turkey'] = ['Turkey', 'TUR']
lookup_country['Belgium'] = ['West Europe', 'BEL']
lookup_country['Malaysia'] = ['South Asia', 'MYS']
lookup_country['Cameroon'] = ['Africa', 'CMR']
lookup_country['Pakistan'] = ['Middle East', 'PAK']
lookup_country['Japan'] = ['North Asia', 'JPN']
lookup_country['Mauritius'] = ['Africa', 'MUS']

lookup_country['Cambodia'] = ['South Asia', 'KHM']
lookup_country['Montenegro'] = ['East Europe', 'MNE']
lookup_country['Ukraine'] = ['East Europe', 'UKR']
lookup_country['Serbia'] = ['East Europe', 'SRB']
lookup_country['Slovakia'] = ['East Europe', 'SVK']
lookup_country['El Salvador'] = ['Latin America', 'SLV']
lookup_country['Europe'] = ['West Europe', 'FRA']
lookup_country['Iran'] = ['Middle East', 'IRN']
lookup_country['Morocco'] = ['Africa', 'MAR']
lookup_country['The Netherlands'] = ['West Europe', 'NLD']
lookup_country['Norway'] = ['West Europe', 'NOR']
lookup_country['Spain'] = ['West Europe', 'ESP']
lookup_country['Lithuania'] = ['East Europe', 'LTU']
lookup_country['South Africa'] = ['Africa', 'ZAF']
lookup_country['Venezuela'] = ['Latin America', 'VEN']

lookup_country['Vietnam'] = ['South Asia', 'VNM']
lookup_country['Nepal'] = ['Middle East', 'NPL']
lookup_country['Nigeria'] = ['Africa', 'NGA']
lookup_country['Kazakhstan'] = ['Middle East', 'KAZ']
lookup_country['Finland'] = ['West Europe', 'FIN']
lookup_country['Georgia'] = ['East Europe', 'GEO']
lookup_country['Bahrain'] = ['Africa', 'BHR']
lookup_country['Namibia'] = ['Africa', 'NAM']
lookup_country['Australia'] = ['Australia', 'AUS']
lookup_country['Rwanda'] = ['Africa', 'RWA']
lookup_country['Denmark'] = ['West Europe', 'DNK']
lookup_country['Slovenia'] = ['East Europe', 'SVN']
lookup_country['Switzerland'] = ['West Europe', 'CHE']
lookup_country['Togo'] = ['Africa', 'TGO']
lookup_country['Croatia'] = ['East Europe', 'HRV']

lookup_country['Gabon'] = ['Africa', 'GAB']
lookup_country['Lebanon'] = ['Middle East', 'LBN']
lookup_country['Bolivia'] = ['East Europe', 'BOL']
lookup_country['United Kingdom'] = ['West Europe', 'GBR']
lookup_country['Benin'] = ['Africa', 'BEN']
lookup_country['France'] = ['West Europe', 'FRA']
lookup_country['Ethiopia'] = ['Africa', 'ETH']
lookup_country['Uruguay'] = ['Latin America', 'URY']
lookup_country['Kyrgyzstan'] = ['Middle East', 'KGZ']
lookup_country['Mozambique'] = ['Africa', 'MOZ']
lookup_country['Moldova'] = ['East Europe', 'MDA']
lookup_country['Ireland'] = ['West Europe', 'IRL']
lookup_country['Sweden'] = ['West Europe', 'SWE']
lookup_country['Oman'] = ['Middle East', 'OMN']
lookup_country['Algeria'] = ['Africa', 'DZA']
lookup_country['Senegal'] = ['Africa', 'SEN']
lookup_country['Myanmar'] = ['South Asia', 'MMR']

lookup_country['Azerbaijan'] = ['Middle East', 'AZE']
lookup_country['Austria'] = ['East Europe', 'AUT']
lookup_country['New Zealand'] = ['Australia', 'NZL']
lookup_country['Afghanistan'] = ['Middle East', 'AFG']
lookup_country['Kenya'] = ['Africa', 'KEN']
lookup_country['Belarus'] = ['East Europe', 'BLR']
lookup_country['Cote D\'Ivoire'] = ['Africa', 'CIV']
lookup_country['Dominican Republic'] = ['Latin America', 'DOM']
lookup_country['Albania'] = ['East Europe', 'ALB']
lookup_country['Liberia'] = ['Africa', 'LBR']
lookup_country['Estonia'] = ['East Europe', 'EST']
lookup_country['Armenia'] = ['Middle East', 'ARM']
lookup_country['Macedonia'] = ['East Europe', 'MKD']
lookup_country['Bosnia and Herzegovina'] = ['East Europe', 'BIH']

lookup_country['Mongolia'] = ['Middle East', 'MNG']
lookup_country['Jordan'] = ['Middle East', 'JOR']
lookup_country['Cabo Verde'] = ['Africa', 'CPV']
lookup_country['Tajikistan'] = ['Middle East', 'TJK']
lookup_country['Nicaragua'] = ['Latin America', 'NIC']
lookup_country['United Arab Emirates'] = ['Middle East', 'ARE']
lookup_country['Latvia'] = ['East Europe', 'LVA']
lookup_country['Laos'] = ['South Asia', 'LAO']
lookup_country['Puerto Rico'] = ['Latin America', 'PRI']
lookup_country['Iceland'] = ['West Europe', 'ISL']
lookup_country['LUXEMBOURG (CLOSED)'] = ['West Europe', 'LUX']

lookup_country['Qatar'] = ['Middle East', 'QAT']
lookup_country['Malawi'] = ['Africa', 'MWI']
lookup_country['Kuwait'] = ['Middle East', 'KWT']
lookup_country['Seychelles'] = ['South Asia', 'SYC']
lookup_country['Bangladesh'] = ['South Asia', 'BGD']
lookup_country['Liechtenstein'] = ['East Europe', 'LIE']
lookup_country['Haiti'] = ['Latin America', 'HTI']
lookup_country['Kingdom of Saudi Arabia'] = ['Middle East', 'SAU']
lookup_country['Cuba'] = ['Latin America', 'CUB']
lookup_country['Uzbekistan'] = ['Middle East', 'UZB']

lookup_country['Cyprus'] = ['Africa', 'CYP']
lookup_country['Fiji'] = ['South Asia', 'FJI']
lookup_country['Mali'] = ['Africa', 'MLI']


def matchability(d):
    ### FETCH + FORMAT VARIABLES ###

    # ------------------------------
    try:
        dmin = d["duration_min"]
        duration_min = ifNull(dmin)
    except:
        duration_min = 0

    # ------------------------------

    # ------------------------------

    try:
        cover_picture_link = ifNull(d["cover_picture_link"])
        has_cover_pic = hasValue(cover_picture_link)
    except:
        has_cover_pic = 0

    try:
        profile_picture_link = ifNull(d["profile_picture_link"])
        has_profile_pic = hasValue(profile_picture_link)
    except:
        has_profile_pic = 0

    # ------------------------------

    # ------------------------------

    try:
        project_fee_cents = ifNull(d["project_fee_cents"])
    except:
        project_fee_cents = 0

    # ------------------------------

    # ------------------------------

    try:
        openings = ifNull(d["openings"])
    except:
        openings = 1

    # ------------------------------
    try:
        created_at = ifStringEmpty(d["created_at"])
    except:
        created_at = ""

    try:
        application_close_date = ifStringEmpty(d["application_close_date"])
    except:
        application_close_date = ""

    try:
        earliest_start_date = ifStringEmpty(d["earliest_start_date"])
    except:
        earliest_start_date = ""

    try:
        latest_end_date = ifStringEmpty(d["latest_end_date"])
    except:
        latest_end_date = ""

    # Duration to apply for the internship: application_close_date - created_at
    try:
        time_window_to_apply = dateDiff(application_close_date, created_at)
    except:
        time_window_to_apply = 0

    # Duration available of the intership: latest_end_date - earliest_end_date
    try:
        experience_max_duration = dateDiff(latest_end_date, earliest_start_date)
    except:
        experience_max_duration = 0

    # Difference between created_at and earliest_start_date
    try:
        created_vs_earliest_start = dateDiff(earliest_start_date, created_at)
    except:
        created_vs_earliest_start = 0

    # Difference between lastest_end_date and created_at
    try:
        created_vs_latest_end = dateDiff(latest_end_date, created_at)
    except:
        created_vs_latest_end = 0

    # How rigid is the timeframe of the internship? (units: number of days)
    try:
        experience_timeframe_rigidness = round((experience_max_duration / duration_min), 1)
    except:
        experience_timeframe_rigidness = round((0), 1)

    # ------------------------------
    # year completion ratio
    month = str(earliest_start_date).split('-')
    try:
        if month[1] != "":
            year_completion_ratio = round(((int(month[1]) - 1) / (12)), 2)
        else:
            year_completion_ratio = 0.00
    except:
        year_completion_ratio = 0.00

    # ------------------------------

    # ------------------------------
    try:
        name_entity = ifStringEmpty(d["name_entity"])
    except:
        name_entity = ""

    try:
        name_region = ifStringEmpty(d["name_region"])
    except:
        name_region = ""

    regions = {'Americas': 0, 'Asia Pacific': 0, 'Europe': 0, 'Middle East and Africa': 0}
    # HDI
    hdi = pd.read_csv('matchability_lib/Data/hdi_gdp_2015.csv', low_memory=False)
    country = name_entity
    try:
        country_code = lookup_country[country][1]
    except:
        country_code = ""
    hdi_array = hdi.loc[hdi['Code'] == country_code][
        'Historical Index of Human Development (including GDP metric) ((0-1; higher values are better))'].values
    if hdi_array and hdi_array[0] != "":
        hdi_index = hdi_array[0]
    else:
        hdi_index = 0.5

    regions[name_region] = 1
    is_americas = regions["Americas"]
    is_asia_pacific = regions["Asia Pacific"]
    is_europe = regions["Europe"]
    is_middle_east_africa = regions["Middle East and Africa"]

    # ------------------------------

    # ------------------------------
    try:
        title_len = len(d["title"])
    except:
        title_len = 0
    try:
        description_len = len(d["description"])
    except:
        description_len = 0
    # ------------------------------

    # ------------------------------
    try:
        salary = ifNull(d["salary"])
    except:
        salary = 0

    # ------------------------------

    # ------------------------------
    try:
        programme_id = ifNull(d["programme_id"])
    except:
        programme_id = 0

    # Programme id lookup
    # prog_dict = {1:"Global Volunteer", 2:"Global Talent", 5:"Global Entrepreneur"}
    prog_dict = {"1": 0, "2": 0, "5": 0}
    prog_dict[str(programme_id)] = 1
    is_global_volunteer = prog_dict["1"]
    is_global_talent = prog_dict["2"]
    is_global_entrepreneur = prog_dict["5"]

    # ------------------------------

    # ------------------------------
    try:
        opp_background_req = ifStringEmpty(d["opp_background_req"])
    except:
        opp_background_req = ""

    try:
        opp_background_pref = ifStringEmpty(d["opp_background_pref"])
    except:
        opp_background_pref = ""

    try:
        opp_skill_req = ifStringEmpty(d["opp_skill_req"])
    except:
        opp_skill_req = ""

    try:
        opp_skill_pref = ifStringEmpty(d["opp_skill_pref"])
    except:
        opp_skill_pref = ""

    background_skills_lst = [opp_background_req, opp_background_pref, opp_skill_req, opp_skill_pref]
    skills = ", ".join(background_skills_lst)
    skills_df = pd.DataFrame()
    skills_df['skills'] = pd.Series(skills)

    ### K-MEANS for JOB DESCRIPTION ###

    # Load the kmeans pickle
    km = pickle.load(open("matchability_lib/pickles/kmeans.pickle", 'rb'))

    vec = pickle.load(open("matchability_lib/pickles/vectorizer.pickle", 'rb'))

    cluster_terms = pickle.load(open("matchability_lib/pickles/cluster_terms.pickle", 'rb'))

    vectorizer = TfidfVectorizer()
    skills_vec = vec.transform(skills_df.skills)

    y = km.predict(skills_vec)

    # setup a dictionary
    clusters_dict = {}
    for ind in range(len(cluster_terms)):
        key = "cl" + str(ind + 1)
        clusters_dict[key] = [cluster_terms[ind], 0]

    # one-hot the proper cluster
    key = "cl" + str(int(y) + 1)
    clusters_dict[key] = [cluster_terms[int(y)], 1]

    cl1 = clusters_dict["cl1"][1]
    cl2 = clusters_dict["cl2"][1]
    cl3 = clusters_dict["cl3"][1]
    cl4 = clusters_dict["cl4"][1]
    cl5 = clusters_dict["cl5"][1]
    cl6 = clusters_dict["cl6"][1]
    cl7 = clusters_dict["cl7"][1]
    cl8 = clusters_dict["cl8"][1]
    cl9 = clusters_dict["cl9"][1]
    cl10 = clusters_dict["cl10"][1]

    num_skills = len(opp_skill_req.split(','))

    num_backgrounds = len(opp_background_req.split(','))

    # ------------------------------

    # ------------------------------
    try:
        opp_language_req = ifStringEmpty(d["opp_language_req"])
        num_languages = len(opp_language_req.split(","))
    except:
        num_languages = 0

    # ------------------------------

    # ------------------------------

    try:
        logistics_info = ifStringEmpty(d["logistics_info"])
    except:
        logistics_info = ""

    try:
        specifics_info = ifStringEmpty(d["specifics_info"])
    except:
        specifics_info = ""

    try:
        legal_info = ifStringEmpty(d["legal_info"])
    except:
        legal_info = ""

    try:
        role_info = ifStringEmpty(d["role_info"])
    except:
        role_info = ""

    try:
        insurance_info = legal_info[0]["health_insurance_info"]
    except:
        insurance_info = ""

    insurance_info = replaceWords(insurance_info)
    insurance_key_words = ["needed", "mandatory", "compulsory"]
    health_insurance_needed = 0
    for keyword in insurance_info:
        if keyword in insurance_info:
            health_insurance_needed = 1

    # Accomodation covered
    try:
        acc_covered = logistics_info[0]["accommodation_covered"]
        if acc_covered == "true":
            accommodation_covered = 1
        else:
            accommodation_covered = 0
    except:
        accommodation_covered = 0

    # Transportation Covered
    try:
        is_transportation_covered = setTransportationCovered(logistics_info[0]["transportation_covered"])
    except:
        is_transportation_covered = 0

    # Food weekends
    try:
        f_weekends = logistics_info[0]["food_weekends"]
        if f_weekends == "true":
            food_weekends = 1
        else:
            food_weekends = 0
    except:
        food_weekends = 0

    # Number of meals
    try:
        n_meals = logistics_info[0]["food_covered"]
        num_meals = setNumMeals(n_meals)
    except:
        num_meals = 0

    # expected work schedule
    try:
        expected_work_schedule = hasValue(specifics_info[0]["expected_work_schedule"])
    except:
        expected_work_schedule = 0

    # computer or not
    try:
        computer = hasValue(specifics_info[0]["computer"])
    except:
        computer = 0

    # ------------------------------

    # Now predict the output

    # Open the model
    model = pickle.load(open("matchability_lib/pickles/matcha_model.pickle", 'rb'))

    # Load the considered features
    features = pickle.load(open("matchability_lib/pickles/features.pickle", 'rb'))

    # features dictionary
    feat_dict = {

        'openings': openings,
        'duration_min': duration_min,
        'application_open_window': time_window_to_apply,
        'experience_max_duration': experience_max_duration,
        'created_vs_earliest_start': created_vs_earliest_start,
        'created_vs_latest_end': created_vs_latest_end,
        'experience_timeframe_rigidness': experience_timeframe_rigidness,

        'title_len': title_len,
        'description_len': description_len,
        'num_languages': num_languages,
        'salary': salary,

        'num_skills': num_skills,
        'num_backgrounds': num_backgrounds,
        'has_cover_pic': has_cover_pic,
        'has_profile_pic': has_profile_pic,
        'computer': computer,
        'expected_work_schedule': expected_work_schedule,

        'accommodation_covered': accommodation_covered,
        'food_weekends': food_weekends,
        'health_insurance_needed': health_insurance_needed,
        'is_transportation_covered': is_transportation_covered,
        'num_meals': num_meals,

        'is_americas': is_americas,
        'is_asia_pacific': is_asia_pacific,
        'is_europe': is_europe,
        'is_middle_east_africa': is_middle_east_africa,
        'hdi': hdi_index,
        'year_completion_ratio': year_completion_ratio,
        'is_global_volunteer': is_global_volunteer,
        'is_global_talent': is_global_talent,
        'is_global_entrepreneur': is_global_entrepreneur

    }

    '''
    for key, val in feat_dict.items():
        print(key, ":", val)
    '''

    data = []
    # append the features to the features list
    for ind in range(0, (len(features) - 10)):
        data.append(feat_dict[features[ind]])

    # append the custom clusters features (10 of them) to the features list
    custom_data_clusters = [cl1, cl2, cl3, cl4, cl5, cl6, cl7, cl8, cl9, cl10]
    for cl in custom_data_clusters:
        data.append(cl)

    # Generate the data to be passed to the model
    df = pd.DataFrame([data], columns=features)
    x_data = df.loc[:].astype(float)

    # predict using the model and fetch outputs
    prob = model.predict_proba(x_data)[0][1]
    output = (model.predict(x_data).astype(int) == 1)[0]

    # get current timestamp
    timestamp = str(datetime.now())
    res_as_dict = {'status': 'OK', 'output': str(output), 'value': prob,
                   'timestamp': timestamp}  # make sure the boolean values in the dict are strings
    res_as_json = json.dumps(res_as_dict)

    return res_as_json
