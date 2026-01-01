value_mappings = {
    'diet': {
        'I think my diet is somewhat in-between': 'Somewhat Inbetween',
        'I think my diet is somewhat inbetween': 'Somewhat Inbetween',
        'Yes, I think my diet is healthy': 'Healthy',
        'No, I think my diet is unhealthy': 'Unhealthy'
    },
    'ethnic_group': {
        'White': 'White',
        'Black/African/Caribbean/Black British': 'Black',
        'Asian/Asian British': 'Asian',
        'Mixed/multiple ethnic groups': 'Mixed',
        'Other ethnic group': 'Other'
    },
    'family_earning_class': {
        'Lower class (less than £25000 per annum)': 'Lower Class (below £25,000)',
        'Lower class (below £25,000)': 'Lower Class (below £25,000)',
        'Lower class': 'Lower Class (below £25,000)',
        'Middle class (between £25k and £90K)': 'Middle Class (£25,000-£54,999)',
        'Middle class (£25,000-£54,999)': 'Middle Class (£25,000-£54,999)',
        'Middle class': 'Middle Class (£25,000-£54,999)',
        'Higher class (£90001 or above per annum)': 'Higher Class (£55,000-£90,000)',
        'Higher class (£55,000-£90,000)': 'Higher Class (£55,000-£90,000)',
        'Higher class': 'Higher Class (£55,000-£90,000)',
        'Upper higher class (above £90,000)': 'Upper Higher Class (above £90,000)'
    },
    'quality_of_life': {
        'Medium quality of life': 'Medium',
        'Low quality of life': 'Low',
        'High quality of life': 'High',
        'Very Low quality of life': 'Very Low',
        'Very High quality of life': 'Very High'
    },
    'alcohol_consumption': {
        'My alcohol consumption is moderate': 'Moderate',
        "I don't drink alcohol": 'No Drinks',
        'My alcohol consumption is below moderate': 'Below Moderate',
        'My alcohol consumption is above moderate': 'Above Moderate'
    },
    'personality_type': {
        'Introvert (a quiet person who is more interested in their own thoughts and feelings than spending time with other people)': 'Introvert',
        'Extrovert (a lively and confident person who enjoys being with other people)': 'Extrovert',
        'Somewhat in between': 'Somewhat in-between'
    },
    'stress_in_general': {
        'Yes (due to employment-related issues)': 'Yes',
        'Yes (due to other circumstances, such as health, family issues, etc)': 'Yes',
        'Yes (due to university work)': 'Yes',
        'No': 'No',
        'Yes': 'Yes',
        'Yes (due to other circumstances, such as health, family issues, etc),No': 'Yes',
        'Yes (due to other circumstances, such as health, family issues, etc), Yes (due to university work)': 'Yes',
        'Yes (due to employment-related issues), Yes (due to other circumstances, such as health, family issues, etc)': 'Yes',
        'Yes (due to employment-related issues),Yes (due to other circumstances, such as health, family issues, etc),Yes (due to university work)': 'Yes',
        'Yes (due to university work),No': 'Yes',
        'Yes (due to employment-related issues), Yes (due to university work)': 'Yes'
    },
    'stress_before_exams': {
        'Yes (due to university work)': 'Yes',
        'Yes (due to employment-related issues)': 'Yes',
        'Yes (due to other circumstances such as health, family issues, etc)': 'Yes',
        'Yes': 'Yes',
        'No': 'No',
        "I don't have exams": 'No',
        "I don't normally have exams": 'No',
        'No (I am not stressed)': 'No'
    },
    'well_hydrated': {'Yes': 'Yes', 'No': 'No'},
    'financial_problems': {'Yes': 'Yes', 'No': 'No'},
    'feel_afraid': {
        'Very frequently': 'Very Frequently',
        'Rarely': 'Rarely',
        'Never': 'Never',
        'Occasionally': 'Occasionally',
        'Very rarely': 'Very Rarely',
        'Frequently': 'Frequently',
        'nan': 'Not Provided'
    },
    'timetable_preference': {
        'I prefer my timetable to be compact. (having all my classes in one day or two days in the week)': 'Compact',
        'I prefer my timetable to be spread with long gaps in between classes (eg, 1-2 modules per day, spread over 3 times per week)': 'Spread'
    },
    'timetable_impact': {
        'Yes': 'Yes',
        'No': 'No',
        'Not completed': 'No',
        'Yes, on my life, health and studies': 'Yes',
        'Yes, on my studies': 'Yes',
        'Yes, on my life and health': 'Yes',
        'No, it has no impact on my studies, life or health': 'No'
    },
    'student_type_time': {
        'I am a part-time student': 'Part Time',
        'I am a full-time student': 'Full Time',
        'I am unsure': "Don't Know"
    },
    'student_type_location': {
        'Home Student': 'Home student',
        'European Student': 'European student',
        'International Student': 'International student'
    },
    'form_of_employment': {
        'I am unemployed': 'Unemployed',
        'Yes, I am part-time employed': 'Part Time',
        'I am self-employed': 'Self Employed',
        'Yes, I am full-time employed': 'Full Time'
    },
    'sense_of_belonging': {
        "I don't know yet": "Don't Know",
        "I don't know how to answer this question": "Don't Know",
        'A little': 'Little',
        'Very much': 'Very Much'
    },
    'physical_activities': {
        'Yes, it helps a lot': 'Yes',
        'Yes, it sometimes helps': 'Yes',
        "I don't do physical activity": "Don't Know",
        "I've not really noticed if it helps or not": "Don't Know",
        'No, it does not help': 'No'
    },
    'level_of_study': {
        'Level 4': 'Level 4',
        'Level 4 ': 'Level 4',
        'Level 4 (first year, undergraduate)': 'Level 4',
        'Level 4 Foundation year': 'Level 4',
        'Foundation year': 'Level 4',
        'Level 5 (second year, undergraduate)': 'Level 5',
        'Level 6 (third year, undergraduate)': 'Level 6',
        'Level 7': 'Level 7',
        'Level 7 ': 'Level 7',
        'Level 7 (postgraduate)': 'Level 7',
        'Others': 'Other',
        'Other': 'Other'
    },
    'actual': {'Yes': 'Yes', 'No': 'No'},
    'gender': {
        'Male': 'Male',
        'Female': 'Female',
        'Other': 'Other',
        'prefer not to say': 'Prefer not to say',
        'Prefer not to say': 'Prefer not to say',
        'Non-binary / LGBTQ+': 'Other'
    }
}

country_mapping = {
    # UK variations
    'UK': 'United Kingdom',
    'Uk': 'United Kingdom',
    'uk': 'United Kingdom',
    'England': 'United Kingdom',
    'England ': 'United Kingdom',
    'Wales': 'United Kingdom',
    'United Kingdom ': 'United Kingdom',
    
    # US variations
    'us': 'United States',
    'America ': 'United States',
    
    # Asia
    'china': 'China',
    'China ': 'China',
    'sri lanka': 'Sri Lanka',
    'Sri lanka': 'Sri Lanka',
    'Viet Nam': 'Vietnam',
    'Korea, Republic of': 'South Korea',
    'Myanmar': 'Myanmar',
    'Philippines ': 'Philippines',
    
    # Europe
    'slovakia': 'Slovakia',
    'serbia': 'Serbia',
    'Russian Federation': 'Russia',
    'Moldova, Republic of': 'Moldova',
    
    # Middle East
    'Iran, Islamic Republic Of': 'Iran',
    'from Egypt, based in saudi': 'Saudi Arabia',
    'Yemen ': 'Yemen',
    
    # Africa
    'Tanzania, United Republic of': 'Tanzania',
    'nig': 'Nigeria',
    
    # Special territories
    'Hong Kong': 'Hong Kong SAR',
    'Falkland Islands (Malvinas)': 'Falkland Islands',
    'Bangladesh - born England': 'United Kingdom',
    
    # Clean spaces
    'India ': 'India',
    'Greece ': 'Greece'
}

value_mappings_min = {
    'stress_in_general': {
        'Yes (due to employment-related issues)': 'Yes',
        'Yes (due to other circumstances, such as health, family issues, etc)': 'Yes',
        'Yes (due to university work)': 'Yes',
        'No': 'No',
        'Yes': 'Yes',
        'Yes (due to other circumstances, such as health, family issues, etc),No': 'Yes',
        'Yes (due to other circumstances, such as health, family issues, etc), Yes (due to university work)': 'Yes',
        'Yes (due to employment-related issues), Yes (due to other circumstances, such as health, family issues, etc)': 'Yes',
        'Yes (due to employment-related issues),Yes (due to other circumstances, such as health, family issues, etc),Yes (due to university work)': 'Yes',
        'Yes (due to university work),No': 'Yes',
        'Yes (due to employment-related issues), Yes (due to university work)': 'Yes'
    },
    'stress_before_exams': {
        'Yes (due to university work)': 'Yes',
        'Yes (due to employment-related issues)': 'Yes',
        'Yes (due to other circumstances such as health, family issues, etc)': 'Yes',
        'Yes': 'Yes',
        'No': 'No',
        "I don't have exams": 'No',
        "I don't normally have exams": 'No',
        'No (I am not stressed)': 'No'
    },
    'timetable_impact': {
        'Yes': 'Yes',
        'No': 'No',
        'Not completed': 'No',
        'Yes, on my life, health and studies': 'Yes',
        'Yes, on my studies': 'Yes',
        'Yes, on my life and health': 'Yes',
        'No, it has no impact on my studies, life or health': 'No'
    },
    'level_of_study': {
        'Level 4': 'Level 4',
        'Level 4 ': 'Level 4',
        'Level 4 (first year, undergraduate)': 'Level 4',
        'Level 4 Foundation year': 'Level 4',
        'Foundation year': 'Level 4',
        'Level 5 (second year, undergraduate)': 'Level 5',
        'Level 6 (third year, undergraduate)': 'Level 6',
        'Level 7': 'Level 7',
        'Level 7 ': 'Level 7',
        'Level 7 (postgraduate)': 'Level 7',
        'Others': 'Other',
        'Other': 'Other'
    },
}