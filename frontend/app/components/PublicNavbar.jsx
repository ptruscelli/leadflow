import Link from "next/link";

export default function PublicNavbar() {
  return (
        <nav>
          <Link href="/">Home</Link>
          <Link href="/leads">Staff Portal</Link>
        </nav>

  );
}
