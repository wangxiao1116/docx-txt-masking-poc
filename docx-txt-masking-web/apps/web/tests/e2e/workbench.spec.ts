import { expect, test, type Page } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../../../..");
const sampleDir = path.join(repoRoot, "sample-data");

async function uploadFile(page: Page, fileName: string) {
  await page.locator("#file").setInputFiles(path.join(sampleDir, fileName));
  await page.getByLabel("分类编码").fill("A1-1");
  await page.getByLabel("分类名称").fill("个人信息");
  await page.getByLabel("分级标签").selectOption("第3级");
  await page.getByLabel("备注").fill(`E2E ${fileName}`);
  await page.getByRole("button", { name: "上传并创建任务" }).click();
  await expect(page.getByText(fileName).first()).toBeVisible({ timeout: 30_000 });
}

test("真实上传、预览、导出、删除和刷新持久化链路", async ({ page, request }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "DOCX/TXT 脱敏验证工作台" })).toBeVisible();
  await expect(page.getByText("暂无处理记录")).toBeVisible();

  await uploadFile(page, "sample_labeled.txt");
  await uploadFile(page, "sample_labeled.docx");

  await page.reload();
  await expect(page.getByText("sample_labeled.txt").first()).toBeVisible();
  await expect(page.getByText("sample_labeled.docx").first()).toBeVisible();

  await page.getByRole("link", { name: /sample_labeled.txt/ }).click();
  await expect(page.getByText("原文文本预览")).toBeVisible();
  await expect(page.getByText("脱敏后文本预览")).toBeVisible();
  await expect(page.getByText("110105********002X")).toBeVisible();
  await expect(page.getByText("category_code=")).toHaveCount(0);

  const download = page.waitForEvent("download");
  await page.getByRole("link", { name: "下载脱敏文件" }).click();
  expect((await download).suggestedFilename()).toContain("sample_labeled_masked");

  const csv = await request.get("/api/v1/exports/manifest.csv");
  expect(csv.ok()).toBeTruthy();
  expect(await csv.text()).toContain("sample_labeled.txt");

  const zip = await request.get("/api/v1/exports/results.zip");
  expect(zip.ok()).toBeTruthy();
  const zipBody = await zip.body();
  expect(zipBody.includes(Buffer.from("处理清单.csv"))).toBeTruthy();
  expect(zipBody.includes(Buffer.from("脱敏文件/"))).toBeTruthy();

  await page.getByRole("link", { name: "返回工作台" }).click();
  page.on("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "删除任务" }).first().click();
  await expect(page.getByText("sample_labeled.txt").first()).toBeHidden({ timeout: 20_000 });
});
