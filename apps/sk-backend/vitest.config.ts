import { baseVitestConfig } from "@sankit/config/vitest.base";
import { defineConfig, mergeConfig } from "vitest/config";

export default mergeConfig(
  defineConfig(baseVitestConfig),
  defineConfig({
    test: { include: ["test/**/*.spec.ts"] },
  }),
);
