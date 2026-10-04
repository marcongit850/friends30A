import assert from "node:assert/strict";
import { handleMessage } from "../src/message.js";

let nextIp = 1;

function post(body, ip) {
  const host = ip || `203.0.113.${nextIp++}`;
  return new Request("https://example.com/api/message", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "cf-connecting-ip": host,
    },
    body: JSON.stringify(body),
  });
}

const missingEmail = await handleMessage(post({ kind: "contact", message: "Hello" }), {});
assert.equal(missingEmail.status, 400);

const unconfigured = await handleMessage(post({
  kind: "contact",
  email: "neighbor@example.com",
  first: "Ada",
  message: "Hello from 30A",
}), {});
assert.equal(unconfigured.status, 503);
const payload = await unconfigured.json();
assert.match(payload.error, /877 N County Hwy 393/);

const trimmed = await handleMessage(post({
  kind: "membership",
  email: "  neighbor@example.com  ",
  first: "Ada",
  last: "Lovelace",
  message: "Membership details",
}), {});
assert.equal(trimmed.status, 503);

for (const email of ["not-an-email", "neighbor@", "neighbor@example", "a@b", "Ada <neighbor@example.com>"]) {
  const rejected = await handleMessage(post({ kind: "contact", email, message: "Hello" }), {});
  assert.equal(rejected.status, 400, email);
}

const honeypot = await handleMessage(post({
  kind: "contact",
  email: "neighbor@example.com",
  company: "not-a-person",
}), {});
assert.equal(honeypot.status, 200);

const realFetch = globalThis.fetch;
const sent = [];
globalThis.fetch = async (url, init) => {
  sent.push({ url, init });
  return new Response(JSON.stringify({ id: "email_123" }), {
    status: 200,
    headers: { "content-type": "application/json" },
  });
};

const env = { CONTACT_EMAIL: "inbox@example.com", RESEND_API_KEY: "re_test_secret" };

try {
  for (const kind of ["contact", "membership", "volunteer", "updates"]) {
    sent.length = 0;
    const response = await handleMessage(post({
      kind,
      email: "neighbor@example.com",
      first: "Ada",
      last: "Lovelace",
      phone: "(850) 555-0100",
      message: "Hello from 30A",
      interests: kind === "volunteer" ? ["Trails", "Events"] : "",
    }, `198.51.100.${kind.length}`), env);
    assert.equal(response.status, 200, kind);
    const mail = JSON.parse(sent[0].init.body);
    assert.equal(mail.subject, `Friends of Scenic 30A — ${kind}`);
    assert.equal(mail.reply_to, "neighbor@example.com");
    assert.match(mail.text, new RegExp(`Form: ${kind}`));
    assert.equal(mail.text.includes("Checked:"), false);
    if (kind === "volunteer") assert.match(mail.text, /Interests: Trails, Events/);
  }

  sent.length = 0;
  const checked = await handleMessage(post({
    kind: "contact",
    email: "neighbor@example.com",
    first: "Ada",
    last: "Lovelace",
    message: "Hello from 30A",
    requests: ["Contact Friends", "Get updates"],
  }, "198.51.100.30"), env);
  assert.equal(checked.status, 200);
  const checkedMail = JSON.parse(sent[0].init.body);
  assert.match(checkedMail.text, /Checked: Contact Friends, Get updates/);
  assert.equal(checkedMail.subject, "Friends of Scenic 30A — contact");

  sent.length = 0;
  const noneChecked = await handleMessage(post({
    kind: "contact",
    email: "neighbor@example.com",
    message: "Hello",
    requests: [],
  }, "198.51.100.31"), env);
  assert.equal(noneChecked.status, 200);
  const noneMail = JSON.parse(sent[0].init.body);
  assert.match(noneMail.text, /Checked: none/);

  sent.length = 0;
  const oneChecked = await handleMessage(post({
    kind: "contact",
    email: "neighbor@example.com",
    requests: "Volunteer",
  }, "198.51.100.32"), env);
  assert.equal(oneChecked.status, 200);
  const oneMail = JSON.parse(sent[0].init.body);
  assert.match(oneMail.text, /Checked: Volunteer/);

  sent.length = 0;
  const injected = await handleMessage(post({
    kind: "contact\r\nBcc: evil@example.com",
    email: "neighbor@example.com",
    message: "Hello",
  }, "198.51.100.20"), env);
  assert.equal(injected.status, 200);
  const injectedMail = JSON.parse(sent[0].init.body);
  assert.equal(injectedMail.subject, "Friends of Scenic 30A — message");
  assert.equal(injectedMail.subject.includes("Bcc"), false);
  assert.equal(injectedMail.text.includes("Bcc"), false);

  sent.length = 0;
  const overwritten = await handleMessage(post({
    kind: ["contact", "not-a-form"],
    email: "neighbor@example.com",
    message: "Hello",
  }, "198.51.100.21"), env);
  assert.equal(overwritten.status, 200);
  const overwrittenMail = JSON.parse(sent[0].init.body);
  assert.equal(overwrittenMail.subject, "Friends of Scenic 30A — message");

  const sheetUrl = "https://sheets.example.test/exec";
  const sheetEnv = {
    ...env,
    GOOGLE_SHEETS_WEBHOOK_URL: sheetUrl,
    GOOGLE_SHEETS_WEBHOOK_TOKEN: "sheet-token",
  };

  function installFetch(sheetResponse) {
    globalThis.fetch = async (url, init) => {
      sent.push({ url, init });
      if (url === "https://api.resend.com/emails") {
        return new Response(JSON.stringify({ id: "email_123" }), {
          status: 200,
          headers: { "content-type": "application/json" },
        });
      }
      return sheetResponse(url, init);
    };
  }

  installFetch(() => new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: { "content-type": "application/json" },
  }));

  sent.length = 0;
  const contactSheet = await handleMessage(post({
    kind: "contact",
    email: "neighbor@example.com",
    first: "Ada",
    last: "Lovelace",
    phone: "(850) 555-0100",
    message: "Hello from 30A",
    requests: ["Volunteer", "Get updates"],
  }, "198.51.100.40"), sheetEnv);
  assert.equal(contactSheet.status, 200);
  assert.equal(sent[0].url, "https://api.resend.com/emails");
  assert.equal(sent[1].url, sheetUrl);
  assert.equal(sent[1].init.method, "POST");
  assert.equal(sent[1].init.headers["content-type"], "application/json");
  const contactRow = JSON.parse(sent[1].init.body);
  assert.equal(contactRow.token, "sheet-token");
  assert.equal(contactRow.kind, "contact");
  assert.equal(contactRow.name, "Ada Lovelace");
  assert.equal(contactRow.email, "neighbor@example.com");
  assert.equal(contactRow.phone, "(850) 555-0100");
  assert.equal(contactRow.message, "Hello from 30A");
  assert.equal(contactRow.contact, "");
  assert.equal(contactRow.volunteer, "Yes");
  assert.equal(contactRow.updates, "Yes");
  assert.equal(Object.prototype.hasOwnProperty.call(contactRow, "address"), false);
  assert.equal(JSON.parse(sent[0].init.body).text.includes("sheet-token"), false);

  sent.length = 0;
  const memberSheet = await handleMessage(post({
    kind: "membership",
    email: "neighbor@example.com",
    first: "Ada",
    last: "Lovelace",
    phone: "(850) 555-0101",
    address: "877 N County Hwy 393",
    city: "Santa Rosa Beach",
    state: "FL",
    zip: "32459",
    membership: "Individual Membership – $25/year",
    message: "Paid on Square",
    requests: ["Volunteer"],
  }, "198.51.100.41"), sheetEnv);
  assert.equal(memberSheet.status, 200);
  const memberRow = JSON.parse(sent[1].init.body);
  assert.equal(memberRow.kind, "membership");
  assert.equal(memberRow.address, "877 N County Hwy 393");
  assert.equal(memberRow.city, "Santa Rosa Beach");
  assert.equal(memberRow.state, "FL");
  assert.equal(memberRow.zip, "32459");
  assert.equal(memberRow.membership, "Individual Membership – $25/year");
  assert.equal(Object.prototype.hasOwnProperty.call(memberRow, "volunteer"), false);

  installFetch(() => new Response("no", { status: 500 }));
  sent.length = 0;
  const sheetDown = await handleMessage(post({
    kind: "contact",
    email: "neighbor@example.com",
    message: "Hello",
    requests: ["Contact Friends"],
  }, "198.51.100.42"), sheetEnv);
  assert.equal(sheetDown.status, 200);
  assert.equal(sent[0].url, "https://api.resend.com/emails");
  assert.equal(sent[1].url, sheetUrl);
  const friendsRow = JSON.parse(sent[1].init.body);
  assert.equal(friendsRow.kind, "contact");
  assert.equal(friendsRow.contact, "Yes");
  assert.equal(friendsRow.volunteer, "");
  assert.equal(friendsRow.updates, "");
  const sheetDownBody = await sheetDown.json();
  assert.equal(sheetDownBody.ok, true);

  installFetch(() => {
    throw new Error("sheet down");
  });
  sent.length = 0;
  const sheetThrew = await handleMessage(post({
    kind: "contact",
    email: "neighbor@example.com",
    message: "Hello",
    requests: ["Contact Friends"],
  }, "198.51.100.43"), sheetEnv);
  assert.equal(sheetThrew.status, 200);
  assert.equal(sent[0].url, "https://api.resend.com/emails");
  const threwBody = await sheetThrew.json();
  assert.equal(threwBody.ok, true);

  globalThis.fetch = async (url, init) => {
    sent.push({ url, init });
    if (url === sheetUrl) return new Response("no", { status: 500 });
    return new Response("no", { status: 502 });
  };
  sent.length = 0;
  const mailFailed = await handleMessage(post({
    kind: "contact",
    email: "neighbor@example.com",
    message: "Hello",
  }, "198.51.100.44"), sheetEnv);
  assert.equal(mailFailed.status, 502);
  assert.equal(sent.length, 1);
  assert.equal(sent[0].url, "https://api.resend.com/emails");

  installFetch(() => new Response(JSON.stringify({ ok: true }), { status: 200 }));
  sent.length = 0;
  const missingToken = await handleMessage(post({
    kind: "contact",
    email: "neighbor@example.com",
    message: "Hello",
  }, "198.51.100.45"), {
    ...env,
    GOOGLE_SHEETS_WEBHOOK_URL: sheetUrl,
  });
  assert.equal(missingToken.status, 200);
  assert.equal(sent.length, 1);
  assert.equal(sent[0].url, "https://api.resend.com/emails");

  let releaseSheet = () => {};
  const sheetGate = new Promise((resolve) => {
    releaseSheet = resolve;
  });
  globalThis.fetch = async (url, init) => {
    sent.push({ url, init });
    if (url === sheetUrl) await sheetGate;
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  };
  sent.length = 0;
  let waited = null;
  try {
    const quick = await Promise.race([
      handleMessage(post({
        kind: "contact",
        email: "neighbor@example.com",
        message: "Hello",
        requests: ["Volunteer"],
      }, "198.51.100.46"), sheetEnv, {
        waitUntil(promise) { waited = promise; },
      }),
      new Promise((_, reject) => {
        setTimeout(() => reject(new Error("sheet delayed the form response")), 300);
      }),
    ]);
    assert.equal(quick.status, 200);
    assert.equal(sent[0].url, "https://api.resend.com/emails");
    assert.ok(waited);
    assert.equal(JSON.parse(sent[1].init.body).kind, "contact");
    assert.equal(JSON.parse(sent[1].init.body).volunteer, "Yes");
  } finally {
    releaseSheet();
  }
  if (waited) await waited;
} finally {
  globalThis.fetch = realFetch;
}

const limitedIp = "203.0.113.250";
for (let i = 0; i < 5; i += 1) {
  const allowed = await handleMessage(post({
    kind: "contact",
    email: "neighbor@example.com",
    message: "Hello",
  }, limitedIp), {});
  assert.equal(allowed.status, 503, `attempt ${i + 1}`);
}
const blocked = await handleMessage(post({
  kind: "contact",
  email: "neighbor@example.com",
  message: "Hello",
}, limitedIp), {});
assert.equal(blocked.status, 429);
const blockedBody = await blocked.json();
assert.match(blockedBody.error, /wait a minute/i);

const otherIp = await handleMessage(post({
  kind: "updates",
  email: "neighbor@example.com",
  message: "Keep me posted",
}, "203.0.113.251"), {});
assert.equal(otherIp.status, 503);

console.log("message handler ok");
