import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  use: { baseURL: "http://localhost:3100", channel: "chrome", headless: true },
  webServer: { command: "pnpm start", url: "http://localhost:3100", reuseExistingServer: true, timeout: 60_000 },
});
