"use client";

import EnquiryForm from "./components/EnquiryForm";
import PublicNavbar from "./components/PublicNavbar";

export default function Home() {
  return (
    <>
      <PublicNavbar />
      <div className="px-4 py-10">
        <EnquiryForm />
      </div>
    </>
  );
}