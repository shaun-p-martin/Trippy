"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { ApiError, TripSummary, Traveler, api, isLoggedIn } from "@/lib/api";

export default function TripsPage() {
  const router = useRouter();
  const [me, setMe] = useState<Traveler | null>(null);
  const [trips, setTrips] = useState<TripSummary[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/login");
      return;
    }

    async function load() {
      try {
        const [traveler, tripList] = await Promise.all([api.me(), api.listTrips()]);
        setMe(traveler);
        setTrips(tripList);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          router.replace("/login");
          return;
        }
        setError(err instanceof ApiError ? err.detail : "Failed to load trips");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [router]);

  async function createTrip(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setError(null);
    try {
      const trip = await api.createTrip({ name: name.trim() });
      router.push(`/trips/${trip.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Could not create trip");
    }
  }

  return (
    <div className="min-h-screen">
      <AppHeader email={me?.email} />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">Your trips</h1>
            <p className="mt-1 text-sm text-slate-500">
              Create a trip to invite TripMates and plan together.
            </p>
          </div>
          <form onSubmit={createTrip} className="flex w-full max-w-md gap-2">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Trip name"
              className="flex-1 rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-teal-600"
            />
            <button
              type="submit"
              className="rounded-md bg-teal-700 px-4 py-2 text-sm font-medium text-white hover:bg-teal-800"
            >
              Create
            </button>
          </form>
        </div>

        {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}

        {loading ? (
          <p className="mt-8 text-slate-500">Loading trips…</p>
        ) : trips.length === 0 ? (
          <div className="mt-8 rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">
            No trips yet. Create one to get started.
          </div>
        ) : (
          <ul className="mt-8 grid gap-3">
            {trips.map((trip) => (
              <li key={trip.id}>
                <Link
                  href={`/trips/${trip.id}`}
                  className="block rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-teal-300"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h2 className="font-medium text-slate-900">{trip.name}</h2>
                      {trip.description ? (
                        <p className="mt-1 text-sm text-slate-500 line-clamp-2">{trip.description}</p>
                      ) : null}
                      <p className="mt-2 text-xs text-slate-400">
                        {trip.start_date || "No start"} → {trip.end_date || "No end"}
                      </p>
                    </div>
                    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium capitalize text-slate-600">
                      {trip.my_role}
                    </span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}
