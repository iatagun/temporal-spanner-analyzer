import "./globals.css";

export const metadata = {
  title: "Temporal Spanner Analyzer",
  description: "Baligács (2026) — Temporal clique to linear spanner visualizer",
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
