import pandas as pd
from pathlib import Path
from structs.columns import value_mappings, stress_columns, numeric_columns, country_mapping, base_columns

class DataMerger:
    def __init__(self):
        self.base_path = Path("data")

    def read_datasets(self):
        try:
            ual1 = pd.read_excel(self.base_path / "UAL_1_Questionnaire_Data.xlsx")
            ual2 = pd.read_excel(self.base_path / "UAL2_Questionnaire_Data.xlsx")
            sol = pd.read_excel(self.base_path / "Sol_Questionnaire_Data.xlsx")
            final = pd.read_excel(self.base_path / "Final.xlsx")
        
            return ual1, ual2, sol, final
        except Exception as e:
            print(f"Error reading files: {e}")
            raise

    def clean_and_standardize_dataset(self, df):
        
        if 'timetable_reasons' in df.columns:
            df = df.drop('timetable_reasons', axis=1)
            
        # Clean special characters
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace('Â', '')
                df[col] = df[col].str.strip()
    
        for col in stress_columns:
            if col in df.columns:
                df[col] = df[col].apply(self.standardize_stress)
        
        # Apply value mappings
        for col, mapping in value_mappings.items():
            if col in df.columns:
                df[col] = df[col].map(mapping).fillna(df[col])
        
        # Handle numeric columns
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Special column handling
        if 'home_country' in df.columns:
            df['home_country'] = df['home_country'].apply(self.standardize_country)
        
        if 'course_of_study' in df.columns:
            df['course_of_study'] = df['course_of_study'].apply(self.standardize_course)
        
        return df
    
    def standardize_numeric(self, value):
        """Extract numeric value from string and convert to int"""
        if pd.isna(value):
            return 0
        if isinstance(value, (int, float)):
            return int(value)
        # Extract numbers from string
        import re
        numbers = re.findall(r'\d+', str(value))
        return int(numbers[0]) if numbers else 0

    def merge_datasets(self):
        """Merge and standardize all datasets"""
        ual1, ual2, sol, final = self.read_datasets()
        
        # Standardize each dataset
        
        # Add source column
        ual1['source'] = 'UAL1'
        ual2['source'] = 'UAL2'
        sol['source'] = 'SOL'
        final['source'] = 'Final'
        
        # Merge datasets
        merged_df = pd.concat([ual1, ual2, sol, final], ignore_index=True)
        
        # Clean and standardize merged dataset
        merged_df = self.clean_and_standardize_dataset(merged_df)
        
        # Save merged dataset
        merged_df.to_excel(self.base_path / "merged_dataset_cleaned_vx.xlsx", index=False)
        print(f"Merged dataset saved with {len(merged_df)} rows")
        
        return merged_df
    
    def compare_columns(self):
        merged = pd.read_excel(self.base_path / "evaluated_dataset.xlsx")
        comparison_results = {}
        
        for col in base_columns:
            comparison_results[col] = {
                'Merged': set(merged[col].dropna().unique()) if col in merged.columns else set(),
            }
        
        return comparison_results

    def save_comparison_results(self, comparison_results):
        output_path = self.base_path / "comparison_results_evaluated.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            for col, datasets in comparison_results.items():
                f.write(f"Column: {col}\n")
                for dataset, values in datasets.items():
                    f.write(f"  {dataset}: {values}\n")
                f.write("\n")
        print(f"Comparison results saved to {output_path}")
        
    def standardize_country(self, country):
        if pd.isna(country):
            return 'Unknown'
        
        country = str(country).strip()
        return country_mapping.get(country, country.title())
    
    def standardize_course(self, course):
        if pd.isna(course):
            return 'Other'
            
        course = str(course).upper().strip()
        
        # Handle Foundation Years
        if 'FOUNDATION' in course:
            return 'Foundation'
            
        # Handle specific degree types
        if 'BSC' in course or 'BACHELOR OF SCIENCE' in course:
            return 'BSc'
        elif 'BA' in course or 'BACHELOR OF ARTS' in course:
            return 'BA'
        elif 'MSC' in course or 'MASTER OF SCIENCE' in course:
            return 'MSc'
        elif 'MA ' in course or 'MASTER OF ARTS' in course:
            return 'MA'
        elif 'BENG' in course or 'BACHELOR OF ENGINEERING' in course:
            return 'BEng'
        elif 'FDSC' in course:
            return 'FdSc'
        elif 'MBA' in course:
            return 'MBA'
        elif 'MRES' in course:
            return 'MRes'
        elif 'HNC' in course or 'HND' in course:
            return 'HNC/HND'
        elif 'LLB' in course:
            return 'LLB'
        elif 'BMUS' in course:
            return 'BMus'
        elif 'APPRENTICESHIP' in course:
            return 'Apprenticeship'
        elif any(x in course for x in ['STUDY ABROAD', 'EXCHANGES']):
            return 'Exchange'
            
        return 'Other'

    def standardize_stress(self, value):
        if pd.isna(value) or value == 'nan':
            return 'No'
        value = str(value).lower()
        
        if any(x in value for x in ['yes', 'stressed']):
            return 'Yes'
        if any(x in value for x in ["don't have exams", "don't normally have exams", 'no', 'not stressed']):
            return 'No'
        return 'No'

if __name__ == "__main__":
    standardizer = DataMerger()
    # merged_data = standardizer.merge_datasets()
    standardizer.save_comparison_results(standardizer.compare_columns())
