import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { join } from "node:path";

const OUT = join(__dirname, "..", "screenshots");
mkdirSync(OUT, { recursive: true });

const sizes = [
  { tag: "desktop", width: 1440, height: 900 },
  { tag: "mobile", width: 390, height: 844 },
] as const;

function watchConsole(page: Page) {
  const errors: string[] = [];
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  page.on("pageerror", (e) => errors.push(String(e)));
  return errors;
}

const nav = (page: Page, name: string) => page.getByRole("button", { name: new RegExp(`^${name}`) }).first().click();

for (const s of sizes) {
  test.describe(s.tag, () => {
    test.use({ viewport: { width: s.width, height: s.height } });

    test("screenshots of every state", async ({ page }) => {
      const errors = watchConsole(page);
      await page.goto("/");
      await page.waitForLoadState("networkidle");
      const shot = (name: string) => page.screenshot({ path: join(OUT, `${s.tag}-${name}.png`) });
      const openNav = async () => {
        if (s.tag === "mobile") await page.getByRole("button", { name: "Open menu" }).click();
      };

      await page.waitForTimeout(1200); // count up and chart draw in finish
      await shot("01-default");

      // warning state is on the overview page
      await page.getByText("Mailbox 2 is near its daily cap").scrollIntoViewIfNeeded();
      await shot("02-warning");

      // button mid processing
      const slow = page.getByRole("button", { name: "Run a slow action" });
      await slow.scrollIntoViewIfNeeded();
      await slow.click();
      await expect(slow).toHaveAttribute("data-state", "processing");
      await shot("03-button-processing");
      await expect(slow).toHaveAttribute("data-state", "success", { timeout: 4000 });
      await shot("04-button-success");

      // toast with undo
      await page.getByRole("button", { name: "Archive with undo" }).click();
      await expect(page.getByText("Archived 3 leads")).toBeVisible();
      await page.waitForTimeout(500);
      await shot("05-toast");

      // detail sheet from the table
      await openNav();
      await nav(page, "Leads");
      await expect(page.getByRole("grid", { name: "Leads" })).toBeVisible();
      await page.waitForTimeout(400);
      await shot("06-table");
      await page.getByRole("grid", { name: "Leads" }).focus();
      await page.keyboard.press("j");
      await page.keyboard.press("Enter");
      await expect(page.getByRole("dialog")).toBeVisible();
      await page.waitForTimeout(500);
      await shot("07-detail-sheet");
      await page.keyboard.press("Escape");

      // empty, error, loading
      await openNav();
      await nav(page, "States and forms");
      await page.waitForTimeout(400);
      await shot("08-empty-state");
      await page.getByRole("radio", { name: "Error" }).click();
      await page.waitForTimeout(300);
      await shot("09-error-state");

      // command palette
      await page.keyboard.press("Control+k");
      await expect(page.getByPlaceholder("Search or run an action")).toBeVisible();
      await page.waitForTimeout(300);
      await shot("10-command-palette");
      await page.getByText("Switch to dark theme").click();

      // dark theme
      await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
      await page.waitForTimeout(500);
      await shot("11-dark-theme");

      expect(errors, errors.join("\n")).toEqual([]);
    });
  });
}

test.describe("behaviour checks (desktop)", () => {
  test.use({ viewport: { width: 1440, height: 900 } });

  test("5,000 rows are windowed", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: /^Leads/ }).click();
    await expect(page.getByText("5,000 rows")).toBeVisible();
    const rows = await page.getByRole("row").count();
    expect(rows).toBeLessThan(60);
    const t0 = Date.now();
    await page.getByRole("grid", { name: "Leads" }).evaluate((el) => (el.scrollTop = 100000));
    await page.waitForTimeout(150);
    expect(Date.now() - t0).toBeLessThan(1500);
    await expect(page.getByRole("row").nth(5)).toBeVisible();
  });

  test("keyboard only: table select and bulk bar", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: /^Leads/ }).click();
    await page.getByRole("grid", { name: "Leads" }).focus();
    await page.keyboard.press("x");
    await expect(page.getByRole("toolbar")).toContainText("1 selected");
    await page.keyboard.press("Escape");
    await expect(page.getByRole("toolbar")).toHaveCount(0);
  });

  test("kanban card moves between columns by dragging", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: /^Pipeline/ }).click();
    const won = page.getByRole("region", { name: "Won" });
    const before = Number(await won.locator(".sx-kanban__head .sx-num").innerText());
    const card = page.getByRole("region", { name: "New" }).locator(".sx-kanban__card").first();
    const box = (await card.boundingBox())!;
    const target = (await won.boundingBox())!;
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width / 2 + 20, box.y + 20, { steps: 4 });
    await page.waitForTimeout(150); // dnd-kit measures drop targets on the next frame, a person is never faster than this
    await page.mouse.move(target.x + target.width / 2, target.y + 80, { steps: 12 });
    await page.waitForTimeout(150);
    await expect(won).toHaveAttribute("data-over", "true");
    await page.mouse.up();
    await expect(won.locator(".sx-kanban__head .sx-num")).toHaveText(String(before + 1));
  });

  test("kanban cards are not buttons, hold a link, and open from the keyboard", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: /^Pipeline/ }).click();
    const card = page.getByRole("group", { name: /^Lead / }).first();
    await expect(card).toHaveAttribute("aria-roledescription", "draggable card");
    expect(await card.getAttribute("role")).toBe("group");
    await expect(card.getByRole("link", { name: /^Email / })).toBeVisible();
    await card.focus();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("dialog")).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.getByRole("dialog")).toHaveCount(0);
    const open = page.getByRole("button", { name: /^Open Lead / }).first();
    await open.focus();
    await expect(open).toBeVisible();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("dialog")).toBeVisible();
  });

  test("kanban keyboard lift and drop still works", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: /^Pipeline/ }).click();
    const contacted = page.getByRole("region", { name: "Contacted" });
    const before = Number(await contacted.locator(".sx-kanban__head .sx-num").innerText());
    const card = page.getByRole("region", { name: "New" }).getByRole("group", { name: /^Lead / }).first();
    await card.focus();
    await page.keyboard.press("Space");
    await page.waitForTimeout(150);
    await page.keyboard.press("ArrowRight");
    await page.waitForTimeout(250);
    await page.keyboard.press("Space");
    await expect(contacted.locator(".sx-kanban__head .sx-num")).toHaveText(String(before + 1));
  });

  for (const view of ["Overview", "Pipeline", "Leads", "States and forms"]) {
    test(`axe: no serious or critical findings on ${view}`, async ({ page }) => {
      await page.goto("/");
      if (view !== "Overview") await page.getByRole("button", { name: new RegExp(`^${view}`) }).first().click();
      await page.waitForTimeout(900);
      const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
      const bad = r.violations.filter((v) => v.impact === "serious" || v.impact === "critical");
      expect(bad.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(" ")).slice(0, 3).join(" | ")}`)).toEqual([]);
    });
  }

  test("axe in the dark theme", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Switch to dark theme" }).click();
    await page.waitForTimeout(700);
    const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
    expect(r.violations.filter((v) => v.impact === "serious" || v.impact === "critical").map((v) => v.id)).toEqual([]);
  });

  test("reduced motion removes movement but keeps the page working", async ({ browser }) => {
    const ctx = await browser.newContext({ reducedMotion: "reduce", viewport: { width: 1440, height: 900 } });
    const page = await ctx.newPage();
    await page.goto("/");
    const slow = page.getByRole("button", { name: "Run a slow action" });
    await slow.click();
    await expect(slow).toHaveAttribute("data-state", "processing");
    const anim = await page.locator(".sx-spinner").evaluate((el) => getComputedStyle(el).animationName);
    expect(anim).toBe("none");
    await ctx.close();
  });

  test("no layout shift on load", async ({ page }) => {
    await page.addInitScript(() => {
      (window as unknown as { __cls: number }).__cls = 0;
      new PerformanceObserver((l) => {
        for (const e of l.getEntries() as unknown as { value: number; hadRecentInput: boolean }[]) if (!e.hadRecentInput) (window as unknown as { __cls: number }).__cls += e.value;
      }).observe({ type: "layout-shift", buffered: true });
    });
    await page.goto("/");
    await page.waitForTimeout(2000);
    const cls = await page.evaluate(() => (window as unknown as { __cls: number }).__cls);
    expect(cls).toBeLessThan(0.1);
  });
});
