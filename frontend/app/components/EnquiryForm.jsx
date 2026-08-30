"use client";

import { useState } from "react";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const SOURCES = ["google", "referral", "social_media", "other"];

function apiErrorMessage(data) {
  if (!data || data.detail == null) {
    return "Something went wrong. Please try again.";
  }

  if (typeof data.detail === "string") {
    return data.detail;
  }

  if (Array.isArray(data.detail)) {
    const messages = data.detail
      .map((item) => item.msg)
      .filter(Boolean);
    if (messages.length > 0) {
      return messages.join(". ");
    }
  }

  return "Something went wrong. Please try again.";
}

function fieldErrorsFromApi(data) {
  const errors = {};
  if (!Array.isArray(data?.detail)) {
    return errors;
  }

  for (const item of data.detail) {
    const field = item.loc?.at(-1);
    if (field && field !== "body") {
      errors[field] = true;
    }
  }

  return errors;
}

function validateEnquiry({ name, company, email, source, message }) {
  return {
    name: name.trim().length < 3 || name.trim().length > 100,
    company: company.trim().length < 1 || company.trim().length > 100,
    email: !EMAIL_PATTERN.test(email.trim()),
    source: !SOURCES.includes(source),
    message: message.trim().length < 1 || message.length > 2000,
  };
}

export default function EnquiryForm() {
  const [name, setName] = useState("");
  const [company, setCompany] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [source, setSource] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});

  const isLoading = status === "loading";

  function clearFieldError(field) {
    setFieldErrors((current) => {
      if (!current[field]) {
        return current;
      }
      const next = { ...current };
      delete next[field];
      return next;
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const nextErrors = validateEnquiry({
      name,
      company,
      email,
      source,
      message,
    });

    if (Object.values(nextErrors).some(Boolean)) {
      setFieldErrors(nextErrors);
      return;
    }

    setFieldErrors({});
    setStatus("loading");
    setErrorMessage("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/leads`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name,
            email,
            company,
            phone: phone.trim() || null,
            source,
            message,
          }),
        }
      );

      if (!response.ok) {
        let data = null;
        try {
          data = await response.json();
        } catch {
          data = null;
        }
        setFieldErrors(fieldErrorsFromApi(data));
        setErrorMessage(apiErrorMessage(data));
        setStatus("error");
        return;
      }

      setName("");
      setCompany("");
      setEmail("");
      setPhone("");
      setSource("");
      setMessage("");
      setStatus("success");
    } catch (error) {
      console.error(error);
      setErrorMessage("Could not send your enquiry. Please try again.");
      setStatus("error");
    }
  }

  function fieldClass(field) {
    return `w-full rounded-md border bg-white px-3 py-2 text-sm text-slate-900 disabled:bg-slate-100 ${
      fieldErrors[field] ? "border-red-600" : "border-slate-300"
    }`;
  }

  function labelClass(field) {
    return `flex flex-col gap-1 text-sm ${
      fieldErrors[field] ? "text-red-600" : ""
    }`;
  }

  if (status === "success") {
    return (
      <main className="mx-auto w-full max-w-md">
        <h2 className="mb-6 text-center text-xl font-medium">Contact Us</h2>
        <p className="mb-6 text-center text-sm text-slate-600">
          Thanks — we have received your enquiry and will be in touch.
        </p>
        <button
          type="button"
          onClick={() => setStatus("idle")}
          className="w-full cursor-pointer rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          Send another enquiry
        </button>
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-md">
      <h2 className="mb-6 text-center text-xl font-medium">Contact Us</h2>

      <form noValidate onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className={labelClass("name")}>
          Full name
          <input
            type="text"
            name="name"
            value={name}
            onChange={(event) => {
              setName(event.target.value);
              clearFieldError("name");
            }}
            maxLength={100}
            disabled={isLoading}
            className={fieldClass("name")}
          />
        </label>

        <label className={labelClass("company")}>
          Company
          <input
            type="text"
            name="company"
            value={company}
            onChange={(event) => {
              setCompany(event.target.value);
              clearFieldError("company");
            }}
            maxLength={100}
            disabled={isLoading}
            className={fieldClass("company")}
          />
        </label>

        <label className={labelClass("email")}>
          Email address
          <input
            type="email"
            name="email"
            value={email}
            onChange={(event) => {
              setEmail(event.target.value);
              clearFieldError("email");
            }}
            disabled={isLoading}
            className={fieldClass("email")}
          />
        </label>

        <label className={labelClass("phone")}>
          <span className="flex items-center gap-1">
            Phone number{" "}
            <span className="text-xs text-slate-500">(optional)</span>
          </span>
          <input
            type="tel"
            name="phone"
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
            disabled={isLoading}
            className={fieldClass("phone")}
          />
        </label>

        <label className={labelClass("source")}>
          How did you hear about us?
          <select
            name="source"
            value={source}
            onChange={(event) => {
              setSource(event.target.value);
              clearFieldError("source");
            }}
            disabled={isLoading}
            className={fieldClass("source")}
          >
            <option value="">Please select</option>
            <option value="google">Google</option>
            <option value="referral">Referral</option>
            <option value="social_media">Social media</option>
            <option value="other">Other</option>
          </select>
        </label>

        <label className={labelClass("message")}>
          Message
          <textarea
            name="message"
            value={message}
            onChange={(event) => {
              setMessage(event.target.value);
              clearFieldError("message");
            }}
            maxLength={2000}
            rows={6}
            disabled={isLoading}
            className={fieldClass("message")}
          />
        </label>
        <p className="text-right text-xs text-slate-500">{message.length}/2000</p>

        {status === "error" && (
          <p className="text-center text-sm text-red-700">{errorMessage}</p>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="cursor-pointer rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {isLoading ? "Sending..." : "Send enquiry"}
        </button>
      </form>
    </main>
  );
}
