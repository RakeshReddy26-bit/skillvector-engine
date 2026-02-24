import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
  title: "SkillVector — AI Career Intelligence Platform",
  description:
    "AI-powered skill gap analysis. Paste your resume, get a match score, learning path, evidence projects, and interview prep. Powered by Claude.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {/* Top glow orb */}
        <div className="fixed -top-52 left-1/2 -translate-x-1/2 w-[800px] h-[400px] rounded-full bg-accent/[0.07] blur-3xl pointer-events-none z-0" />
        <div className="relative z-10">
          <AuthProvider>{children}</AuthProvider>
        </div>
      </body>
    </html>
  );
}
