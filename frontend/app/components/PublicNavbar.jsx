import Link from "next/link";

export default function PublicNavbar() {
  return (
    <nav className="flex justify-center gap-8 border-y border-slate-200 bg-white py-3 text-sm">
      <Link href="/" className="text-slate-600 hover:text-slate-900">
        Home
      </Link>
      <Link href="/leads" className="text-slate-600 hover:text-slate-900">
        Staff Portal
      </Link>
    </nav>
  );
}
