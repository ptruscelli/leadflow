'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
    const router = useRouter();
    const started = useRef(false);
    const [status, setStatus] = useState('signing-in');

    useEffect(() => {
        if (started.current) return;
        started.current = true;

        const raw_token = new URLSearchParams(window.location.search).get('token');

        if (!raw_token) {
            setStatus("error");
            return;
        }

        async function login() {
            try {
                const response = await fetch(
                    `${process.env.NEXT_PUBLIC_API_URL}/auth/login`,
                    {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        credentials: 'include',
                        body: JSON.stringify({ raw_token: raw_token }),
                    }
                );

                if (!response.ok) {
                    setStatus("error");
                    return;
                }

                router.replace("/leads");
            } catch (error) {
                setStatus("error");
                console.error("Login failed:", error);
            }
        }

        login();
    }, [router]);

    if (status === "error") {
        return <p>This login link is invalid or has expired.</p>;
    }

    return <p>Signing in...</p>;
}
