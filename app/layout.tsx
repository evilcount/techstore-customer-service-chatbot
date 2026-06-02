import "./globals.css";

export const metadata = {
  title: "TechStore Plus Support",
  description: "Customer support chat demo",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
