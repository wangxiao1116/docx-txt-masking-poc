import { describe, expect, it } from "vitest";

import { formatBytes, maskIdCards } from "@/lib/utils";

describe("frontend utilities", () => {
  it("masks id card values before showing original preview by default", () => {
    const value = "110105" + "19491231002X";
    expect(maskIdCards(`身份证号：${value}`)).toContain("110105********002X");
  });

  it("formats file sizes for the task table", () => {
    expect(formatBytes(1024)).toBe("1.0 KB");
  });
});
