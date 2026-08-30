"use client";

import { useState } from "react";

export default function EnquiryForm() {
  const [name, setName] = useState("");
  const [company, setCompany] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [source, setSource] = useState("");
  const [message, setMessage] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    console.log({ name, company, email, phone, source, message });
  }

  return (
    <main>
      <h1>Contact Brightline</h1>

      <form onSubmit={handleSubmit}>
        <label>
          Full name
          <input
            type="text"
            name="name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
            minLength={3}
            maxLength={100}
          />
        </label>

        <label>
          Company
          <input
            type="text"
            name="company"
            value={company}
            onChange={(event) => setCompany(event.target.value)}
            required
            maxLength={100}
          />
        </label>

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

        <label>
          Phone number
          <input
            type="tel"
            name="phone"
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
          />
        </label>

        <label>
          How did you hear about us?
          <select
            name="source"
            value={source}
            onChange={(event) => setSource(event.target.value)}
            required
          >
            <option value="">Please select</option>
            <option value="google">Google</option>
            <option value="referral">Referral</option>
            <option value="social_media">Social media</option>
            <option value="other">Other</option>
          </select>
        </label>

        <label>
          Message
          <textarea
            name="message"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            required
            maxLength={2000}
            rows={6}
          />
        </label>
        <p>{message.length}/2000</p>

        <button type="submit">Send enquiry</button>
      </form>
    </main>
  );
}