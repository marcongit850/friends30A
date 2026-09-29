const FROM = "Friends of Scenic 30A <onboarding@resend.dev>";

function json(body, status) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function textValue(value) {
  if (Array.isArray(value)) return value.map(textValue).filter(Boolean).join(", ");
  return String(value || "").trim();
}

export async function handleMessage(request, env) {
  if (request.method !== "POST") {
    return json({ error: "Method not allowed" }, 405);
  }

  let data;
  try {
    data = await request.json();
  } catch {
    return json({ error: "Send a JSON message." }, 400);
  }

  if (textValue(data.company)) {
    return json({ ok: true }, 200);
  }

  const kind = textValue(data.kind) || "message";
  const email = textValue(data.email);
  const name = [textValue(data.first), textValue(data.last)].filter(Boolean).join(" ");
  if (!email || !email.includes("@")) {
    return json({ error: "Enter an email address." }, 400);
  }

  if (!env.CONTACT_EMAIL || !env.RESEND_API_KEY) {
    return json({
      error: "Message delivery is not configured yet. Please write Friends of Scenic 30A, 877 N County Hwy 393, Santa Rosa Beach, FL 32459.",
    }, 503);
  }

  const lines = [
    `Form: ${kind}`,
    name ? `Name: ${name}` : "",
    `Email: ${email}`,
    textValue(data.phone) ? `Phone: ${textValue(data.phone)}` : "",
    textValue(data.address) ? `Address: ${textValue(data.address)}` : "",
    textValue(data.city) ? `City: ${textValue(data.city)}` : "",
    textValue(data.state) ? `State: ${textValue(data.state)}` : "",
    textValue(data.zip) ? `ZIP: ${textValue(data.zip)}` : "",
    textValue(data.membership) ? `Membership: ${textValue(data.membership)}` : "",
    textValue(data.interests) ? `Interests: ${textValue(data.interests)}` : "",
    "",
    textValue(data.message),
  ].filter((line) => line !== "");

  const response = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      authorization: `Bearer ${env.RESEND_API_KEY}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      from: FROM,
      to: [env.CONTACT_EMAIL],
      reply_to: email,
      subject: `Friends of Scenic 30A — ${kind}`,
      text: lines.join("\n"),
    }),
  });

  if (!response.ok) {
    return json({ error: "The message could not be delivered. Please try again later." }, 502);
  }

  return json({ ok: true }, 200);
}
