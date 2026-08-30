"use client";

import { useState } from "react";

export default function LoginForm() {

    const [email, setEmail] = useState("");
    const [status, setStatus] = useState("idle");

    async function handleSubmit(event) {
      event.preventDefault();
      setStatus("loading");
      
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/magic-link`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ email }),
        });
        
        if (!response.ok) {
          return
        }

        setStatus("success");

      } catch (error) {
        setStatus("error");
        console.error(error);
      }

    }

    return (
      <>
        <h1>Staff login</h1>
        <p>Enter your email to request a login link</p>
        <form onSubmit={handleSubmit}>
          <label>
            Email address
            <input
              type="email"
              name="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          <button type="submit">Send login link</button>
        </form>
      </>
    );
  }
  