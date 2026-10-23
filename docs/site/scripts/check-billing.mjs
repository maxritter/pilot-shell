import assert from "node:assert/strict";
import { chromium, expect } from "playwright/test";
import { QUALITYLAYER_PRODUCTS } from "../src/lib/polar-products.ts";

const origin = new URL(process.argv[2] ?? "http://127.0.0.1:8090");
assert(["127.0.0.1", "localhost"].includes(origin.hostname), "Billing action tests require the isolated local fixture");
const products = [
  ...Object.values(QUALITYLAYER_PRODUCTS.solo),
  ...Object.values(QUALITYLAYER_PRODUCTS.team),
  "35801944-799d-4763-88fa-b2046765464f",
  "c0a1f846-2909-4aff-b3fe-42a4818c34b5",
  "bf3d0ac1-6cda-4122-bd76-a20d0beef958",
];
const browser = await chromium.launch({ headless: true });
try {
  for (const productId of products) {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    try {
      // Fail closed if the fixture ever attempts to reach a real billing or email service.
      await context.route("**/*", (route) => new URL(route.request().url()).origin === origin.origin ? route.continue() : route.abort());
      const reset = await context.request.post(new URL("/__billing-fixture__/reset", origin).href, { data: { productId } });
      assert.equal(reset.status(), 200);
      const configuration = await reset.json();
      assert.equal(configuration.productId, productId);
      const page = await context.newPage();
      page.setDefaultTimeout(10000);
      const errors = [];
      page.on("pageerror", (error) => errors.push(error.message));
      await page.goto(new URL("/billing", origin).href);
      await page.getByLabel("Email address", { exact: true }).fill("buyer@example.test");
      await page.getByRole("button", { name: "Send sign-in code", exact: true }).click();
      await expect(page.getByLabel("Sign-in code", { exact: true })).toBeVisible();
      const mail = await (await context.request.get(new URL("/__billing-fixture__/mail", origin).href)).json();
      await page.getByLabel("Sign-in code", { exact: true }).fill(mail.code);
      await page.getByRole("button", { name: "Sign in", exact: true }).click();
      await expect(page.getByRole("heading", { name: "Subscription & billing", exact: true })).toBeVisible();
      const account = await (await context.request.get(new URL("/api/billing", origin).href)).json();
      assert.equal(account.subscriptions[0].productId, productId);
      assert.equal(account.seats.length, configuration.seats === null ? 0 : 1);
      await expect(page.getByText("TEST-1", { exact: true })).toBeVisible();
      await page.getByRole("button", { name: "Prepare invoice", exact: true }).click();
      await expect(page.getByRole("link", { name: "Download invoice", exact: true })).toBeVisible();
      await page.getByRole("button", { name: "Prepare receipt", exact: true }).click();
      await expect(page.getByRole("link", { name: "Download receipt", exact: true })).toBeVisible();
      await page.getByRole("button", { name: "Update payment method", exact: true }).click();
      await page.getByRole("button", { name: "Use fixture card", exact: true }).click();
      await expect(page.getByRole("listitem").filter({ hasText: "visa •••• 4321" })).toBeVisible();
      await page.getByRole("tab", { name: "Licence keys", exact: true }).click();
      await expect(page.getByText("MacBook Pro", { exact: true })).toBeVisible();
      await page.getByRole("button", { name: /^Release / }).last().click();
      await page.getByRole("button", { name: "Release machine", exact: true }).click();
      await expect(page.getByText("Machine released. Its place on the key is free.", { exact: true })).toBeVisible();
      await expect(page.getByRole("button", { name: /^Release / })).toHaveCount(1);
      const legacy = products.indexOf(productId) >= 4;
      if (!legacy) {
        await page.getByRole("button", { name: /^Switch to .* billing$/ }).click();
        await page.getByRole("button", { name: "Schedule change", exact: true }).click();
        await page.getByRole("button", { name: "Remove scheduled change", exact: true }).click();
        await page.getByRole("button", { name: "Keep current plan", exact: true }).click();
        await expect(page.getByRole("button", { name: "Remove scheduled change", exact: true })).toHaveCount(0);
      }
      const teamTab = page.getByRole("tab", { name: "Team seats", exact: true });
      const team = configuration.seats !== null;
      if (team) await expect(teamTab).toBeVisible();
      else await expect(teamTab).toHaveCount(0);
      if (team) {
        await teamTab.click();
        await page.getByLabel("Assign a seat by email", { exact: true }).fill("teammate@example.test");
        await page.getByRole("button", { name: "Invite teammate", exact: true }).click();
        const seat = page.getByRole("listitem").filter({ hasText: "teammate@example.test" });
        await expect(seat).toBeVisible();
        await seat.getByRole("button", { name: "Resend invitation", exact: true }).click();
        await page.getByRole("button", { name: "Send invitation", exact: true }).click();
        await expect(page.getByRole("dialog")).toHaveCount(0);
        await seat.getByRole("button", { name: "Revoke seat", exact: true }).click();
        await page.getByRole("dialog").getByRole("button", { name: "Revoke seat", exact: true }).click();
        await expect(seat).toHaveCount(0);
        if (legacy) await expect(page.getByLabel("Purchased seats", { exact: true })).toBeDisabled();
        else {
          await page.getByLabel("Purchased seats", { exact: true }).fill("3");
          await page.getByRole("button", { name: "Review seat count", exact: true }).click();
          await page.getByRole("button", { name: "Schedule change", exact: true }).click();
          await page.getByRole("button", { name: "Remove scheduled change", exact: true }).click();
          await page.getByRole("button", { name: "Keep current plan", exact: true }).click();
          await expect(page.getByRole("button", { name: "Remove scheduled change", exact: true })).toHaveCount(0);
        }
      }
      await page.getByRole("button", { name: "Pause subscription", exact: true }).click();
      await page.getByRole("button", { name: "Pause at period end", exact: true }).click();
      await expect(page.getByText("Pauses at period end", { exact: true })).toBeVisible();
      await page.getByRole("button", { name: "Keep active", exact: true }).click();
      await page.getByRole("dialog").getByRole("button", { name: "Keep active", exact: true }).click();
      await expect(page.getByText("active", { exact: true })).toBeVisible();
      await page.getByRole("button", { name: "Cancel subscription", exact: true }).click();
      await page.getByRole("button", { name: "Continue", exact: true }).click();
      await page.getByRole("dialog").getByRole("button", { name: "Cancel subscription", exact: true }).click();
      await page.getByRole("button", { name: "Close", exact: true }).click();
      await expect(page.getByText("Ends at period end", { exact: true })).toBeVisible();
      await page.getByRole("button", { name: "Keep subscription", exact: true }).click();
      await page.getByRole("dialog").getByRole("button", { name: "Keep subscription", exact: true }).click();
      await expect(page.getByText("active", { exact: true })).toBeVisible();
      await page.getByRole("button", { name: "Sign out", exact: true }).click();
      await expect(page.getByLabel("Email address", { exact: true })).toBeVisible();
      assert.deepEqual(errors, []);
      console.log(JSON.stringify({ productId, signIn: true, invoiceAndReceipt: true, paymentFixture: true, machineRelease: true, billingPeriod: legacy ? "preserved" : "scheduled-and-cleared", teamSeats: team, pauseAndUndo: true, cancellationAndUndo: true, signOut: true }));
    } finally { await context.close(); }
  }
} finally { await browser.close(); }
