"use client";

import { useState } from "react";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function LoginForm() {

    const [email, setEmail] = useState("");
    const [status, setStatus] = useState("idle");
    const [emailError, setEmailError] = useState(false);

    async function handleSubmit(event) {
      event.preventDefault();

      if (!EMAIL_PATTERN.test(email.trim())) {
        setEmailError(true);
        return;
      }

      setEmailError(false);
      setStatus("loading");
      
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/magic-link`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ email }),
        });
        
        if (!response.ok) {
          setStatus("error");
          return
        }

        setStatus("success");

      } catch (error) {
        setStatus("error");
        console.error(error);
      }

    }

    if (status === "success") {
      return (
        <main className="mx-auto w-full max-w-md">
          <h2 className="mb-6 text-center text-xl font-medium">Staff login</h2>
          <p className="mb-6 text-center text-sm text-slate-600">
            If email is on the allowlist, a login link was sent.
          </p>
          <button
            type="button"
            onClick={() => setStatus("idle")}
            className="w-full cursor-pointer rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
          >
            Use a different email
          </button>
        </main>
      );
    }

    return (
      <main className="mx-auto w-full max-w-md">
        <h2 className="mb-2 text-center text-xl font-medium">Staff login</h2>
        <p className="mb-6 text-center text-sm text-slate-600">
          Enter your email to request a login link
        </p>
        <form noValidate onSubmit={handleSubmit} className="flex flex-col gap-4">
          <label className={`flex flex-col gap-1 text-sm ${emailError ? "text-red-600" : ""}`}>
            Email address
            <input
              type="email"
              name="email"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value);
                setEmailError(false);
              }}
              className={`w-full rounded-md border bg-white px-3 py-2 text-sm text-slate-900 ${
                emailError ? "border-red-600" : "border-slate-300"
              }`}
            />
          </label>
          <button
            type="submit"
            className="cursor-pointer rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
          >
            Send login link
          </button>
        </form>
      </main>
    );
  }
