# AIESEC International Matchability API - Opportunity

Model trained to predict whether a newly created opportunity will find an applicant or not.

## Getting Started

Simple guide to train and run the opportunity matchability API.

### Prerequisites

Make sure sure the server/database's private key file is included in the same directory as matcha.py under the name:

```
intercom_scripts.pem
```

### Training the model

Train the model by running the Python file:
```
matcha.py
```
Note: training the model can take up to 15 minutes.

Tip: Re-train the model every month or so.


### Running the model

Open port 5000 on your server and run the process named:

```
matcha_api.py
```

To make a request to the API, simply make a POST request to the following URL:

```
http://matchability.aiesec.org/api/opportunity
```

and passing a JSON object in the following format:

```
{
    "data": {
      "created_at": "2014-11-05 00:00:00",
      "application_close_date": "2015-03-30 00:00:00",
      "earliest_start_date": "2015-02-01 00:00:00",
      "latest_end_date": "2015-07-31 00:00:00",
      "duration_min": 6,
      "name_entity": "Mexico",
      "name_region": "Americas",
      "title": "This is a test title",
      "description": "This is a test description for the matchability model. This is completely useless. Some more words.",
      "salary": 4000,
      "programme_id": 1,
      "opp_background_req": "Business administration",
      "opp_background_pref": "Public relations",
      "opp_skill_req": "Client servicing,Internet usage,Leadership,Organisational Management,Presentation skills,Team Management,Windows PC usage",
      "opp_skill_pref": "Sales",
      "opp_language_req": "English",
      "cover_picture_link": "https://adummylink/picture/image.png",
      "profile_picture_link": null,
      "project_fee_cents": 0,
      "openings": 2,
      "logistics_info": [
        {
          "food": "not provided", "food_covered":"2 meals per day", "accommodation":"provided", "transportation":"not provided", "arrival_reception":"airport", "support_for_destination":"Will be dropped to the office on the first day to help understand the daily travel route.",
          "accommodation_additional_info":"Will be in the range of 100 to 120 dollars.", "transportation_covered":"Return trip", "transportation_additional_info": "Will be covered during the induction interview after matching."
        }
      ],
      "specifics_info": [
        {
          "salary":"400", "salary_currency":"USD", "computer":"true", "expected_work_schedule":"{:from=>\"10:00\", :to=>\"18:00\"}", "saturday_work_schedule":"{:from=>\"10:00\", :to:\"15:00\"}"
        }
      ],
      "legal_info": [
        {
          "departure_info":"Will be helped to reach the airport.", "health_insurance_info":"This is not mandatory thanks.", "visa_work_permit_info":"Yes will be provided."
        }
      ],
      "role_info": [
        {
          "supervisor":"Mr John Doe", "learning_points":"Building a start-up.\r\nTeam building and management.", "expected_results":"Proper establishment of customer and product base.\r\nCreating a sustainable process that is successful and proper branding of the organization", "supervisor_title":"Owner", "development_spaces":"Invitation to AIESEC forums and activities and training meets to help understand AIESEC and develop interpersonal and professional skills.", "required_preparation":"Understanding how Marketing, sales and business development work in a company.", "additional_instructions":"None"
        }
      ]
    }
}

```

### API Response

Here is an example JSON response returned by an API request using the dummy data shown above:

```
{   
    'status': 'OK',
    'output': 'True',
    'value': 0.5926904761904762,
    'timestamp': '2019-08-07 11:21:38.581200'
}
```

## Training File

The model is trained by the following file:

```
matcha.py
```

Let's run through the code sequentially as it goes from extracting to training the model.

### Extraction

Upon connecting to the AIESEC server, extracting the applications and opportunities data from the AIESEC database are done using the following two SQL files:

```
aiesec_opportunities_extraction.sql
```
```
aiesec_applications_extraction.sql
```

Note: it is recommended to extract the data ranging from the last 36 months to the last 3 months to avoid biases.

The extracted rows are saved locally under the Data/ folder as mentioned later on.


### Cleaning

The  main challenge of training the model lies in getting the data clean and ready to be worked on.

The following actions are the cleaning procedures carried out to prepare the data.

```
Apply 500 openings threshold to opportunities.
```

```
Ignore opportunities having 0 openings.
```

```
Replace possible infinite values.
```

```
Ignore opportunities with status != 'open'.
```

```
Cleaning date columns.
date_columns = ['created_at', 'applications_close_date', 'earliest_start_date', 'latest_end_date']
```
As mentioned above, one of the most tricky cleaning occurs when working on the data field. We must make sure all the dates are in the format: YYYY-MM-DD 00:00:00
And, that each year, month and day value are in their respective range and make sense (ie: the year 1014 is impossible, meant to be 2014...)

Upon cleaning all the extracted data, it is expected to "lose" around 15-20% of the initial data. For example, an extraction of 60k rows will have about 45k rows remaining after cleaning.


### Manipulations & Formatting

Using the same format as shown for the cleaning of the data, here are the manipulations that were done on the data before being able to train the model.

```
Merge the following skills columns into one "skills" columns:
['opp_skill_req', 'opp_skill_pref', 'opp_background_req', 'opp_background_pref']
```
The above will be used to compute a K-Means clustering on the textual job descriptions.
Note the  library used to perform the K-Means and other of its procedures is the following:
```
from sklearn.cluster import KMeans
```
```
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
```

Now, we append/extract new columns/features of interest to the data table. Most are simply differences between dates or simple values extracted from the opportunities table.

```
['accepted_count', 'application_open_window', 'experience_max_duration', 'created_vs_earliest_start', 'created_vs_latest_end', 'experience_timeframe_rigidness']
```

Other features extracted:

```
Add length of title and description.
```

```
Add number of languages required for the opportunity.
```

```
Add number of languages required for the opportunity.
```

```
Add if has cover picture or not.
```

```
Add if has profile picture or not.
```

```
Add project fee cents.
```

```
Add salary from opportunity.
```

```
Add whether food is provided or not.
```

```
Add the Human Development Index for the respective country.
```

Now, we append the "one-hot encoded" variables which are the regions (Americas, Europe, Middle East and Africa, Asia Pacific) and the job descriptions clusters (to which cluster an opportunity belongs to based on the skills needed to apply for the internship)

Finally, in order to train the model, the longest step is to expand each opportunity row by the number of openings for it and keeping track of the number of accepted and empty spots. For instance, say a single row opportunity has 10 openings, 6 of which have accepted applicants (4 empty spots), then after expanding, we will have 10, basically identical, rows, 6 of which having the target variable (the one we want our model to eventually predict) set to 1 and the others set to 0.

### Training

We train the  model using three different modeling algorithms, but we keep one as the production model: a logistic regression, a decision tree and a random forest (used in production).

The Random Forest Classifier gets passed 41 features.
The split value between training and testing data is respectively 70/30.
The library used to properly split the data is the following:
```
from sklearn.model_selection import train_test_split
```

The Python package used to train the model is:
```
from sklearn.ensemble import RandomForestClassifier
```


### Analysis

To understand if our trained model is "accurate" or not, we need to test the model on the testing dataset as mentioned above. We then, compute the ratio of correctly predicted outcomes by the model versus the true values from the dataset.

Additionally, we can plot a Receiver Operating Characteristic curve which tells us how “good” the model is at predicting true matched opportunities from unmatched ones. The graph plots the True Positive Rate versus the False Negative Rate. The library used to compute the ROC analysis is the following:
```
from sklearn.metrics import roc_curve, auc, roc_auc_score
```

## Other file(s) and folder(s)

### API processing
```
matchability.py
```
Handles the formatting and processing of the incoming data from the API request. Calls the model (locally saved as a Python pickle file) and returns the output as a JSON response.


### Data Directory

This folder holds a CSV file of the Human Development Indexes for every country from 2015. This is used as a reference table when training the model. It should be kept unchanged.

Upon training the model, two CSV files are created/updated in this directory:
```
aiesec_opportunities_extracted.csv
```
```
aiesec_applications_extracted.csv
```

### Resources Directory

In this directory, besides the snapshots of the performance of each model, we have a text file:

```
model_output.txt
```

which keeps track of the model's status (accuracy, rate of of good classification and timestamp) as it is retrained each month or so.


## Authors

* **Felix Simard** - *Initial work*
* **Ali Soliman** - *Integration*
