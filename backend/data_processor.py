import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from data_evaluation import predict_new_data
from structs.other import questions
from structs.columns import all_columns

class DataProcessor:
    def __init__(self):
        self.base_path = Path("../data")

    def append_row_to_excel(self, excel_path, data_dict):
        Path(excel_path).parent.mkdir(parents=True, exist_ok=True)
        if os.path.exists(excel_path):
            # Read full file with first row as header
            df = pd.read_excel(excel_path, header=0)

            # Create new row
            new_row = {}
            for col in df.columns:
                col_id = df.iloc[0][col]  # Get column ID from second row

                # Find matching answer
                answer = next((item.get('answer', None)
                            for item in data_dict['answers']
                            if item['id'] == col_id), None)

                # Special handling
                if col_id == 'stress_in_general' and answer:
                    if any('Yes' in a for a in answer):
                        answer = [a for a in answer if a != 'No']
                    answer = ','.join(answer).replace('[', '').replace(']', '')
                elif col_id == 'age' and answer:
                    current_year = int(datetime.now().strftime('%Y'))
                    answer = current_year - int(answer)

                new_row[col] = answer

            # Add metadata
            new_row['Source'] = data_dict['source']
            new_row['Predictions'] = data_dict['predictions']
            new_row['Captured At'] = data_dict['captured_at']

            # Append row after headers
            new_row_df = pd.DataFrame([new_row])
            df = pd.concat([df.iloc[:1], new_row_df, df.iloc[1:]], ignore_index=True)

            # Save preserving both header rows
            df.to_excel(excel_path, index=False)

        else:
            # Create DataFrame with questions as headers
            df = pd.DataFrame(columns=questions)

            # Add column IDs as first row
            df.loc[0] = all_columns

            # Add new data row
            new_row = {}
            for q, col_id in zip(questions, all_columns):
                if col_id in ['source', 'predictions', 'captured_at']:
                    answer = data_dict.get(col_id)
                else:
                    answer = next((item.get('answer', None)
                                for item in data_dict['answers']
                                if item['id'] == col_id), None)
                new_row[q] = answer

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_excel(excel_path, index=False)

    def save_and_evaluate(self, data, university: str):
        try:
            # Convert model to dict
            data_dict = data.dict()

            # Add timestamp and source
            data_dict['source'] = university.upper()
            data_dict['predictions'] = 0
            data_dict['captured_at'] = datetime.now().strftime('%d.%m.%Y %H:%M')

            # Paths to Excel files
            university_excel_path = self.base_path / university.lower() / f"{university.lower()}_data" / f"{university.lower()}_data.xlsx"
            merged_excel_path = self.base_path / "merged" / "merged_data.xlsx"

            # Append row to both university-specific and merged Excel files
            self.append_row_to_excel(university_excel_path, data_dict)
            self.append_row_to_excel(merged_excel_path, data_dict)

            # Read merged data with dual headers for inference
            df_merged_raw = pd.read_excel(merged_excel_path, header=None)
            questions_row = df_merged_raw.iloc[0].copy()
            column_ids = df_merged_raw.iloc[1].copy()

            # Run ML inference on "Prefer not to say" records
            df_copy = pd.read_excel(merged_excel_path, header=[0, 1])
            df_evaluated = predict_new_data(df_copy)

            # Build output dataframe: data rows with question text headers
            df_data = df_merged_raw.iloc[2:].copy()
            df_data.columns = column_ids

            # Copy updated predictions from evaluated data
            df_data['predictions'] = df_evaluated['predictions'].values

            # Restore question text headers for saving
            df_data.columns = questions_row

            # Save university-specific files
            for source in df_data['Source'].unique():
                if pd.isna(source) or not str(source).strip():
                    continue
                source_str = str(source).strip().lower()
                source_path = self.base_path / source_str / f"{source_str}_data" / f"{source_str}_data.xlsx"
                source_df = df_data[df_data['Source'] == source].copy()

                # Insert column IDs as first row
                id_row = pd.DataFrame([column_ids.values], columns=source_df.columns)
                source_df = pd.concat([id_row, source_df], ignore_index=True)
                source_df.to_excel(str(source_path), index=False)

            # Save merged file with column IDs as first row
            id_row = pd.DataFrame([column_ids.values], columns=df_data.columns)
            df_data = pd.concat([id_row, df_data], ignore_index=True)
            df_data.to_excel(str(merged_excel_path), index=False)

            return True

        except Exception as e:
            print(f"Error saving to Excel: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    processor = DataProcessor()
    processor.process_data()
