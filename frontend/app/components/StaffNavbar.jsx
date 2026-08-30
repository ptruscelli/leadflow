"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

export default function StaffNavbar() {
  const router = useRouter();

  async function handleLogout() {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error(error);
    }

    router.replace('/login');
  }

  return (
    <nav className="flex justify-center gap-8 border-y border-slate-200 bg-white py-3 text-sm">
      <Link href="/" className="text-slate-600 hover:text-slate-900">
        Home
      </Link>
      <button
        type="button"
        onClick={handleLogout}
        className="cursor-pointer text-slate-600 hover:text-slate-900"
      >
        Log Out
      </button>
    </nav>
  );
}