import assert from "node:assert/strict";
import { handleMessage } from "../src/message.js";

function post(body) {
  return new Request("https://example.com/api/message", {
    method: "POST",
    headers: { "content-type": "application/json" },
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

const honeypot = await handleMessage(post({
  kind: "contact",
  email: "neighbor@example.com",
  company: "not-a-person",
}), {});
assert.equal(honeypot.status, 200);

console.log("message handler ok");
