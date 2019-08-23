'''

Matchability - Training model
Data extraction, cleaning, formatting and model training.

'''

import pandas as pd
import numpy as np
import sshtunnel
import math
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime
import psycopg2
import statsmodels.api as sm
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import roc_curve, auc, roc_auc_score
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.externals.six import StringIO
from sklearn.ensemble import RandomForestClassifier
import warnings; warnings.simplefilter('ignore')
import graphviz
import time
import pickle
import re


print("\n")
print("###------------------- AIESEC Matchability Modelling ---------------------###")
print("###----------------------------------------------------------------------###", "\n")

#----------------------- HELPER FUNCTIONS --------------------------------###

# Simple ratio function
def ratio(numerator, denominator):
    return (numerator / denominator) * 100

# Removing rows from a Pandas Dataframe
def removeRows(data, column, indexes_unwanted):
    data = data.drop(indexes_unwanted, axis=0)
    print("Removed", len(indexes_unwanted), "rows.")
    return data

# Function to parse the dates of a specified column and get the badly formatted dates to be cleaned
def scanDates(data, column):
    bad_dates_indexes = []
    fake_nan_indexes = []
    for index, row in data.iterrows():
        date = str(row[column])
        try:
            if date == 'nan':
                fake_nan_indexes.append(index)
            date = pd.to_datetime(date)
        except Exception as e:
            bad_dates_indexes.append(index)
            print(date, "Error is:", e)
            pass

    print("Found", len(bad_dates_indexes), "incorrectly formatted dates.")
    print("Found", len(fake_nan_indexes), "NaN dates.")

    return bad_dates_indexes

# Date cleaner function
def cleanDates(data, column, bad_dates):
    for index in bad_dates:
        bad_date = data[column][index]
        first_two_year_digit = data[column][index][:2]

        # Handle the weird two digits year format, replace with a 4 digit format
        if bad_date[0] == '1' and len(bad_date) == 17:
            data[column][index] = "20{}".format(bad_date)

        # Handle the cases of 00, 01, 10, 11, etc as the first two values of a date... replace with 20
        if first_two_year_digit != "20" and len(bad_date) == 19:
            data[column][index] = data[column][index].replace(first_two_year_digit, '20')

        if str(first_two_year_digit) == 'nan':
            data[column][index] = data[column][index].replace(first_two_year_digit, '20')


# Returns the difference between two dates
def dateDiff(date1, date2): # date1 and date2 come in as Strings
    diff = pd.to_datetime(date1) - pd.to_datetime(date2)
    diff = diff / np.timedelta64(1,'D')
    return diff
    '''
        if not diff.empty:
            diff = diff.values[0]
        else:
            diff = 0.0
        return diff
    '''

# Getting the value of a Pandas Series
def getSeriesValue(data, column):
    if len(data[column]) > 0:
        return data[column].values[0]
    else:
        return np.nan


 # Database connection function
def execute_sql(filename, csv_name):
    try:
        with sshtunnel.SSHTunnelForwarder(
            (host, 22),
            ssh_private_key = ssh_private_key,
            ssh_username = ssh_username,
            remote_bind_address = (remote_host, 5432),
            local_bind_address = (localhost, 5430)) as server:
            server.start()
            print("\n")
            print("Server connected.", "\n")
            params = {
                'database': database,
                'user': user,
                'password': password,
                'host': server.local_bind_host,
                'port': server.local_bind_port
            }
            conn = psycopg2.connect(**params)
            curs = conn.cursor()
            print("Database connected.", "\n")

            # Open and read the file as a single buffer
            print("Reading", filename, "...", "\n")
            fd = open(filename, 'r')
            sqlFile = fd.read().strip()
            fd.close()

            print("Running query...", "\n")
            # execute the query
            curs.execute(sqlFile)

            col_names = []
            for elt in curs.description:
                col_names.append(elt[0])
            result = curs.fetchall()
            conn.close()

            # create a dataframe to show the results
            df = pd.DataFrame(result, columns=col_names)
            print("Query OK.", len(df), "rows found.")

            # save results dataframe to CSV
            print("Saving results to", "Data/"+csv_name)
            df.to_csv("Data/"+csv_name)

            return df

    except Exception as e:
        print("Connection failed:", e)


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

print("Variables, constants and functions setup.", "\n")
print("###---------------------------------------------------------------------###", "\n")
###---------------------------------------------------------------------###


###-------------------------- SQL EXTRACTION ---------------------------###
print("\n")
print("###-------------------------- SQL EXTRACTION ---------------------------###", "\n")

# ssh variables
host = 'internal.aiesec.org'
localhost = '127.0.0.1'
ip = '207.107.68.234'
remote_host = 'gisapi-production-aurora.cluster-ro-csrm8v3e6d8r.eu-west-1.rds.amazonaws.com'
ssh_username = 'ec2-user'
#ssh_private_key = '/Users/felixsimard/OneDrive - McGill University/Personal/SeedAISummer2019/matchability/matchability_api/matchability_lib/intercom_scripts.pem'
ssh_private_key = '/root/core-bot/intercom_scripts.pem'

# db variables
user = 'gisapi_prod'
password = '7Src3pPn8t2d'
# old password: RQUTA5S8JPTMpbpK
# new password: 7Src3pPn8t2d
database = 'gisapi_prod_production'

# Run the extraction queries and save to CSVs

print("SQL Data Extraction.")

tic = time.time()
# Fetch the opportunities
# old path: sql/aiesec_opportunities_extraction.sql
opps = execute_sql("/root/matchability_api/current/matchability_api/matchability_lib/sql/aiesec_opportunities_extraction.sql", "aiesec_opportunities_extracted.csv")
toc = time.time()
print("Opportunities data extraction took:", round((toc-tic), 2), "seconds")

# Fetch the applications
# old path: sql/aiesec_applications_extraction.sql
tic = time.time()
apps = execute_sql("/root/matchability_api/current/matchability_api/matchability_lib/sql/aiesec_applications_extraction.sql", "aiesec_applications_extracted.csv")
toc = time.time()
print("Applications data extraction took:", round((toc-tic), 2), "seconds")


###----------------------------------------------------------------------###

###----------------------------- FETCH DATA -----------------------------###

# Load opportunities CSV table
print("Extracting...", "\n")
print("Reading data...a moment please...")
opps = pd.read_csv('Data/aiesec_opportunities_extracted.csv', low_memory=False)
apps = pd.read_csv('Data/aiesec_applications_extracted.csv', low_memory=False)
print("Total opportunities:", len(opps), "\n")

print("---------------------------------------------------------------", "\n")

#print("Dropping duplicate rows.", "\n")
#opps = opps.drop_duplicates(subset=['opportunity_id'])

print("Total opportunities:", len(opps), "\n")
opps = opps[:100000]
apps = apps.loc[apps['an_status'] == "accepted"]
print("Total opportunities:", len(opps), "\n")
print("Total 'accepted' applications:", len(apps), "\n")

print("###----------------------------------------------------------------------###", "\n")
###----------------------------------------------------------------------###


###---------------------- DATA CLEANING + TRIMMING ----------------------###
print("\n")
print("###---------------------- DATA CLEANING + TRIMMING ----------------------###", "\n")

# 500 openings threshold, ignore the others
limit = 500
print("Applying 500 openings threshold to opportunities.")
print(len(opps.loc[opps['openings'] > limit]), "rows ignored.", "\n")
opps = opps.loc[opps['openings'].apply(lambda x : x <= limit)]

# also ignore the opportunities with 0 openings
print("Ignore opportunities having 0 openings.")
print(len(opps.loc[opps['openings'].apply(lambda x : x == 0)]), "rows ignored.", "\n")
opps = opps.loc[opps['openings'].apply(lambda x : x != 0)]

# replacing possible infinite values
print("Replacing possible infinite values.", "\n")
opps = opps.replace([np.inf, -np.inf, "nan", "NaN"], 0)
#opps.dropna(inplace=True)

# finally, ignore the opportunities where status was not 'open'
print("Ignore opportunities with status != 'open'.")
print(len(opps.loc[opps['status'] != 0.0]), "rows ignored.", "\n")
opps = opps.loc[opps['status'] == 0.0]
# drop the "Unnamed: ..." columns
try:
    opps = opps.drop(columns=['Unnamed: 0'])
except Exception as e:
    pass

print("Cleaning date columns.")

# Date columns cleaning
date_columns = ['created_at', 'applications_close_date', 'earliest_start_date', 'latest_end_date']
for column in date_columns:
    # run the date cleaning process on the column
    print("Cleaning date column:", column)
    bad_dates = scanDates(opps, column)
    print(bad_dates)
    cleanDates(opps, column, bad_dates)
    # Now, if any other dates are found to be incorrectly formatted
    remaining_dates_indexes = scanDates(opps, column)
    # Now we simply delete the remaining badly formatted dates...
    opps = removeRows(opps, column, remaining_dates_indexes)

print("Total rows after first cleaning and trimming:", len(opps), "\n")

print("###----------------------------------------------------------------------###", "\n")
###----------------------------------------------------------------------###


###-------------------------- DATA MANIPULATIONS -----------------------###
print("\n")
print("###-------------------------- DATA MANIPULATIONS -----------------------###", "\n")

# Merge the skills columns together for k-means later
try:
    opps['skills'] = opps[['opp_skill_req', 'opp_skill_pref', 'opp_background_req', 'opp_background_pref']].apply(lambda x: ','.join(x[x.notnull()]), axis = 1)
except Exception as e:
    pass;

# We can now drop the individual skill columns
try:
    pass
    #opps = opps.drop(columns=['opp_skill_req', 'opp_skill_pref', 'opp_background_req', 'opp_background_pref', 'opp_language_pref', 'matched_or_rejected_at', 'experience_start_date', 'experience_end_date', 'status'])
except Exception as e:
    print("Error dropping irrelevant columns:", e, "\n")

print("Appending extra columns of interest.")

### New variables of interest ###
columns = ['opportunity_id', 'accepted_count', 'application_open_window', 'experience_max_duration',
           'created_vs_earliest_start', 'created_vs_latest_end', 'experience_timeframe_rigidness',
           'hot_days_intersection', 'popular_time_period_factor']
extra_cols_df = pd.DataFrame(columns=columns)
data_list = []

for index, row in opps.iterrows():
    opp_id = row['opportunity_id']
    sample = apps.loc[apps['opportunity_id'] == opp_id]
    duration_min = row['duration_min']
    earliest_start_date = row['earliest_start_date']
    accepted_count = len(sample.loc[sample['an_status'] == 'accepted'])
    opp_year = pd.to_datetime(row['earliest_start_date']).year

    # Hot Summer zone setup
    year_str = str(opp_year)
    if year_str == "" or year_str == "nan" or year_str == "NaN":
        year_str = "2018"
    hot_zone_start = year_str+'-07-01 00:00:00';
    hot_zone_end = year_str+'-08-31 00:00:00';
    hot_days_list = []
    for hot_day in range(0, 31):
        hot_day_datetime = pd.to_datetime(hot_zone_start)
        hot_days_list.append(hot_day_datetime)
        hot_day_datetime += timedelta(days=1)
        hot_zone_start = hot_day_datetime


    # New variables of interest

    # Duration to apply for the internship: application_close_date - created_at
    time_window_to_apply = dateDiff(row['applications_close_date'], row['created_at'])

    # Duration available of the intership: latest_end_date - earliest_end_date
    experience_max_duration = dateDiff(row['latest_end_date'], row['earliest_start_date'])

    # Difference between created_at and earliest_start_date
    created_vs_earliest_start = dateDiff(row['earliest_start_date'], row['created_at'])

    # Difference between lastest_end_date and created_at
    created_vs_latest_end = dateDiff(row['latest_end_date'], row['created_at'])

    # How rigid is the timeframe of the internship? (units: number of days)
    experience_timeframe_rigidness = round((experience_max_duration / duration_min), 1)

    # "Hot summer zones overlap". Find the intersection with the 'hot_days_list' and the range of dates
    # earliest_start_date - latest_end_date
    hot_days_intersection = 0
    popular_time_period_factor = 0
    start = earliest_start_date

    # Handle the NaN possible duration_min value
    if str(duration_min) == "nan" or type(duration_min) == "float":
        duration = 0
    else:
        duration = duration_min

    # compute the popular_time_period_factor --> how many possible days of the experience intersect the "popular summer days"
    for day in range(0, int(duration)):
        start_datetime = pd.to_datetime(start)

        if start_datetime in hot_days_list:
            hot_days_intersection += 1

        start_datetime = start_datetime + timedelta(days=1)
        start = start_datetime

    popular_time_period_factor = round((hot_days_intersection / len(hot_days_list)), 1)

    # build the row to be appended
    df_data = [opp_id, accepted_count, time_window_to_apply, experience_max_duration, created_vs_earliest_start,
              created_vs_latest_end, experience_timeframe_rigidness, hot_days_intersection, popular_time_period_factor]

    # construct the dataframe to be concatenated to the main dataframe
    df = pd.DataFrame([df_data], columns=extra_cols_df.columns)
    data_list.append(df)

extra_cols_df = pd.concat(data_list)
# Merge the newly created variables to the cleaned opportunities table
opps = pd.merge(opps, extra_cols_df, how='right', on='opportunity_id')

print("Done adding new variables of interest. Begin adding the one-hot encoded variables, matrices and others.", "\n")


### TITLE AND DESCRIPTION LENGTH ###
print("Adding length of title and description.")
def getTextLength(x):
    if type(x) != float and str(x) != "" and str(x) != "NaN":
        return len(x)
    else:
        return 0
# compute title length
opps['title_len'] = opps['title'].apply(getTextLength)

# compute description length
opps['description_len'] = opps['description'].apply(getTextLength)
print("Done adding length of title and description.", "\n")


### NUMBER OF LANGUAGES REQUIRED ###
print("Adding number of languages required for the opportunity.")
def getNumLanguages(x):
    if type(x) != float and str(x) != "" and str(x) != "NaN":
        return len(x.split(','))
    else:
        return 0

opps['num_languages'] = opps['opp_language_req'].apply(getNumLanguages)
print("Done adding number of languages.", "\n")

### NUMBER OF SKILLS REQUIRED ###
print("Adding number of languages required for the opportunity.")

opps['num_skills'] = opps['opp_skill_req'].apply(getNumLanguages)
print("Done adding number of skills.", "\n")

### NUMBER OF BACKGROUNDS REQUIRED ###
print("Adding number of backgrounds required for the opportunity.")

opps['num_backgrounds'] = opps['opp_background_req'].apply(getNumLanguages)
print("Done adding number of backgrounds.", "\n")


### HAS COVER PICTURE ###
print("Adding if has cover picture or not.")
def getHasCoverOrProfilePic(x):
    if type(x) != float and str(x) != "" and str(x) != "NaN":
        return 1
    else:
        return 0

opps['has_cover_pic'] = opps['cover_photo_file_size'].apply(getHasCoverOrProfilePic)
print("Done adding if has cover picture.", "\n")

### HAS PROFILE PICTURE ###
print("Adding if has profile picture or not.")
opps['has_profile_pic'] = opps['profile_photo_file_size'].apply(getHasCoverOrProfilePic)
print("Done adding if has profile picture.", "\n")


### PROJECT FEE CENTS ###
print("Adding project fee cents.")
def getProjectFeeCents(x):
    if type(x) != float and str(x) != "" and str(x) != "NaN":
        return x
    else:
        return 0
opps['project_fee_cents'] = opps['project_fee_cents'].apply(getHasCoverOrProfilePic)
print("Done adding project fee cents.", "\n")


### SALARY ###
print("Adding salary from opportunity.")
def getSalary(x):
    if type(x) != float and str(x) != "" and str(x) != "NaN":
        unwanted_str = ['$', 'USD', 'rub', ' ']
        specifics = x.split(',')
        has_salary_specified = False
        for spec in specifics:
            spec = spec.replace('"', '')
            attribute = spec.split('=>')
            if attribute[0] == 'salary':
                has_salary_specified = True
                s = attribute[1].strip()
                for i in unwanted_str:
                    s = s.replace(i, '')
                if s.isdigit():
                    return s
                else:
                    return 0

            if not has_salary_specified:
                return 0
    else:
        return 0

opps['salary'] = opps['specifics_info'].apply(getSalary)
print("Done adding opportunity salary.", "\n")

### EXTRACT SOME VARIABLES FROM THE HASMAP LIKE TEXTFIELDS ###
print("Extracting some new variables.")
### SPECIFICS INFO ###

df_list = []
specs_df = pd.DataFrame()
for i in range(len(opps[:])):
    df = pd.DataFrame()
    opp_id = opps.loc[i, "opportunity_id"]
    data = {"opportunity_id":[opp_id]}
    specific = opps.loc[i, "specifics_info"]
    if type(specific) != float and str(specific) != "nan":
        specific = specific.replace('"', '')
        specific = specific.replace('\\', '')
        specific = specific.replace('', '')
        specs = specific.split(',')
        for spec in specs:
            attribute = spec.split("=>")
            try:
                att = attribute[0].strip()
                val = attribute[1].strip()
                if att == "expected_work_schedule":
                    data[att] = [1]
                elif att != ":to" and att != "to":
                    data[att] = [val]
            except Exception:
                pass
    df = pd.DataFrame.from_dict(data)
    df_list.append(df)

specs_df = pd.concat(df_list)
specs_df = specs_df.fillna("undefined")

### LEGAL INFO ###

df_list = []
legal_df = pd.DataFrame()
for i in range(len(opps[:])):
    df = pd.DataFrame()
    opp_id = opps.loc[i, "opportunity_id"]
    data = {"opportunity_id":[opp_id]}
    legal = opps.loc[i, "legal_info"]
    if type(legal) != float and str(legal) != "nan":
        legal = legal.replace('"', '')
        legal = legal.replace('\\', '')
        legal = legal.replace('', '')
        leg = legal.split(',')
        for l in leg:
            attribute = l.split("=>")
            try:
                att = attribute[0].strip()
                val = attribute[1].strip()
                data[att] = [val]
            except Exception:
                pass
    df = pd.DataFrame.from_dict(data)
    df_list.append(df)
legal_df = pd.concat(df_list)
legal_df = legal_df.fillna("undefined")

### ROLE INFO ###

df_list = []
role_df = pd.DataFrame()
for i in range(len(opps[:])):
    df = pd.DataFrame()
    opp_id = opps.loc[i, "opportunity_id"]
    data = {"opportunity_id":[opp_id]}
    role = opps.loc[i, "role_info"]
    if type(role) != float and str(role) != "nan":
        role = role.replace('"', '')
        role = role.replace('\\', '')
        role = role.replace('', '')
        ro = role.split(',')
        for r in ro:
            attribute = r.split("=>")
            try:
                att = attribute[0].strip()
                val = attribute[1].strip()
                data[att] = [val]
            except Exception:
                pass
    df = pd.DataFrame.from_dict(data)
    df_list.append(df)
role_df = pd.concat(df_list)
role_df = role_df.fillna("undefined")

### LOGISTICS INFO ###

df_list = []
logistics_df = pd.DataFrame()
for i in range(len(opps[:])):
    df = pd.DataFrame()
    opp_id = opps.loc[i, "opportunity_id"]
    data = {"opportunity_id":[opp_id]}
    opp_id = opps.loc[i, "opportunity_id"]
    logistic = opps.loc[i, "logistics_info"]
    if type(logistic) != float and str(logistic) != "nan":
        logistic = logistic.replace('"', '')
        logistic = logistic.replace('\\', '')
        logistic = logistic.replace('', '')
        logi = logistic.split(',')
        for l in logi:
            attribute = l.split("=>")
            try:
                att = attribute[0].strip()
                val = attribute[1].strip()
                data[att] = [val]
            except Exception:
                pass
    df = pd.DataFrame.from_dict(data)
    df_list.append(df)

logistics_df = pd.concat(df_list)
logistics_df = logistics_df.fillna("undefined")

# New Dataframe with the relevant columns
info_df = pd.DataFrame()
info_df = pd.concat([specs_df])
info_df = pd.merge(info_df, legal_df, how='right', on='opportunity_id')
info_df = pd.merge(info_df, role_df, how='right', on='opportunity_id')
info_df = pd.merge(info_df, logistics_df, how='right', on='opportunity_id')

columns_to_format = ['ef_test_required', 'saturday_work', 'accommodation_covered', 'health_insurance_info', "food_weekends", "computer"]
mapping = [('true', '1'), ('false', '0'), ('Not compulsory', 'replaced_words'), ('not compulsory', 'replaced_words'), ('Not mandatory', 'replaced_words'), ('not mandatory', 'replaced_words')]
for col in columns_to_format:
    for k, v in mapping:
        info_df[col] = info_df[col].replace(k, v)

def setHealthInsuranceNeeded(x):
    if "mandatory" in x or "compulsory" in x:
        return 1
    else:
        return 0

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
            return num[0]
        else:
            return 0

# apply the functions above to extract variables
info_df['health_insurance_needed'] = info_df['health_insurance_info'].apply(setHealthInsuranceNeeded)
info_df['is_transportation_covered'] = info_df['transportation_covered'].apply(setTransportationCovered)
info_df['num_meals'] = info_df['food_covered'].apply(setNumMeals)

# undefined ==> 0
info_df = info_df.replace("undefined", "0")

info_df_columns = [info_df['opportunity_id'],
                   info_df['computer'],
                   info_df['expected_work_schedule'],
                   info_df['saturday_work'],
                   info_df['accommodation_covered'],
                   info_df['food_weekends'],
                   info_df['health_insurance_needed'],
                   info_df['is_transportation_covered'],
                   info_df['num_meals']
                  ]

info_df_relevant = pd.DataFrame()
info_df_relevant = pd.concat(info_df_columns, axis=1)

opps = pd.merge(opps, info_df_relevant, how='right', on='opportunity_id')

print("Done extracting the new variables.", "\n")

### IS FOOD PROVIDED ###
print("Adding whether food is provided or not.")
def getFoodProvided(x):
    if type(x) != float and str(x) != "" and str(x) != "NaN":

        logistics = x.split(',')
        for logis in logistics:
            logis = logis.replace('"', '')
            attribute = logis.split('=>')
            has_food_specified = False
            if attribute[0] == 'food':
                has_food_specified = True
                is_provided = attribute[1].strip()
                if is_provided != 'not provided':
                    return 1
                else:
                    return 0
            if not has_food_specified:
                return 0
    else:
        return 0

opps['food_provided'] = opps['logistics_info'].apply(getFoodProvided)
print("Done adding if food is provided.", "\n")


### ADD COUNTRY CODE + HUMAN DEVELOPMENT INDEX ###
print("Constructing the country code and HDI dataframes.")
hdi = pd.read_csv('Data/hdi_gdp_2015.csv', low_memory=False)
columns = ['opportunity_id', 'country_code', 'hdi']

hdi_df = pd.DataFrame(columns=columns)

data_list = []
for index, row in opps.iterrows():
    country = row['name_entity']
    opp_id = row["opportunity_id"]
    try:
        country_code = lookup_country[country][1]
        hdi_array = hdi.loc[hdi['Code'] == country_code]['Historical Index of Human Development (including GDP metric) ((0-1; higher values are better))'].values
        if hdi_array[0] != "":
            hdi_index = hdi_array[0]
        else:
            hdi_index = 0.5
    except:
        hdi_index = 0.5

    df_data = [opp_id, country_code, hdi_index]
    df = pd.DataFrame([df_data], columns=hdi_df.columns)
    data_list.append(df)



hdi_df = pd.concat(data_list)

# Merge the country code + HDI dataframe to the cleaned opportunities table
print("Merging the country codes and HDI.", "\n")
opps = pd.merge(opps, hdi_df, how='right', on='opportunity_id')


### PROGRAMME ID MATRIX + MONTH OF YEAR RATIO ###
print("Constructing the programme ID matrix.")
# Define column names
programs = ['Global Volunteer', 'Global Talent', 'Global Entrepreneur']
columns = ['opportunity_id', 'year_completion_ratio', 'is_global_volunteer', 'is_global_talent', 'is_global_entrepreneur']
programme_matrix = pd.DataFrame(columns=columns)

data_list = []
for index, row in opps.iterrows():
    program_name = row['programme_id']
    opp_id = row["opportunity_id"]

    # Fetch the month value
    month = str(row["earliest_start_date"]).split('-')
    try:
        if month[1] != "":
            month_ratio = round(((int(month[1]) - 1) / (12)), 2)
        else:
            month_ratio = 0.00
    except:
        month_ratio = 0.00


    try:
        which_program = programs.index(program_name)
    except:
        which_program = 0

    df_data = [opp_id, month_ratio, 0, 0, 0]
    df_data[which_program+2] = 1

    df = pd.DataFrame([df_data], columns=programme_matrix.columns)
    data_list.append(df)


programme_matrix = pd.concat(data_list)
# Merge the programme ID matrix and year completion ratio dataframe to the cleaned opportunities table
print("Merging the programme ID matrix.", "\n")
opps = pd.merge(opps, programme_matrix, how='right', on='opportunity_id')


### REGION MATRIX ###
print("Constructing the regions matrix.")
# Define column names
columns = ['opportunity_id', 'is_americas', 'is_asia_pacific', 'is_europe', 'is_middle_east_africa']
region_matrix = pd.DataFrame(columns=columns)

data_list = []
for index, row in opps.iterrows():
    region = row['name_region']
    opp_id = row["opportunity_id"]
    if region == "Americas" :
        df_data = [opp_id, 1, 0, 0, 0]
    elif region == "Asia Pacific":
        df_data = [opp_id, 0, 1, 0, 0]
    elif region == "Europe":
        df_data = [opp_id, 0, 0, 1, 0]
    elif region == "Middle East and Africa":
        df_data = [opp_id, 0, 0, 0, 1]
    else:
        df_data = [opp_id, 0, 0, 0, 0]

    df = pd.DataFrame([df_data], columns=region_matrix.columns)
    data_list.append(df)

region_matrix = pd.concat(data_list)
# Merge the regions matrix dataframe to the cleaned opportunities table
print("Merging the regions matrix.", "\n")
opps = pd.merge(opps, region_matrix, how='right', on='opportunity_id')


### K-MEANS for JOB DESCRIPTION ###

print("Starting text analysis of the experience descriptions.", "\n")
desc_df = pd.DataFrame()
desc_df['opportunity_id'] = opps['opportunity_id']
desc_df['skills'] = opps['skills']

print("Formatting corpus for text mining and k-means.")
# Need to replace the special characters, format the corpus
desc_df.skills = desc_df.skills.str.replace('&', 'and')
desc_df.skills = desc_df.skills.str.replace('(', '')
desc_df.skills = desc_df.skills.str.replace(')', '')
desc_df.skills = desc_df.skills.str.replace('-', 'dash')
desc_df.skills = desc_df.skills.str.replace('/', ' ')
desc_df.skills = desc_df.skills.str.replace(' ', '_')
desc_df.skills = desc_df.skills.str.replace(',', ' ')
print("Done formatting.", "\n")

# Standard TF/IDF procedure
corpus = desc_df.skills
vec = CountVectorizer(min_df=0.001) # at least one occurrence in 1000
X = vec.fit_transform(corpus)
df = pd.DataFrame(X.toarray(), columns=vec.get_feature_names())
# drop the 'other' column (useless and irrelevant)
df = df.drop(columns=['other'])
df['opportunity_id'] = desc_df['opportunity_id']

vectorizer = TfidfVectorizer()
#response = vectorizer.fit_transform(desc_df.skills)
vec = vectorizer.fit(desc_df.skills)
response = vec.transform(desc_df.skills)
X = response.toarray()
# set number of clusters
NUM_CLUSTERS = 10
kmeans_groups = KMeans(NUM_CLUSTERS, n_init=20, random_state=0).fit(X)
centers = kmeans_groups.cluster_centers_
labels = kmeans_groups.predict(X)

# Save vectorizer object as Python pickle
pickle.dump(vec, open("pickles/vectorizer.pickle", 'wb'))

# Save kmeans object as Python pickle
pickle.dump(kmeans_groups, open("pickles/kmeans.pickle", 'wb'))

print("Fetching top words per clusters.", "\n")
order_centroids = kmeans_groups.cluster_centers_.argsort()[:, ::-1]
terms = vectorizer.get_feature_names()

# Get the size of each cluster
cluster_map = pd.DataFrame()
cluster_map['cluster'] = kmeans_groups.labels_
cluster_map['opportunity_id'] = desc_df['opportunity_id']

# prepare the column names list to be ventually merged to the main opportunities dataframe
columns_name_list = [["cl1"], ["cl2"], ["cl3"], ["cl4"], ["cl5"], ["cl6"], ["cl7"], ["cl8"], ["cl9"], ["cl10"]]
for i in range(len(centers)):
    friendly_cluster_index = i+1
    print("Cluster", friendly_cluster_index, "has a size of", len(cluster_map[cluster_map.cluster == i]))
    #print("Top words are:")
    index=0;
    for ind in order_centroids[i, :10]:
        if index==0 or index==1:
            columns_name_list[i].append(terms[ind])
        print('%s' % terms[ind], end=',')
        index += 1
    print("\n")

# now we construct the custom column names based on the cluster centers
for i in range(len(columns_name_list)):
    columns_name_list[i] = '_'.join(columns_name_list[i])


# Save cluster terms object as Python pickle
pickle.dump(columns_name_list, open("pickles/cluster_terms.pickle", 'wb'))

columns_name_list.append("opportunity_id")

# Create a dataFrame for job description categories merging
category_df = pd.DataFrame(columns=columns_name_list)
category_df['opportunity_id'] = desc_df['opportunity_id']
category_merging_df = pd.DataFrame(columns=columns_name_list)

data_list = []
for i in range(len(cluster_map)):

    df_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, cluster_map['opportunity_id'][i]]
    df_data[cluster_map['cluster'][i]] = 1

    df = pd.DataFrame([df_data], columns=category_df.columns)
    data_list.append(df)

category_merging_df = pd.concat(data_list)
# Merge the job description matrix dataframe to the cleaned opportunities table
print("Merging the job description categories.", "\n")
opps = pd.merge(opps, category_merging_df, how='right', on='opportunity_id')
print("Total opportunities:", len(opps))

print("\n")

### EXPAND OPPORTUNITIES BY OPENINGS ###
# Expand opportunities --> one row for one opening
print("Expanding the current dataframe to the format: one row for one opening.")
# use the same columns as the current table
column_names = opps.columns
# add our Y variable, which is whether the opportunity has found a match or not (true or false)
column_names = column_names.append(pd.Index(["matched"]))


# Make sure the openings and accepted_count columns are of 'int' type only
opps.openings = opps.openings.astype(int)
opps.accepted_count = opps.accepted_count.astype(int)

# Start iterating over the opportunities
merged = pd.DataFrame(columns=column_names)
data_list = []
print("Iterating over the current opportunities dataframe. This may take a few minutes...")

# start a timer
t0 = time.time();
index = 0

# for efficiency purposes, we will append all single row dataframes to a list and then
# concatenate the list of dataframes together
df_list = []
for index, row in opps.iterrows():
    row_data = row.values
    row_columns = row.index
    try:
        num_openings = row['openings']
        num_matched = row['accepted_count']
    except Exception as e:
        print("Error:", e)

    # append the matched=True
    for i in range(num_matched):
        row_data = row.values
        row_data = row_data.tolist()
        row_data.append(1)
        df_list.append(pd.DataFrame([row_data], columns=column_names))

    # apppend the matched=False
    for i in range(num_openings - num_matched):
        row_data = row.values
        row_data = row_data.tolist()
        row_data.append(0)
        df_list.append(pd.DataFrame([row_data], columns=column_names))


# concatenate all the dataframes together
merged = pd.concat(df_list)
t1 = time.time()

print("Expanded opportunities dataframe now has:", len(merged), "rows.")
print("Expanding process took:", round(t1-t0, 2), "seconds")

print("###-----------------------------------------------------------------------###", "\n")

###-----------------------------------------------------------------------###


###--------------------------- MODELLING + MODEL ANALYSIS -----------------------------###
print("\n")
print("###--------------------------- MODELLING + MODEL ANALYSIS -----------------------------###", "\n")

### LOGISTIC REGRESSION ##
print("Beginning Logistic Regression.", "\n")

# start a timer
t0 = time.time();

# Fill in NaN values by the mean
merged.fillna(0, inplace=True)

# Assign the 'merged' dataframe
regression_data_df = merged

# Split training and testing data (70/30 respectively)
xtrain, xtest = train_test_split(regression_data_df, test_size=0.3)
training_data = xtrain
testing_data = xtest

print("Size of training data:", len(training_data))
print("Size of testing data:", len(testing_data), "\n")

# Define the predictors DataFrame as well as the target DataFrame
df_train = pd.DataFrame(training_data)
df_test = pd.DataFrame(testing_data)
target_train = pd.DataFrame(training_data['matched'], columns=['matched'])
target_test = pd.DataFrame(testing_data['matched'], columns=['matched'])

# list the features of interest: CAREFUL WITH THE CLUSTER COLUMN NAMES
# Create the list of features we want to consider for the model

features = [

            'openings',
            'duration_min',
            'application_open_window',
            'experience_max_duration',
            'created_vs_earliest_start',
            'created_vs_latest_end',
            'experience_timeframe_rigidness',

            'title_len',
            'description_len',
            'num_languages',
            'salary',

            'project_fee_cents',
            'num_skills',
            'num_backgrounds',
            'has_cover_pic',
            'has_profile_pic',
            'computer',
            'expected_work_schedule',

            'accommodation_covered',
            'food_weekends',
            'health_insurance_needed',
            'is_transportation_covered',
            'num_meals',

            'is_americas',
            'is_asia_pacific',
            'is_europe',
            'is_middle_east_africa',
            'hdi',
            'year_completion_ratio',
            'is_global_volunteer',
            'is_global_talent',
            'is_global_entrepreneur'

            ]

# Append the custom cluster column names to the features to be considered
custom_columns_categories = category_df.columns
custom_columns_categories = custom_columns_categories[:-1]
for i in range(len(custom_columns_categories)):
    features.append(custom_columns_categories[i])

# Define our X/y variables
X_train = df_train[features] # pass the list of features to be considered
X_test = df_test[features] # pass the list of features to be considered
y_train = target_train["matched"]
y_test = target_test["matched"]


print("Ratio of 1s:", len(target_train.loc[target_train['matched'] == 1]) / len(target_train))
print("Ratio of 0s:", len(target_train.loc[target_train['matched'] == 0]) / len(target_train), "\n")

# Scan over the features and make sure no columns have only zeros (would cause a 'Singular Matrix Error')
# Apply changes to both the X_train and X_test dataframes to respect the shape of training and testing data


for feat in features:
    is_only_zeros = (X_train[feat] == 0).all()
    if is_only_zeros:
        X_train = X_train.drop(columns=[feat])
        X_test = X_test.drop(columns=[feat])


# Save features object as Python pickle
pickle.dump(X_train.columns, open("pickles/features.pickle", 'wb'))

print("Training model...")


# Train Model
try:

    # train the model
    model = sm.Logit(y_train.astype(float), X_train.astype(float), missing='drop').fit(start_params=None, maxiter=100)

    # predict on the testing data
    predictions = model.predict(X_test.astype(float))

    print("Model Trained Successfully.", "\n")
    t1 = time.time()
    print("Elapsed time:", round(t1-t0, 2), "seconds", "\n")
except Exception as e:
    print("Sorry, an error occurred while training the model (Logistic Regression). Please re-run the program again.")
    print("Error:", e, "\n")


### MODEL ANALYSIS FOR LOGISTIC REGRESSION ###

print("Beginning Model Analysis of Logistic Regression.", "\n")

print("Creating new dataframe for predictions of matched opportunities.", "\n")
# New DataFrame for ROC curve analysis
roc_df = pd.DataFrame(columns=["matched", "pred"])


# add predictions to dataframe
roc_df['pred'] = predictions
roc_df['matched'] = y_test.values


# fill nan values
roc_df['pred'].fillna(roc_df['pred'].mean(), inplace=True)

print("Plotting the ROC curve.", "\n")

# plot the 'False Positive Rate' vs the 'True Positive Rate'
fpr, tpr, thresholds = roc_curve(y_test, roc_df['pred'])

# get the area under the ROC curve
print("Computing the Area Under the ROC Curve.")
roc_auc = auc(fpr, tpr)
print("Area under the ROC curve: %f" % roc_auc, "\n")

# results summary
#print(model.summary(), "\n")

# show p-values
#print("P-values:")
#print(model.pvalues, "\n")

i = np.arange(len(tpr))
roc = pd.DataFrame({'fpr' : pd.Series(fpr, index=i),'tpr' : pd.Series(tpr, index = i), 'fpr' : pd.Series(fpr, index = i), 'tf' : pd.Series(tpr - (fpr), index = i), 'thresholds' : pd.Series(thresholds, index = i)})
roc.iloc[(roc.tf-0).abs().argsort()[:1]]


# Test Model on testing data
predictions_new = model.predict(X_test.astype(float))

print("------------------------------------")
print("Logistic Regression Score:", ((predictions_new>0.5) == y_test).mean())
print("------------------------------------", "\n")

# Plotting
'''
fig, ax = plt.subplots(figsize=(10, 10))
plt.plot([0,1], [0,1], linestyle='--')
plt.plot(roc['fpr'], roc['tpr'], color='red')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
ax.set_xticklabels([])


print("Saving plot...")
filename = 'roc_logisitic_regression.png'
plt.savefig("Resources/"+filename)
print("Plot saved as", filename, "\n")
'''



print("End of logistic regression.", "\n")


### DECISION TREE ###

print("\n")
print("------------------------------------------------------------------------")
print("\n")
print("Beginning Decision Tree Classifier.", "\n")

# start a timer
t0 = time.time();

# Train Decision Tree Classifier
try:
    # train model
    model = tree.DecisionTreeClassifier(random_state=0, min_samples_leaf=100)
    model.fit(X_train.astype(float), y_train.astype(float))

    # predict on testing data
    #predictions_tree = model.predict(X_test.astype(float)) # change X_train for X_test

    predictions_tree = model.predict_proba(X_test.astype(float))

    predictions_tree_proba = []
    for pred in predictions_tree:
        predictions_tree_proba.append(pred[1])

    # create a series from the pred
    predictions_tree_series = pd.Series(predictions_tree_proba, name="pred")

    print("Model Trained Successfully.", "\n")
    t1 = time.time()
    print("Elapsed time:", round(t1-t0, 2), "seconds", "\n")
except Exception as e:
    print("Sorry, an error occurred while training the model (Decision Tree Classifier). Please re-run the program again.")
    print("Error:", e, "\n")

'''
print("Visualizing the decision tree. This will open a new window with a PDF image of the decision tree.", "\n")
dot_data = StringIO()
dot_data = tree.export_graphviz(model, out_file=None, feature_names=X_train.columns, leaves_parallel=True, filled=True, rounded=True, special_characters=True)
graph = graphviz.Source(dot_data)
graph.view()
'''


### MODEL ANALYSIS FOR DECISION TREE ###

print("Beginning Model Analysis of Decision Tree.", "\n")


# Test Model on testing data
# Need to reformat the predictions and y values first
y_test = y_test.reset_index(drop=True)

print("------------------------------------")
print("Decision Tree Score:", ((predictions_tree_series>0.5) == y_test).mean())
print("------------------------------------", "\n")


print("Creating new dataframe for predictions of matched opportunities.", "\n")
# New DataFrame for ROC curve analysis
roc_df_tree = pd.DataFrame(columns=["matched", "pred"])

# add predictions to dataframe
roc_df_tree['pred'] = predictions_tree_series
roc_df_tree['matched'] = y_test.values


# fill nan values
roc_df_tree['pred'].fillna(roc_df_tree['pred'].mean(), inplace=True)

print("Plotting the ROC curve.", "\n")
# plot the 'False Positive Rate' vs the 'True Positive Rate'
fpr, tpr, thresholds = roc_curve(y_test.astype(float), roc_df_tree['pred'])

# get the area under the ROC curve
print("Computing the Area Under the ROC Curve.")
roc_auc = auc(fpr, tpr)
print("Area under the ROC curve: %f" % roc_auc, "\n")

i = np.arange(len(tpr))
roc = pd.DataFrame({'fpr' : pd.Series(fpr, index=i),'tpr' : pd.Series(tpr, index = i), 'fpr' : pd.Series(fpr, index = i), 'tf' : pd.Series(tpr - (fpr), index = i), 'thresholds' : pd.Series(thresholds, index = i)})
roc.iloc[(roc.tf-0).abs().argsort()[:1]]

'''
# Plotting
fig, ax = plt.subplots(figsize=(10, 10))
plt.plot([0,1], [0,1], linestyle='--')
plt.plot(roc['fpr'], roc['tpr'], color='red')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
ax.set_xticklabels([])


print("Saving plot...")
filename = 'roc_decision_tree.png'
plt.savefig("Resources/"+filename)
print("Plot saved as", filename, "\n")
'''

print("End of decision tree classifier.", "\n")



###-----------------------------------------------------------------------###



### RANDOM FOREST CLASSIFIER ###

print("\n")
print("------------------------------------------------------------------------")
print("\n")
print("Beginning Random Forest Classifier.", "\n")

# start a timer
t0 = time.time();

# Train Random Forest Classifier

try:
    # train model
    print("Training Random Forest... this may take a minute...", "\n")
    model = RandomForestClassifier(n_estimators=100, random_state=0)
    model.fit(X_train.astype(float), y_train.astype(float))

    # Save model as python pickle
    pickle.dump(model, open("pickles/matcha_model.pickle", 'wb'))

    # Save testing columns names as pickle
    pickle.dump(features, open("pickles/matcha_columns.pickle", "wb"))

    # predict on testing data
    #predictions_tree = model.predict(X_test.astype(float)) # change X_train for X_test

    predictions_forest = model.predict_proba(X_test.astype(float))

    predictions_forest_proba = []
    for pred in predictions_forest:
        predictions_forest_proba.append(pred[1])

    # create a series from the pred
    predictions_forest_series = pd.Series(predictions_forest_proba, name="pred")

    print("Model Trained Successfully.", "\n")
    t1 = time.time()
    print("Elapsed time:", round(t1-t0, 2), "seconds", "\n")

except Exception as e:
    print("Sorry, an error occurred while training the model (Decision Tree Classifier). Please re-run the program again.")
    print("Error:", e, "\n")



### MODEL ANALYSIS FOR RANDOM FOREST ###

print("Beginning Model Analysis of Random Forest.", "\n")


# Show variable importances
importances = model.feature_importances_
std = np.std([tree.feature_importances_ for tree in model.estimators_], axis=0)
indices = np.argsort(importances)
features_list = X_train.columns.tolist()
for f in range(len(features_list)):
    # importances[indices[f]]
    #print("%d - %s" % (indices[f], features_list[indices[f]]))
    pass


'''
plt.figure(figsize=(10, 10))
plt.title("Feature Importances")
plt.barh(features_list[::-1], importances[indices],
       color=[(0, 0.552, 0.827)], align="center", linewidth=5)
plt.xlabel("Feature Score")
plt.show()
'''


# Test Model on testing data
# Need to reformat the predictions and y values first
y_test = y_test.reset_index(drop=True)
score = ((predictions_forest_series>0.5) == y_test).mean()
print("------------------------------------")
print("Random Forest Score:", score)
print("------------------------------------", "\n")

### OUTPUT TEXT FILE ###
f = open(r"Resources/model_output.txt", "a")

model_status = "Model trained successfully. \n"
model_score = "Score: "+str(score)+"\n"
model_trained_date = str(datetime.now())+"\n"
text = [model_status, model_score, model_trained_date, "\n"]
for t in text:
    f.write(t)

f.close()

###


print("Creating new dataframe for predictions of matched opportunities.", "\n")
# New DataFrame for ROC curve analysis
roc_df_forest = pd.DataFrame(columns=["matched", "pred"])

# add predictions to dataframe
roc_df_forest['pred'] = predictions_forest_series
roc_df_forest['matched'] = y_test.values


# fill nan values
roc_df_forest['pred'].fillna(roc_df_forest['pred'].mean(), inplace=True)

print("Plotting the ROC curve.", "\n")
# plot the 'False Positive Rate' vs the 'True Positive Rate'
fpr, tpr, thresholds = roc_curve(y_test.astype(float), roc_df_forest['pred'])

# get the area under the ROC curve
print("Computing the Area Under the ROC Curve.")
roc_auc = auc(fpr, tpr)
print("Area under the ROC curve: %f" % roc_auc, "\n")

i = np.arange(len(tpr))
roc = pd.DataFrame({'fpr' : pd.Series(fpr, index=i),'tpr' : pd.Series(tpr, index = i), 'fpr' : pd.Series(fpr, index = i), 'tf' : pd.Series(tpr - (fpr), index = i), 'thresholds' : pd.Series(thresholds, index = i)})
roc.iloc[(roc.tf-0).abs().argsort()[:1]]

'''
# Plotting
fig, ax = plt.subplots(figsize=(10, 10))
plt.plot([0,1], [0,1], linestyle='--')
plt.plot(roc['fpr'], roc['tpr'], color='red')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
ax.set_xticklabels([])

print("Saving plot...")
filename = 'roc_random_forest.png'
plt.savefig("Resources/"+filename)
print("Plot saved as", filename, "\n")
'''

print("End of random forest classifier.", "\n")


print("###------------------------------------------------------------------###", "\n")

print("###----------------- END OF MATCHABILITY -------------------------###", "\n")

###-----------------------------------------------------------------------###
