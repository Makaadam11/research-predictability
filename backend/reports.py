import base64
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from io import BytesIO
from pathlib import Path
from PIL import Image
from models.groq import GroqClient
from structs.columns import base_columns, categorical_columns, numeric_columns, demographic_cols, academic_cols, financial_cols, lifestyle_cols, psychological_cols

matplotlib.use('Agg')

def clean_numeric_values(value):
    try:
        if isinstance(value, str):
            value = value.replace(',', '')
        return float(value)
    except (ValueError, TypeError):
        return np.nan
    
# TODO: Add source and consider actual
def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cols = base_columns.copy()
    cols.append('predictions')
    # cols.remove('actual')
    # cols.append('source')

    df = df[cols].copy()
    
    for col in numeric_columns:
        df[col] = df[col].apply(clean_numeric_values)
    
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
    
    for col in categorical_columns:
        df[col] = df[col].astype('category')
    
    return df

class Reports:
    def __init__(self):
        self.llm: GroqClient = GroqClient()
        self.output_dir = Path("tmp_report_assets")
        self.output_dir.mkdir(exist_ok=True)
        self.pdf = FPDF()
        
        # Add Unicode font
        font_path = Path("fonts/DejaVuLGCSans.ttf")
        self.pdf.add_font('DejaVuLGCSans', '', str(font_path), uni=True)
        
        font_path = Path("fonts/DejaVuLGCSans-Bold.ttf")
        self.pdf.add_font('DejaVuLGCSans-Bold', '', str(font_path), uni=True)
        self.pdf.set_font('DejaVuLGCSans', '', 12)
        
    def get_category_statistics(self, df, category_cols):
        stats = {}
        for col in category_cols:
            if col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    stats[col] = {
                        'mean': df[col].mean(),
                        'median': df[col].median(),
                        'std': df[col].std()
                    }
                else:
                    stats[col] = df[col].value_counts().to_dict()
        return stats

    def add_image_with_text(self, image_data, text):
        print(f"Adding image with text: {text}")
        image_data_base64 = image_data.split(",")[1]  # Correctly split the image data
        image = Image.open(BytesIO(base64.b64decode(image_data_base64)))
        image_path = self.output_dir / f"{text}.png"
        image.save(image_path)

        # Calculate the appropriate width and height while maintaining aspect ratio
        max_width = 190
        max_height = 150
        width, height = image.size
        aspect_ratio = width / height

        if height > max_height:
            height = max_height
            width = height * aspect_ratio

        if width > max_width:
            width = max_width
            height = width / aspect_ratio

        self.pdf.image(str(image_path), x=10, y=10, w=width, h=height)
        self.pdf.set_xy(10, 10 + height + 10)  # Adjust the position for the text
        self.pdf.set_font('DejaVuLGCSans', '', 12)
        self.pdf.multi_cell(190, 9)
        print(f"Image with text added: {text}")
    
    def remove_tmp_dir(self):
        for img_file in self.output_dir.glob("*.png"):
            img_file.unlink()
        self.output_dir.rmdir()

    def generate_report_pdf(self, df: pd.DataFrame, output_path: str, chart_images: dict = None):
        
        df: pd.DataFrame = preprocess_dataframe(df)

        self.pdf.add_page()
        self.pdf.set_font('DejaVuLGCSans-Bold', '', 16)

        stats = {
            'demographics': self.get_category_statistics(df, demographic_cols),
            'academic': self.get_category_statistics(df, academic_cols),
            'financial': self.get_category_statistics(df, financial_cols),
            'lifestyle': self.get_category_statistics(df, lifestyle_cols),
            'psychological': self.get_category_statistics(df, psychological_cols)
        }

        prompt = self.llm.get_prompt_template(df, stats)

        report_content = self.llm.generate_report_content(prompt)
        
        self.pdf.cell(200, 10, "Student Mental Health Analysis", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.pdf.ln(10)
        self.pdf.set_font('DejaVuLGCSans', '', 12)

        # For images
        # self.pdf.multi_cell(0, 10, report_content)
        
        paragraphs = report_content.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                if paragraph.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
                    self.pdf.set_font('DejaVuLGCSans-Bold', '', 14)
                    self.pdf.multi_cell(0, 10, paragraph.strip())
                    self.pdf.ln(2)
                    self.pdf.set_font('DejaVuLGCSans', '', 12)
                else:
                    self.pdf.multi_cell(0, 10, paragraph.strip())
                    self.pdf.ln(2)

        if chart_images:
            for title, image in chart_images.items():
                if isinstance(image, str) and image.startswith("data:image/png;base64,"):
                    chart_title = title if title != "[object HTMLDivElement]" else "Chart"
                    self.pdf.add_page()
                    self.add_image_with_text(image, f"Analysis for {chart_title.replace('_', ' ').title()}")

        self.pdf.output(output_path)
        self.remove_tmp_dir()
        print(f"PDF report generated successfully at: {output_path}")