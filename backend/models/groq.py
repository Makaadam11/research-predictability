import json
import os
from groq import Groq

class GroqClient:
    def __init__(self):
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY")
        )

    def get_prompt_template(self, df, stats) -> str:
        prompt1 = f"""
        Create a comprehensive mental health report with these sections:
        
        1. Executive Summary
        2. Demographic Analysis: {stats['demographics']}
        3. Academic Factors Analysis: {stats['academic']}
        4. Financial Analysis: {stats['financial']}
        5. Lifestyle Analysis: {stats['lifestyle']}
        6. Psychological and Social Analysis: {stats['psychological']}
        7. Percentages Summary
        8. Key Findings
        9. Recommendations
        
        For each category, analyze the data based on the prediction values (0 or 1) indicating mental health issues.
        
        Example format:
        
        BSc Computer Science (Analysis)
        
        Summary Metrics
        • Total Records for BSc Computer Science: 37
        • Predicted "Mental Health Proneness" (Predictions = 1): 7
        • Predicted "Not Prone to Mental Health" (Predictions = 0): 30
        
        Age Group Distribution:
        o 16–20 years: Majority of students (70%), with 90% classified as not prone (Prediction = 0). Only 10% classified as prone (Prediction = 1).
        o 21–25 years: 20% of students, all predominantly classified as not prone.
        o Evidence indicates that younger students face lower mental health proneness.
        
        Financial Support and Financial Problems:
        o Parent Support: 100% of students with parent support were classified as not prone (Prediction = 0).
        o Student Loans: Represents 65% of students, with 85% classified as not prone and 15% prone. Financial dependency plays a role in mental health stability.
        o Financial Problems: 80% of those facing financial problems (e.g., lower family income) were classified as prone to mental health issues (Prediction = 1).
        
        Stress Levels:
        o Stress before exams: 90% reported stress, but only 15% were prone (Prediction = 1).
        o Stress in general: 80% of students reported general stress, with a small correlation to being prone (20%).
        
        Employment Status:
        o Unemployed Students: 90% classified as not prone. Lack of work may reduce mental health risk.
        o Part-time/Full-time Jobs: 10% prone, possibly linked to time management and academic pressure.
        
        Diet and Exercise:
        o Students with healthy diets and regular exercise were predominantly not prone (95%).
        o Lack of hydration/alcohol consumption showed no strong correlation.
        
        Social Media and Device Use:
        o High social media use (15+ hours weekly): 40% prone to mental health issues.
        o Moderate use (8–15 hours weekly): 10% prone.
        o Low use (<8 hours weekly): No correlation observed with mental health proneness.
        
        Family Earning Class:
        o Lower Class: 60% prone.
        o Middle Class: 90% not prone.
        o Higher Class: 95% not prone. Economic stability correlates with mental health resilience.
        
        Gender Distribution:
        o Female students: 15% prone (Prediction = 1).
        o Male students: 5% prone.
        o Other genders (e.g., Non-binary): Higher proneness (40%), though sample size is small.
        
        Evidenced-Based Conclusion
        1. Age and Support Systems: Younger students (16–20 years) with adequate parental or financial support exhibit low mental health risks. Financial problems and lack of familial support significantly increase susceptibility.
        2. Stress and Workload: General and exam-related stress are not sole predictors of mental health issues. However, combining high stress with heavy workloads (employment) amplifies risks.
        3. Economic Class: Lower-income students face disproportionately higher mental health challenges, highlighting a critical area for intervention.
        4. Social Media Influence: Excessive use (15+ hours) correlates with increased mental health issues. Moderation appears to offer protection.
        5. Gender Differences: Females and non-binary individuals demonstrate higher vulnerability, suggesting gender-sensitive support mechanisms.
        
        Recommendations
        1. Enhance Financial Support: Universities should prioritize financial aid, especially for lower-income and international students. Emergency grants and mental health funding should be streamlined.
        2. Promote Balanced Lifestyles:
        a. Campaigns promoting healthy diets, hydration, and regular exercise should be instituted.
        b. Social media workshops to teach moderation and device-free time could mitigate digital stress.
        3. Targeted Mental Health Resources:
        a. Expand counseling and peer-support services, with a focus on gender-sensitive approaches.
        b. Provide tailored support for part-time workers balancing employment and studies.
        4. Monitor High-Risk Groups:
        a. Track stress levels and workload in younger cohorts, offering early intervention.
        b. Introduce mentorship programmes pairing upper-year students with first years for guidance.
        5. Data-Driven Initiatives:
        a. Conduct regular surveys and use predictive models to refine mental health strategies.
        b. Integrate mental health modules into the academic curriculum for greater awareness.
        
        Generally
        • Financial issues, stress, heavy social media usage, and limited physical activity are significant indicators of mental health proneness.
        • Strengthening coping mechanisms and offering financial and mental health support could mitigate risks.
        • Encouraging balanced lifestyles, reduced social media reliance, and physical activity can promote resilience.
        """

        prompt2 = f"""
        Create a comprehensive mental health report based on the following student data analysis.
        Format the report with clear sections and professional language.
        
        Dataset Overview:
        - Total Students: {len(df)}
        - Students with Mental Health Issues: {df[df['predictions'] == 1].shape[0]}
        - Students without Mental Health Issues: {df[df['predictions'] == 0].shape[0]}
        
        1. Executive Summary
        Provide a brief overview of key findings.
        
        2. Demographic Analysis
        {json.dumps(stats['demographics'], indent=2)}
        
        3. Academic Factors Analysis
        {json.dumps(stats['academic'], indent=2)}
        
        4. Financial Analysis
        {json.dumps(stats['financial'], indent=2)}
        
        5. Lifestyle and Behavioral Analysis
        {json.dumps(stats['lifestyle'], indent=2)}
        
        6. Psychological and Social Analysis
        {json.dumps(stats['psychological'], indent=2)}
        
        7. Key Findings
        Highlight the most significant correlations with mental health issues.
        
        8. Recommendations
        Provide actionable recommendations for universities and students.
        
        Please format the report professionally with clear headings and bullet points where appropriate.
        """
        return prompt2


    def generate_report_content(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional report writer specializing in mental health analysis. Format your response in clear sections with headers. Focus on analyzing the data based on the prediction values (0 or 1) indicating mental health issues."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.1-8b-instant"
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"Error generating report: {e}")
            return f"Error generating report: {str(e)}"