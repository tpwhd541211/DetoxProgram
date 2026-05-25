import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Unbelievable v2 - Youtube Detox",
  description: "당신의 알고리즘 편향성을 거울 치료해 드립니다.",
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  minimumScale: 0.5,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className="h-full">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=0.5" />
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet" />
      </head>
      <body className="h-full overflow-hidden">
        {children}
      </body>
    </html>
  );
}
