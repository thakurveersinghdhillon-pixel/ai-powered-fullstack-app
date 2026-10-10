import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI-Powered Full-Stack Application",
  description: "Next.js, FastAPI, PostgreSQL, and LLM Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-slate-950 text-slate-100">{children}</body>
    </html>
  );
}
