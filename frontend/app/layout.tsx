import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { Analytics } from "@vercel/analytics/next";

export const metadata: Metadata = {
  title: "SkillVector — AI Career Intelligence Platform",
  description:
    "AI-powered skill gap analysis. Paste your resume, get a match score, learning path, evidence projects, and interview prep. Powered by Claude.",
  metadataBase: new URL("https://skill-vector.com"),
  openGraph: {
    title: "SkillVector — AI Career Intelligence Platform",
    description:
      "Upload your resume, paste a job description, and get an instant skill gap analysis with a learning path, portfolio projects, and interview prep.",
    url: "https://skill-vector.com",
    siteName: "SkillVector",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "SkillVector — AI Career Intelligence Platform",
    description:
      "AI-powered skill gap analysis. Match score, learning path, portfolio projects, and interview prep in seconds.",
  },
  robots: {
    index: true,
    follow: true,
  },
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
          <Analytics />
        </div>
      </body>
    </html>
  );
}
