"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import StaffNavbar from "../components/StaffNavbar";
import { isLoggedIn } from "../lib/isLoggedIn";

export default function LeadsLayout({ children }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function gate() {
      const ok = await isLoggedIn();
      if (cancelled) {
        return;
      }
      if (!ok) {
        router.replace("/login");
        return;
      }
      setReady(true);
    }

    gate();

    return () => {
      cancelled = true;
    };
  }, [router]);

  if (!ready) {
    return null;
  }

  return (
    <>
      <StaffNavbar />
      {children}
    </>
  );
}
