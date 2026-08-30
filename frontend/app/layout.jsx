import "./globals.css";

export const metadata = {
  title: "Brightline",
  description: "Enquiry form and staff CRM",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        <header className="bg-white px-4 py-8">
          <h1 className="text-center text-4xl font-semibold tracking-tight sm:text-5xl">
            Brightline Studios
          </h1>
        </header>
        {children}
      </body>
    </html>
  );
}
