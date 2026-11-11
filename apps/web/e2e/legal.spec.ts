import { test, expect } from "@playwright/test";

const VERDICTS =
  /Подтверждено источниками|Подтверждено частично|Обоснованный отказ|Нужно уточнение|Вне компетенции ассистента/;
const SEND = { name: "Отправить вопрос" };

test("пустой экран: заголовок, герой, примеры и поле вопроса", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Юридический ассистент", level: 1 }),
  ).toBeAttached();
  await expect(
    page.getByRole("heading", { name: /Ответ по документам/i, level: 2 }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: /Договор аренды/i }).first()).toBeVisible();
  await expect(page.getByRole("textbox").first()).toBeVisible();
  await expect(page.getByRole("button", SEND)).toBeVisible();
  await expect(page.getByRole("heading", { name: "Источники", level: 2 })).toBeVisible();
});

test("пример заполняет поле, ответ несёт статус, источники и паспорт сессии", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: /Договор аренды/i }).first().click();
  await page.getByRole("button", SEND).click();

  await expect(page.getByText(VERDICTS)).toBeVisible({ timeout: 60_000 });
  await expect(page.getByText("Паспорт сессии")).toBeVisible();
  await expect(page.getByRole("button", { name: /Скопировать/i })).toBeVisible();
});

test("вопрос вне базы знаний даёт вердикт отказа или частичный ответ", async ({ page }) => {
  await page.goto("/");
  await page
    .getByRole("textbox")
    .first()
    .fill("Какой размер пособия по беременности и родам?");
  await page.getByRole("button", SEND).click();

  await expect(
    page.getByText(/Обоснованный отказ|Подтверждено источниками|Подтверждено частично/),
  ).toBeVisible({ timeout: 60_000 });
});

test("счётчик символов и ошибка лимита у поля ввода", async ({ page }) => {
  await page.goto("/");
  const box = page.getByRole("textbox").first();
  await box.fill("я".repeat(3100));
  await expect(page.locator(".counter-near")).toBeVisible();

  await box.fill("я".repeat(4010));
  await expect(page.locator(".composer-field.has-error")).toBeVisible();
  await expect(page.getByRole("alert")).toContainText("Слишком длинный вопрос");
});

test("клавиша / фокусирует поле вопроса", async ({ page }) => {
  await page.goto("/");
  await page.locator("body").click();
  await page.keyboard.press("/");
  await expect(page.getByRole("textbox").first()).toBeFocused();
});
