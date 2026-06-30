import "./globals.css";

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
    <html lang="en">
      <head>
        <meta httpEquiv="Content-Security-Policy" content="script-src 'self' 'unsafe-eval' 'unsafe-inline';" />
      </head>
      <body className="font-sans">{children}</body>
    </html>
  );
}
