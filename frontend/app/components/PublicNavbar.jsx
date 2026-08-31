"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { isLoggedIn } from "../lib/isLoggedIn";

export default function PublicNavbar() {
  const router = useRouter();
  const [checking, setChecking] = useState(false);

  async function handleStaffPortal(event) {
    event.preventDefault();
    if (checking) {
      return;
    }

    setChecking(true);
    const ok = await isLoggedIn();
    router.push(ok ? "/leads" : "/login");
    setChecking(false);
  }

  return (
    <nav className="flex justify-center gap-8 border-y border-slate-200 bg-white py-3 text-sm">
      <Link href="/" className="text-slate-600 hover:text-slate-900">
        Home
      </Link>
      <Link
        href="/leads"
        onClick={handleStaffPortal}
        className="text-slate-600 hover:text-slate-900"
      >
        Staff Portal
      </Link>
    </nav>
  );
}
