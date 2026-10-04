const FROM = "Friends of Scenic 30A <onboarding@resend.dev>";
const WINDOW_MS = 60 * 1000;
const MAX_PER_WINDOW = 5;
const recentHits = new Map();
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const FORM_KINDS = new Set(["contact", "membership", "volunteer", "updates"]);

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

function clientIp(request) {
  return request.headers.get("cf-connecting-ip") || "unknown";
}

function rateLimited(ip) {
  const now = Date.now();
  const stamps = (recentHits.get(ip) || []).filter((time) => now - time < WINDOW_MS);
  if (stamps.length >= MAX_PER_WINDOW) {
    recentHits.set(ip, stamps);
    return true;
  }
  stamps.push(now);
  recentHits.set(ip, stamps);
  if (recentHits.size > 1000) {
    for (const [key, times] of recentHits) {
      const fresh = times.filter((time) => now - time < WINDOW_MS);
      if (fresh.length) recentHits.set(key, fresh);
      else recentHits.delete(key);
    }
  }
  return false;
}

function validEmail(value) {
  const email = textValue(value);
  if (!email || email.length > 254 || !EMAIL_RE.test(email)) return "";
  return email;
}

function formKind(value) {
  const kind = textValue(value).replace(/[\r\n\t]+/g, " ").replace(/\s+/g, " ").trim();
  return FORM_KINDS.has(kind) ? kind : "message";
}

function checkedLine(data) {
  if (!Object.prototype.hasOwnProperty.call(data, "requests")) return "";
  const checked = textValue(data.requests).replace(/[\r\n\t]+/g, " ").replace(/\s+/g, " ").trim();
  return `Checked: ${checked || "none"}`;
}

function sheetKind(kind) {
  return kind === "membership" ? "membership" : "contact";
}

function checkedLabels(value) {
  const items = Array.isArray(value) ? value : textValue(value) ? [value] : [];
  return new Set(items.map((item) => textValue(item).toLowerCase()));
}

function marked(labels, label) {
  return labels.has(label) ? "Yes" : "";
}

function sheetRow(data, kind, email, name) {
  const rowKind = sheetKind(kind);
  const row = {
    kind: rowKind,
    name,
    email,
    phone: textValue(data.phone),
    message: textValue(data.message),
  };
  if (rowKind === "membership") {
    row.address = textValue(data.address);
    row.city = textValue(data.city);
    row.state = textValue(data.state);
    row.zip = textValue(data.zip);
    row.membership = textValue(data.membership);
    return row;
  }
  const labels = checkedLabels(data.requests);
  row.contact = marked(labels, "contact friends");
  row.volunteer = marked(labels, "volunteer");
  row.updates = marked(labels, "get updates");
  return row;
}

async function recordSheet(env, row) {
  const url = env && String(env.GOOGLE_SHEETS_WEBHOOK_URL || "").trim();
  const token = env && String(env.GOOGLE_SHEETS_WEBHOOK_TOKEN || "").trim();
  if (!url || !token) return;
  try {
    await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ token, ...row }),
    });
  } catch {
    // The email already went out. A sheet miss must not change that result.
  }
}

export async function handleMessage(request, env, ctx) {
  if (request.method !== "POST") {
    return json({ error: "Method not allowed" }, 405);
  }

  if (rateLimited(clientIp(request))) {
    return json({ error: "Please wait a minute and try again." }, 429);
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

  const kind = formKind(data.kind);
  const email = validEmail(data.email);
  const name = [textValue(data.first), textValue(data.last)].filter(Boolean).join(" ");
  if (!email) {
    return json({ error: "Enter an email address." }, 400);
  }

  if (!env.CONTACT_EMAIL || !env.RESEND_API_KEY) {
    return json({
      error: "Message delivery is not configured yet. Please write Friends of Scenic 30A, 877 N County Hwy 393, Santa Rosa Beach, FL 32459.",
    }, 503);
  }

  const lines = [
    `Form: ${kind}`,
    checkedLine(data),
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

  const sheetWrite = recordSheet(env, sheetRow(data, kind, email, name));
  if (ctx && typeof ctx.waitUntil === "function") ctx.waitUntil(sheetWrite);
  else await sheetWrite;

  return json({ ok: true }, 200);
}
