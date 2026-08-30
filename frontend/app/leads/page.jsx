"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';


export default function LeadsPage() {
    const router = useRouter();
    const [leads, setLeads] = useState(null);

    useEffect(() => {
        async function loadLeads() {
            try {
                const response = await fetch(
                    `${process.env.NEXT_PUBLIC_API_URL}/leads`,
                    { credentials: 'include' }
                ); 

                if (response.status === 401) {
                    router.replace('/login');
                    return;
                }

                if (!response.ok) {
                    throw new Error('Failed to load leads');
                }

                setLeads(await response.json());
            } catch (error) {
                console.error(error);
                alert('Failed to load leads');
            }
        }

        loadLeads();
    }, [router]);

    if (leads === null) return <p>Loading...</p>;
    if (leads.length === 0) return <p>No leads yet...</p>;
    
    return <div>Leads loaded</div>;
}

