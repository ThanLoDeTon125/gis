import { defineConfig, type ViteUserConfig } from "vitest/config";

/** Shared Vitest base. Apps/packages spread or extend this. */
export const baseVitestConfig: ViteUserConfig = {
  test: {
    globals: true,
    passWithNoTests: true,
  },
};

export default defineConfig(baseVitestConfig);
