import { NextRequest, NextResponse } from "next/server";

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

    // Przetwarzanie danych
    console.log("Webhook received:", body);

    // Możesz tu przekazać dalej do backendu, zapisać do bazy itd.
    // await fetch("http://localhost:8000/api/submit/ual", { ... })

    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 400 });
  }
}