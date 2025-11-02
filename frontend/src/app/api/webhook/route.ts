import axios from "axios";
import { NextRequest, NextResponse } from "next/server";
import { QuestionarieData } from "@/types/QuestionaireTypes";

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export const QltrixFormsTranslationMap: Record<string, string> = {
  "Would you describe your current diet as healthy and balanced?": "diet",
  "How would you classify your ethnic group?": "ethnic_group",
  "How many hours do you spend on university/academic-related work, separate from your Course Timetable, per week during exams?": "hours_per_week_university_work",
  "How would you rate your family class? (family earnings per year)": "family_earning_class",
  "How would you define your quality of life? (as defined by the World Health Organization)": "quality_of_life",
  "How would you define your alcohol consumption?": "alcohol_consumption",
  "Would you consider yourself an introvert or extrovert person? (Definitions from Oxford Languages)": "personality_type",
  "In general, do you feel you experience stress while in the University/Academic Studies? (tick all that apply)": "stress_in_general",
  "Would you say that you are normally well hydrated?": "well_hydrated",
  "How often do you exercise per week?": "exercise_per_week",
  "Do you have any known disabilities?": "known_disabilities",
  "How many hours per week do you work?": "work_hours_per_week",
  "What is your main financial support for your studies?": "financial_support",
  "Are you in any form of employment?": "form_of_employment",
  "Do you normally encounter financial issues paying your fees?": "financial_problems",
  "What Country are you from?": "home_country",
  "What is your year of birth?": "age",
  "What is your course of study?": "course_of_study",
  "Do you normally feel stressed before exams?": "stress_before_exams",
  "How often in the last week or two did you feel afraid that something awful might happen?": "feel_afraid",
  "If your Course has less than 24 hours on Timetable, would you prefer your timetable to be spread (3-4 days with fewer lectures) or compact (1-2 busy days) so you have less stress at university? (eg, 1-2 busy days or 3-4 days with less lectures)": "timetable_preference",
  "What are the reasons for your timetable preference?": "timetable_reasons",
  "Do you feel your timetabling structure has any impact on your study, life and health?": "timetable_impact",
  "How many hours do you spend using technology devices per day (mobile, desktop, laptops, etc)?": "total_device_hours",
  "How many hours do you spend using social media per day (Instagram, Tiktok, Twitter, etc)?": "hours_socialmedia",
  "What year of study are you in?": "level_of_study",
  "How would you describe your biological gender?": "gender",
  "Do you consider physical activity to be helpful to your mental health?": "physical_activities",
  "How many hours do you normally have BETWEEN lectures per day?": "hours_between_lectures",
  "How many hours per week do you have active lectures? (Active means attending lectures)": "hours_per_week_lectures",
  "How many hours per week do you socialise? (Meeting other people, participating in social activities etc).": "hours_socialising",
  "Would you classify yourself or have you been diagnosed with mental health issues by a professional?": "actual",
  "Are you full-time or part-time student?": "student_type_time",
  "Are you a home student or an international student?": "student_type_location",
  "What are the approximate costs for your studies? (tuition fee per year of study, in pound sterling £)": "cost_of_study",
  'Do you feel a sense of "belonging" at UAL?': "sense_of_belonging",
  "Please let us know about any activities that could support your mental health that you would be interested in. (e.g., physical activities, sports, mindfulness, book clubs, arts/craft activities etc)": "mental_health_activities",
};

export function translateWebhookPayload(body: Record<string, unknown>): { id: string; answer: string | number | string[] }[] {
  const out: { id: string; answer: string | number | string[] }[] = [];
  console.log("Translating webhook payload:", body);

  for (const [question, id] of Object.entries(QltrixFormsTranslationMap)) {
    if (!Object.prototype.hasOwnProperty.call(body, question)) continue;

    const raw = (body as any)[question];

    if (id === "stress_in_general") {
      let arr: string[] = [];
      if (Array.isArray(raw)) {
        arr = raw
          .map((x) => (typeof x === "string" ? x.trim() : String(x)))
          .filter((x) => x.length > 0);
      } else if (typeof raw === "string") {
        const v = raw.trim();
        if (v) {
          arr = v.split(/[;,]/).map((s) => s.trim()).filter(Boolean);
        }
      }
      if (arr.length > 0) {
        out.push({ id, answer: arr });
      }
      continue;
    }

    out.push({ id, answer: raw as string | number | string[] });
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

    let translatedAnswers: { id: string; answer: string | number | string[] }[] = [];
    if (Array.isArray(body)) {
      translatedAnswers = body.map((b: Record<string, unknown>) => translateWebhookPayload(b)).flat();
    } else if (body && typeof body === "object") {
      translatedAnswers = translateWebhookPayload(body as Record<string, unknown>);
    } else {
      console.warn("Unsupported webhook body shape");
    }

    console.log("Translated answers:", translatedAnswers);

    const data: QuestionarieData = {
      answers: translatedAnswers,
      source: university
    };

    console.log("Sending data:", data);

    const response = await fetch(`${API_BASE_URL}/api/submit/${university}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    console.log("Webhook response:", response.status, await response.text());
    return NextResponse.json({ success: true });
  } catch (error: any) {
    const detail = error?.response?.data || error?.message;
    console.error("Webhook error:", detail);
    return NextResponse.json({ error: detail }, { status: 400 });
  }
}