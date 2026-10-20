import assert from "node:assert/strict";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "playwright";

const origin = new URL(process.argv[2] || "https://qualitylayer.dev");
assert(origin.protocol === "https:" || ["localhost", "127.0.0.1"].includes(origin.hostname), "Checkout verification requires HTTPS or loopback");
const output = process.argv[3] ? resolve(process.argv[3]) : null;
if (output) await mkdir(output, { recursive: true, mode: 0o700 });
const browser = await chromium.launch({ headless: true });
const results = [];
try {
  const context = await browser.newContext({ locale: "en-US", viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();
  page.setDefaultTimeout(20000);
  await page.route("**/api/billing", route => route.abort());
  for (const billing of ["yearly", "monthly"]) {
    for (const plan of ["Solo", "Team"]) {
      await page.goto(new URL("/pricing", origin).href);
      await page.getByRole("button", { name: billing === "monthly" ? "Monthly" : /Yearly/, exact: billing === "monthly" }).click();
      const link = page.getByRole("link", { name: `Start ${plan}`, exact: true });
      assert.equal(new URL(await link.getAttribute("href")).origin, "https://buy.polar.sh");
      // A native link still works if the website's checkout API or iframe is blocked.
      await link.click();
      await page.waitForURL(url => url.origin === "https://polar.sh" && url.pathname.startsWith("/checkout/"));
      const name = `QualityLayer ${plan}${billing === "yearly" ? " (yearly)" : ""}`;
      await page.getByText(name, { exact: true }).waitFor();
      await page.getByRole("textbox", { name: "Email", exact: true }).waitFor();
      const payment = page.frameLocator('iframe[title="Secure payment input frame"]');
      for (const field of ["Card number", "Expiration date", "Security code"]) await payment.getByRole("textbox", { name: field, exact: true }).waitFor();
      const amount = plan === "Solo" ? (billing === "yearly" ? 288 : 29) : (billing === "yearly" ? 468 : 49);
      assert((await page.locator("body").innerText()).includes(`$${amount}`), `${name}: expected price missing`);
      if (output) await page.screenshot({ path: resolve(output, `${plan.toLowerCase()}-${billing}.png`) });
      results.push({ plan, billing, amount, currency: "USD", paymentFieldsReady: true, paymentSubmitted: false });
      console.log(`PASS ${plan} ${billing}: $${amount}; Stripe payment fields ready; no payment submitted`);
    }
  }
} finally { await browser.close(); }
if (output) await writeFile(resolve(output, "checkout-readiness.json"), JSON.stringify({ origin: origin.origin, checkedAt: new Date().toISOString(), results }, null, 2), { mode: 0o600 });
