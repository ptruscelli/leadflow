
import "./globals.css";


export const metadata = {
  title: "Brightline",
  description: "Enquiry form and staff CRM",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <h1>Brightline Studios</h1>
        {children}
      </body>
    </html>
  );
}
