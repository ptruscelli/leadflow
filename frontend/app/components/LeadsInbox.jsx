"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

const STATUSES = ["new", "contacted", "qualified", "closed"];
const PAGE_SIZE = 10;

function formatStatus(status) {
  return status.charAt(0).toUpperCase() + status.slice(1);
}

function formatSource(source) {
  const labels = {
    google: "Google",
    referral: "Referral",
    social_media: "Social media",
    other: "Other",
  };
  return labels[source] ?? source;
}

function formatDateTime(iso) {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function LeadsInbox() {
  const router = useRouter();
  const [deleted, setDeleted] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");
  const [q, setQ] = useState("");
  const [qDebounced, setQDebounced] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [leads, setLeads] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [isAddingNote, setIsAddingNote] = useState(false);
  const [noteDraft, setNoteDraft] = useState("");
  const noteFieldRef = useRef(null);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setQDebounced(q.trim());
      setPage(1);
    }, 150);

    return () => clearTimeout(timeoutId);
  }, [q]);

  useEffect(() => {
    let cancelled = false;

    async function loadLeads() {
      setExpandedId(null);
      setIsAddingNote(false);
      setNoteDraft("");

      try {
        const params = new URLSearchParams({
          deleted: String(deleted),
          page: String(page),
          page_size: String(PAGE_SIZE),
        });
        if (qDebounced) {
          params.set("q", qDebounced);
        }
        if (statusFilter) {
          params.set("status", statusFilter);
        }

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/leads?${params}`,
          { credentials: "include" }
        );

        if (response.status === 401) {
          router.replace("/login");
          return;
        }

        if (!response.ok) {
          throw new Error("Failed to load leads");
        }

        const data = await response.json();
        if (!Array.isArray(data.leads)) {
          throw new Error("Failed to load leads");
        }
        if (!cancelled) {
          setLeads(data.leads);
          setTotalPages(data.total_pages ?? 0);
        }
      } catch (error) {
        console.error(error);
        if (!cancelled) {
          setLeads([]);
          setTotalPages(0);
          alert("Failed to load leads");
        }
      }
    }

    loadLeads();

    return () => {
      cancelled = true;
    };
  }, [deleted, page, qDebounced, statusFilter, router]);

  useEffect(() => {
    const field = noteFieldRef.current;
    if (!field) {
      return;
    }

    field.style.height = "auto";
    field.style.height = `${field.scrollHeight}px`;
  }, [noteDraft, isAddingNote]);

  function tabClass(isActive) {
    return `cursor-pointer border-b-2 px-1 pb-2 text-sm ${
      isActive
        ? "border-slate-900 font-medium text-slate-900"
        : "border-transparent text-slate-600 hover:text-slate-900"
    }`;
  }

  async function updateStatus(leadId, status) {
    const previous = leads;
    const previousPage = page;
    const leavesFilter = Boolean(statusFilter) && status !== statusFilter;
    const remaining = leavesFilter
      ? leads.filter((lead) => lead.id !== leadId)
      : leads.map((lead) =>
          lead.id === leadId ? { ...lead, status } : lead
        );

    setLeads(remaining);
    if (remaining.length === 0 && page > 1) {
      setPage((currentPage) => currentPage - 1);
    }
    if (leavesFilter && expandedId === leadId) {
      setExpandedId(null);
      setIsAddingNote(false);
      setNoteDraft("");
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/leads/${leadId}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ status }),
        }
      );

      if (response.status === 401) {
        router.replace("/login");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to update status");
      }

      const updated = await response.json();
      setLeads((current) =>
        current.map((lead) => (lead.id === updated.id ? updated : lead))
      );
    } catch (error) {
      console.error(error);
      setLeads(previous);
      setPage(previousPage);
      alert("Failed to update status");
    }
  }

  async function saveNote(leadId, note) {
    const previous = leads;
    const nextNote = note.trim() || null;

    setLeads((current) =>
      current.map((lead) =>
        lead.id === leadId ? { ...lead, note: nextNote } : lead
      )
    );

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/leads/${leadId}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ note: nextNote ?? "" }),
        }
      );

      if (response.status === 401) {
        router.replace("/login");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to save note");
      }

      const updated = await response.json();
      setLeads((current) =>
        current.map((lead) => (lead.id === updated.id ? updated : lead))
      );
    } catch (error) {
      console.error(error);
      setLeads(previous);
      alert("Failed to save note");
    }
  }

  async function deleteLead(leadId) {
    const previous = leads;
    const previousPage = page;
    const remaining = leads.filter((lead) => lead.id !== leadId);
    setLeads(remaining);
    if (remaining.length === 0 && page > 1) {
      setPage((currentPage) => currentPage - 1);
    }
    if (expandedId === leadId) {
      setExpandedId(null);
      setIsAddingNote(false);
      setNoteDraft("");
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/leads/${leadId}`,
        {
          method: "DELETE",
          credentials: "include",
        }
      );

      if (response.status === 401) {
        router.replace("/login");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to delete lead");
      }
    } catch (error) {
      console.error(error);
      setLeads(previous);
      setPage(previousPage);
      alert("Failed to delete lead");
    }
  }

  function toggleExpanded(lead) {
    const isOpen = expandedId === lead.id;
    if (isOpen) {
      setExpandedId(null);
      setIsAddingNote(false);
      setNoteDraft("");
      return;
    }

    setExpandedId(lead.id);
    setIsAddingNote(Boolean(lead.note));
    setNoteDraft(lead.note ?? "");
  }

  return (
    <main className="mx-auto w-full max-w-4xl">
      <div className="mb-4 flex gap-6 border-b border-slate-200">
        <button
          type="button"
          onClick={() => {
            setDeleted(false);
            setPage(1);
            setLeads(null);
          }}
          className={tabClass(!deleted)}
        >
          Leads
        </button>
        <button
          type="button"
          onClick={() => {
            setDeleted(true);
            setPage(1);
            setLeads(null);
          }}
          className={tabClass(deleted)}
        >
          Archive
        </button>
      </div>

      <div className="mb-2 flex items-center justify-between gap-4">
        <input
          type="search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search name, email, phone, company"
          className="w-1/3 rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-slate-400 focus:ring-0"
        />
        <label className="flex items-center gap-2 text-xs text-slate-600">
          Status
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
              setLeads(null);
            }}
            className="rounded-md border border-slate-200 bg-white px-2 py-1 text-xs text-slate-900 outline-none focus:border-slate-400 focus:ring-0"
          >
            <option value="">All</option>
            {STATUSES.map((status) => (
              <option key={status} value={status}>
                {formatStatus(status)}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="overflow-hidden rounded-md border border-slate-200 bg-white">
        {leads === null ? (
          <p className="px-4 py-8 text-center text-sm text-slate-500">
            Loading...
          </p>
        ) : leads.length === 0 ? (
          <p className="px-4 py-8 text-center text-sm text-slate-500">
            {q.trim() || statusFilter
              ? "No matching leads."
              : deleted
                ? "No deleted leads."
                : "No leads yet."}
          </p>
        ) : (
          <ul>
            {leads.map((lead) => {
              const isExpanded = expandedId === lead.id;

              return (
                <li
                  key={lead.id}
                  className="border-b border-slate-100 last:border-b-0"
                >
                  <div className="relative flex flex-wrap items-center gap-x-4 gap-y-1 px-4 py-3 hover:bg-slate-50">
                    <button
                      type="button"
                      aria-expanded={isExpanded}
                      aria-label={`View enquiry from ${lead.name}`}
                      onClick={() => toggleExpanded(lead)}
                      className="absolute inset-0 cursor-pointer"
                    />
                    <span className="pointer-events-none relative w-40 shrink-0 truncate text-sm font-medium">
                      {lead.name}
                    </span>
                    <span className="pointer-events-none relative min-w-0 flex-1 truncate text-sm text-slate-600">
                      {lead.company}
                    </span>
                    <span className="relative z-10 inline-grid shrink-0">
                      <select
                        value={lead.status}
                        disabled={deleted}
                        onChange={(event) =>
                          updateStatus(lead.id, event.target.value)
                        }
                        className="col-start-1 row-start-1 w-full cursor-pointer appearance-none rounded-md border border-slate-200 bg-slate-100 px-2 py-1 text-center text-xs font-medium text-slate-700 hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        {STATUSES.map((status) => (
                          <option key={status} value={status}>
                            {formatStatus(status)}
                          </option>
                        ))}
                      </select>
                      <span
                        aria-hidden
                        className="invisible col-start-1 row-start-1 whitespace-nowrap border border-transparent px-2 py-1 text-center text-xs font-medium"
                      >
                        {formatStatus(lead.status)}
                      </span>
                    </span>
                    <span className="pointer-events-none relative ml-auto shrink-0 text-xs text-slate-500">
                      Last updated: {formatDateTime(lead.updated_at)}
                    </span>
                    {!deleted && (
                      <button
                        type="button"
                        onClick={() => deleteLead(lead.id)}
                        className="relative z-10 shrink-0 cursor-pointer text-xs font-normal text-slate-500 hover:text-red-700"
                      >
                        Delete
                      </button>
                    )}
                  </div>

                  {isExpanded && (
                    <div className="space-y-3 border-t border-slate-100 bg-slate-50 px-4 py-4 text-sm">
                      <p>
                        <span className="text-slate-500">Email: </span>
                        {lead.email}
                      </p>
                      {lead.phone && (
                        <p>
                          <span className="text-slate-500">Phone: </span>
                          {lead.phone}
                        </p>
                      )}
                      <p>
                        <span className="text-slate-500">Source: </span>
                        {formatSource(lead.source)}
                      </p>
                      <p>
                        <span className="text-slate-500">Received: </span>
                        {formatDateTime(lead.created_at)}
                      </p>
                      <p className="whitespace-pre-wrap text-slate-800">
                        {lead.message}
                      </p>
                      {isAddingNote ? (
                        <label className="flex flex-col gap-1">
                          <span className="text-slate-500">Notes:</span>
                          <textarea
                            ref={noteFieldRef}
                            value={noteDraft}
                            onChange={(event) =>
                              setNoteDraft(event.target.value)
                            }
                            onBlur={() => {
                              if ((lead.note ?? "") !== noteDraft) {
                                saveNote(lead.id, noteDraft);
                              }
                            }}
                            onKeyDown={(event) => {
                              if (event.key === "Enter" && !event.shiftKey) {
                                event.preventDefault();
                                event.target.blur();
                              }
                            }}
                            rows={1}
                            className="w-full resize-none overflow-hidden border-0 bg-transparent p-0 text-sm leading-5 text-slate-800 outline-none"
                          />
                        </label>
                      ) : (
                        !deleted && (
                          <button
                            type="button"
                            onClick={() => {
                              setNoteDraft(lead.note ?? "");
                              setIsAddingNote(true);
                            }}
                            className="cursor-pointer text-xs font-normal text-slate-500 hover:text-slate-900"
                          >
                            Add a note
                          </button>
                        )
                      )}
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {leads !== null && totalPages > 0 && (
        <nav
          aria-label="Lead pages"
          className="mt-4 flex items-center justify-center gap-3 text-xs text-slate-600"
        >
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => setPage((current) => current - 1)}
            className="cursor-pointer disabled:cursor-default disabled:opacity-40"
          >
            Previous
          </button>
          <span>
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            disabled={page >= totalPages}
            onClick={() => setPage((current) => current + 1)}
            className="cursor-pointer disabled:cursor-default disabled:opacity-40"
          >
            Next
          </button>
        </nav>
      )}
    </main>
  );
}
