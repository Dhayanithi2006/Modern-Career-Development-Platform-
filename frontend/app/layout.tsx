import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/layout/providers";

export const metadata: Metadata = {
  title: "AI Career Copilot",
  description: "Placement readiness platform for students"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
