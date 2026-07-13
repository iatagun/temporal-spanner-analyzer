import { Newsreader, Source_Sans_3 } from "next/font/google";
import "./globals.css";

// Newsreader (serif, headings) + Source Sans 3 (UI/body) -- the
// academic-journal pairing this redesign is going for. Both loaded as CSS
// variables so Tailwind's font-serif/font-sans utilities (wired in
// globals.css) can reference them without a FOUC-prone <link> tag.
// latin-ext is required, not optional -- Turkish diacritics (ç ğ ı ö ş ü)
// live outside the plain "latin" subset, and this app's own body text is
// Turkish throughout.
const newsreader = Newsreader({
  subsets: ["latin", "latin-ext"],
  variable: "--font-serif",
  style: ["normal", "italic"],
  display: "swap",
});

const sourceSans = Source_Sans_3({
  subsets: ["latin", "latin-ext"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata = {
  title: "Temporal Spanner Analyzer — Derlem Dilbiliminde Zamansal Kavram Analizi",
  description: "Türkçe derlemlerde kelime birlikteliklerinin zamansal evrimini Baligács (2026) lineer spanner algoritmasıyla analiz eden açık kaynak araç. CoNLL-U, CSV, JSON, VRT destekler.",
  keywords: "derlem dilbilimi, zamansal çizge, spanner, Türkçe NLP, kelime birlikteliği, PMI, klik analizi",
  openGraph: {
    title: "Temporal Spanner Analyzer",
    description: "Derlem dilbiliminde zamansal kavram evrimi analizi",
    url: "https://frontend-teal-iota-ee3dg8j6wx.vercel.app",
    type: "website",
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="tr" className={`${newsreader.variable} ${sourceSans.variable}`}>
      <head>
        <meta httpEquiv="Content-Security-Policy" content="script-src 'self' 'unsafe-eval' 'unsafe-inline';" />
        <meta name="google-site-verification" content="iWWxPp7bzUz7BIlM8Kb27tIKEtz_6Y9iz1tqI6TGEI4" />
      </head>
      <body className="font-sans">{children}</body>
    </html>
  );
}
