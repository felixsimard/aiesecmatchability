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

## Other file(s) and folder(s)

### API processing
```
matchability.py
```
Handles the formatting and processing of the incoming data from the API request. Calls the model (locally saved as a Python pickle file) and returns the output as a JSON response.


### SQL extraction
```
aiesec_opportunities_extraction.sql
```
```
aiesec_applications_extraction.sql
```

### Data folder

This folder holds a CSV file of the Human Development Indexes for every country from 2015. This is used as a reference table when training the model. It should be kept unchanged.

Upon training the model, two CSV files are created/updated in this directory:
```
aiesec_opportunities_extracted.csv
```
```
aiesec_applications_extracted.csv
```


## Authors

* **Felix Simard** - *Initial work*
* **Ali Soliman** - *Integration*
