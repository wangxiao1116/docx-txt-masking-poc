import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "DOCX/TXT 脱敏验证工作台",
  description: "高保真 DOCX/TXT 脱敏验证 Web 产品工程",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
