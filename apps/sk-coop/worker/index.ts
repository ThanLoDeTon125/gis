export interface Env {
  ASSETS: Fetcher;
  APP_SECRET: string; // placeholder secret (set via `wrangler secret put APP_SECRET`)
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/healthz") {
      return new Response("ok", { status: 200 });
    }
    return env.ASSETS.fetch(request);
  },
} satisfies ExportedHandler<Env>;
