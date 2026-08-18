import tnaEslintConfig from "@nationalarchives/eslint-config";
import { defineConfig, globalIgnores } from "eslint/config";
import globals from "globals";

export default defineConfig([
  ...tnaEslintConfig,
  globalIgnores(["lighthouserc.js", "init.uv.js", "init.uv.test.js"]),
  {
    languageOptions: {
      globals: {
        ...globals.node,
        ...globals.jest,
      },
    },
  },
]);
