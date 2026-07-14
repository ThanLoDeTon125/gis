import { cloudflareTest } from "@cloudflare/vitest-pool-workers";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// pool-workers 0.18.4 (Vitest 4) API: the old `defineWorkersProject` + `test.poolOptions.workers`
// was replaced by the `cloudflareTest()` Vite plugin (see the package's vitest-v3-to-v4 codemod).
export default defineConfig({
  test: {
    projects: [
      {
        plugins: [react()],
        test: { name: "unit", environment: "jsdom", include: ["src/**/*.test.tsx"] },
      },
      {
        plugins: [
          cloudflareTest({
            main: "./worker/index.ts",
            wrangler: { configPath: "./wrangler.jsonc" },
          }),
        ],
        test: { name: "workers", include: ["test/**/*.spec.ts"] },
      },
    ],
  },
});
