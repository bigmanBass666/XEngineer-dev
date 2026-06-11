import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "XEngineer",
  description: "Qiniu AI Hackathon Batch 4",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
