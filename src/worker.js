import { handleMessage } from "./message.js";

function isMessagePath(pathname) {
  return pathname === "/api/message" || pathname === "/api/message/";
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (isMessagePath(url.pathname)) {
      return handleMessage(request, env);
    }

    if (!env || !env.ASSETS || typeof env.ASSETS.fetch !== "function") {
      return new Response("Not found", {
        status: 404,
        headers: { "content-type": "text/plain; charset=utf-8" },
      });
    }

    return env.ASSETS.fetch(request);
  },
};
