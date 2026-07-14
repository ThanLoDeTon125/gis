import { baseVitestConfig } from "@sankit/config/vitest.base";
import swc from "unplugin-swc";
import { defineConfig } from "vitest/config";

export default defineConfig({
  ...baseVitestConfig,
  test: {
    // spread the shared base test options (globals, passWithNoTests) then add api-specific ones
    ...baseVitestConfig.test,
    root: "./",
    include: ["test/**/*.spec.ts", "src/**/*.spec.ts"],
    setupFiles: ["./test/setup.ts"],
  },
  plugins: [
    swc.vite({
      jsc: {
        transform: { legacyDecorator: true, decoratorMetadata: true },
      },
    }),
  ],
});
