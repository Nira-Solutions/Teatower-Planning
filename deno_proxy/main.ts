// Teatower orders proxy — forwards validated form submissions into the private
// Teatower-Orders-Inbox repo via the GitHub Contents API.
//
// Deploy on deno.com/deploy (free tier, GitHub login, no CB).
// Env vars required in Deno Deploy:
//   GITHUB_PAT        fine-grained PAT, scope: Contents:Write on Teatower-Orders-Inbox only
//   SHARED_SECRET     same value baked into commande.html, anti-abuse check
//   INBOX_REPO        e.g. "Nira-Solutions/Teatower-Orders-Inbox"
//
// The frontend POSTs JSON: { secret, order: {...}, source_file: { name, content_b64 } | null }

const GITHUB_PAT = Deno.env.get("GITHUB_PAT")!;
const SHARED_SECRET = Deno.env.get("SHARED_SECRET")!;
const INBOX_REPO = Deno.env.get("INBOX_REPO")!;
const GH_API = "https://api.github.com";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...CORS },
  });
}

async function putFile(path: string, contentB64: string, message: string) {
  const url = `${GH_API}/repos/${INBOX_REPO}/contents/${path}`;
  const res = await fetch(url, {
    method: "PUT",
    headers: {
      "Authorization": `Bearer ${GITHUB_PAT}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, content: contentB64 }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`GitHub API ${res.status}: ${err}`);
  }
  return await res.json();
}

function b64(str: string): string {
  return btoa(unescape(encodeURIComponent(str)));
}

function safeSlug(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "cmd";
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
  if (req.method !== "POST") return json(405, { error: "POST only" });

  let payload;
  try {
    payload = await req.json();
  } catch {
    return json(400, { error: "Invalid JSON" });
  }

  if (payload.secret !== SHARED_SECRET) return json(403, { error: "Forbidden" });

  const order = payload.order;
  if (!order || !order.client_name || !Array.isArray(order.lines) || !order.lines.length) {
    return json(400, { error: "Missing required fields (client_name, lines)" });
  }

  const now = new Date();
  const ts = now.toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const slug = safeSlug(order.client_name);
  const orderId = `${ts}__${slug}`;
  const basePath = `inbox/${orderId}`;

  try {
    const metaJson = JSON.stringify({ order_id: orderId, ...order }, null, 2);
    await putFile(`${basePath}/order.json`, b64(metaJson), `order: ${order.client_name}`);

    if (payload.source_file && payload.source_file.content_b64) {
      const filename = (payload.source_file.name || "source.bin").replace(/[^\w.\-]+/g, "_");
      await putFile(
        `${basePath}/source__${filename}`,
        payload.source_file.content_b64,
        `source: ${filename}`,
      );
    }

    return json(200, { ok: true, order_id: orderId });
  } catch (err) {
    return json(502, { error: (err as Error).message });
  }
});
