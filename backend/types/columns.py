all_columns = [
    'diet', 'ethnic_group', 'hours_per_week_university_work', 'family_earning_class',
    'quality_of_life', 'alcohol_consumption', 'personality_type', 'stress_in_general',
    'well_hydrated', 'exercise_per_week', 'known_disabilities', 'work_hours_per_week',
    'financial_support', 'form_of_employment', 'financial_problems', 'home_country',
    'age', 'course_of_study', 'stress_before_exams', 'feel_afraid',
    'timetable_preference', 'timetable_reasons', 'timetable_impact', 'total_device_hours',
    'hours_socialmedia', 'level_of_study', 'gender', 'physical_activities',
    'hours_between_lectures', 'hours_per_week_lectures', 'hours_socialising', 'actual',
    'student_type_time', 'student_type_location', 'cost_of_study', 'sense_of_belonging',
    'mental_health_activities', 'source', 'predictions', 'captured_at'
]

base_columns = [
    'diet', 'ethnic_group', 'hours_per_week_university_work', 'family_earning_class', 
    'quality_of_life', 'alcohol_consumption', 'personality_type', 'stress_in_general', 
    'well_hydrated', 'exercise_per_week', 'known_disabilities', 'work_hours_per_week', 
    'financial_support', 'form_of_employment', 'financial_problems', 'home_country', 
    'age', 'course_of_study', 'stress_before_exams', 'feel_afraid', 'timetable_preference', 
    'timetable_reasons', 'timetable_impact', 'total_device_hours', 'hours_socialmedia', 
    'level_of_study', 'gender', 'physical_activities', 'hours_between_lectures', 
    'hours_per_week_lectures', 'hours_socialising', 'actual', 'student_type_time', 
    'student_type_location', 'cost_of_study', 'sense_of_belonging', 'mental_health_activities'
]

categorical_columns = [
    'home_country', 'ethnic_group', 'course_of_study', 'financial_support', 
    'financial_problems', 'family_earning_class', 'stress_before_exams', 
    'stress_in_general', 'form_of_employment', 'quality_of_life', 'known_disabilities',
    'alcohol_consumption', 'well_hydrated', 'diet', 'personality_type', 
    'feel_afraid', 'timetable_preference', 'timetable_reasons', 'timetable_impact', 
    'gender', 'student_type_location', 'student_type_time', 'level_of_study', 
    'physical_activities', 'mental_health_activities', 'sense_of_belonging'
]

numeric_columns = [
    'age', 'hours_per_week_university_work', 'work_hours_per_week', 
    'hours_socialising', 'hours_socialmedia', 'total_device_hours', 
    'cost_of_study', 'hours_per_week_lectures', 'hours_between_lectures', 
    'exercise_per_week'
]

demographic_cols = [
            'home_country', 'ethnic_group', 'age', 'gender', 
            'family_earning_class', 'student_type_location'
]

academic_cols = [
    'course_of_study', 'level_of_study', 'cost_of_study', 
    'hours_per_week_lectures', 'hours_between_lectures'
]

financial_cols = [
    'financial_support', 'financial_problems'
]

lifestyle_cols = [
    'stress_before_exams', 'stress_in_general', 'work_hours_per_week', 
    'hours_socialising', 'hours_socialmedia', 'total_device_hours', 
    'diet', 'well_hydrated', 'alcohol_consumption', 'quality_of_life'
]

psychological_cols = [
    'personality_type', 'exercise_per_week', 'feel_afraid', 'known_disabilities'
]

stress_columns = [
    'stress_in_general', 'stress_before_exams'
]
