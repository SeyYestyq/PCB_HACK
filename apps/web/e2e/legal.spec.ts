import { test, expect } from "@playwright/test";

test("legal chat landing", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Юридический ассистент/i })).toBeVisible();
  await expect(page.getByPlaceholder(/нормативным/i)).toBeVisible();
  await expect(page.getByRole("button", { name: /Спросить/i })).toBeVisible();
});
