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
      <header>
        <nav>
          <Link href="/">Home</Link>
          <button type="button" onClick={handleLogout}>Log Out</button>
        </nav>
      </header>

  );
}