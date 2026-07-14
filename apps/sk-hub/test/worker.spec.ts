import { SELF } from "cloudflare:test";
import { describe, expect, it } from "vitest";

describe("sk-hub worker", () => {
  it("returns 200 from the Worker entry", async () => {
    const res = await SELF.fetch("https://example.com/healthz");
    expect(res.status).toBe(200);
  });
});
