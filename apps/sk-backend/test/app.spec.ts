import { describe, expect, it } from "vitest";

import app from "../src/app";

describe("sk-backend", () => {
  it("GET /health returns ok", async () => {
    const res = await app.request("/health");
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ status: "ok" });
  });

  it("GET /openapi.json serves an OpenAPI 3.1 spec including /health", async () => {
    const res = await app.request("/openapi.json");
    expect(res.status).toBe(200);
    const spec = (await res.json()) as { openapi: string; paths: Record<string, unknown> };
    expect(spec.openapi).toMatch(/^3\.1/);
    expect(spec.paths["/health"]).toBeDefined();
  });

  it("GET /docs serves the Scalar reference UI", async () => {
    const res = await app.request("/docs");
    expect(res.status).toBe(200);
    expect(await res.text()).toContain("scalar");
  });
});
