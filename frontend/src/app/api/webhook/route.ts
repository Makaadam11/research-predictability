import { NextRequest, NextResponse } from "next/server";

export const QltrixFormsTranslationMap: Record<string, string> = {
  "Are you a home student or an international student?": "student_type_location",
  "Are you full-time or part-time student?": "student_type_time",
  "Are you in any form of employment?": "form_of_employment",
  "Do you consider physical activity to be helpful to your mental health?": "physical_activities",
  'Do you feel a sense of "belonging" at UAL?': "sense_of_belonging",
  "Do you feel your timetabling structure has any impact on your study, life and health?": "timetable_impact",
  "Do you have any known disabilities?": "known_disabilities",
  "Do you normally encounter financial issues paying your fees?": "financial_problems",
  "Do you normally feel stressed before exams?": "stress_before_exams",
  "How many hours do you normally have BETWEEN lectures per day?": "hours_between_lectures",
  "How many hours do you spend on university/academic-related work, separate from your Course Timetable, per week during exams?": "hours_per_week_university_work",
  "How many hours do you spend using social media per day (Instagram, Tiktok, Twitter, etc)?": "hours_socialmedia",
  "How many hours per week do you have active lectures? (Active means attending lectures)": "hours_per_week_lectures",
  "How many hours per week do you socialise? (Meeting other people, participating in social activities etc).": "hours_socialising",
  "How many hours per week do you work?": "work_hours_per_week",
  "How often do you exercise per week?": "exercise_per_week",
  "How often in the last week or two did you feel afraid that something awful might happen?": "feel_afraid",
  "How would you classify your ethnic group?": "ethnic_group",
  "How would you define your alcohol consumption?": "alcohol_consumption",
  "How would you define your quality of life? (as defined by the World Health Organization)": "quality_of_life",
  "How would you describe your biological gender?": "gender",
  "How would you rate your family class? (family earnings per year)": "family_earning_class",
  "If your Course has less than 24 hours on Timetable, would you prefer your timetable to be spread (3-4 days with fewer lectures) or compact (1-2 busy days) so you have less stress at university? (eg, 1-2 busy days or 3-4 days with less lectures)": "timetable_preference",
  "In general, do you feel you experience stress while in the University/Academic Studies? (tick all that apply)": "stress_in_general",
  "Please let us know about any activities that could support your mental health that you would be interested in. (e.g., physical activities, sports, mindfulness, book clubs, arts/craft activities etc)": "mental_health_activities",
  "What Country are you from?": "home_country",
  "What are the approximate costs for your studies? (tuition fee per year of study, in pound sterling £)": "cost_of_study",
  "What are the reasons for your timetable preference?": "timetable_reasons",
  "What is your course of study?": "course_of_study",
  "What is your main financial support for your studies?": "financial_support",
  "What is your year of birth?": "age",
  "What year of study are you in?": "level_of_study",
  "Would you classify yourself or have you been diagnosed with mental health issues by a professional?": "actual",
  "Would you consider yourself an introvert or extrovert person? (Definitions from Oxford Languages)": "personality_type",
  "Would you describe your current diet as healthy and balanced?": "diet",
  "Would you say that you are normally well hydrated?": "well_hydrated",
};


export interface QualtricsData {
  university: string;
  answers: Record<string, unknown>[];
}

export type NormalizedSurvey = Partial<Record<(typeof QltrixFormsTranslationMap)[keyof typeof QltrixFormsTranslationMap], string | number | string[]>>;

export function translateWebhookPayload(body: Record<string, unknown>): NormalizedSurvey {
  const out: NormalizedSurvey = {};
  for (const [rawKey, value] of Object.entries(body)) {
    const key = rawKey?.trim?.();
    if (!key) continue;
    const mapped = QltrixFormsTranslationMap[key];
    if (!mapped) continue; // pomiń nieznane pytania
    out[mapped] = typeof value === "string" ? value.trim() : value as any;
  }
  return out;
}

export async function POST(request: NextRequest) {
  try {
    console.log("Processing webhook...");
    const body = await request.json();
    console.log("Webhook received:", body);

    const secret = request.headers.get("X-Webhook-Secret");
    const expectedSecret = process.env.WEBHOOK_SECRET;
    if (expectedSecret && secret !== expectedSecret) {
      return NextResponse.json({ error: "Invalid secret" }, { status: 401 });
    }
    const university = request.headers.get("X-University") || "unknown";
    const answers = body['answers'] as Record<string, unknown>[] || [];
    const translatedAnswers = answers.map(translateWebhookPayload);

    // Przetwarzanie danych
    console.log("Webhook received:", body);

    // Możesz tu przekazać dalej do backendu, zapisać do bazy itd.
    // await fetch("http://localhost:8000/api/submit/ual", { ... })

    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 400 });
  }
}