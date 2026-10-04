import { handleMessage } from "./message.js";

function isMessagePath(pathname) {
  return pathname === "/api/message" || pathname === "/api/message/";
}

const IMPACT_PATHS = new Set([
  "/impact",
  "/impact/",
  "/impact/index.html",
  "/impact.html",
]);

const SHOP_STOREFRONT = "https://shop.friendsofscenic30a.org/";

const SHOP_PATHS = new Set([
  "/shop",
  "/shop/",
  "/shop/index.html",
]);

const GET_INVOLVED_PATHS = new Set([
  "/get-involved",
  "/get-involved/",
  "/get-involved/index.html",
]);

function impactRedirect() {
  return new Response(null, {
    status: 301,
    headers: { Location: "/our-work/#past-accomplishments" },
  });
}

function shopRedirect() {
  return new Response(null, {
    status: 301,
    headers: { Location: SHOP_STOREFRONT },
  });
}

function getInvolvedRedirect() {
  return new Response(null, {
    status: 301,
    headers: { Location: "/membership/" },
  });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (isMessagePath(url.pathname)) {
      return handleMessage(request, env, ctx);
    }
    if (IMPACT_PATHS.has(url.pathname)) {
      return impactRedirect();
    }
    if (SHOP_PATHS.has(url.pathname)) {
      return shopRedirect();
    }
    if (GET_INVOLVED_PATHS.has(url.pathname)) {
      return getInvolvedRedirect();
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
