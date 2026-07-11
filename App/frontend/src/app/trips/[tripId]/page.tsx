"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { IdeasPanel } from "@/components/IdeasPanel";
import {
  ApiError,
  TripDetail,
  TripStop,
  Tripmate,
  TripmateRole,
  Traveler,
  api,
  isLoggedIn,
} from "@/lib/api";

type Tab = "ideas" | "schedule" | "expenses" | "mates" | "stops";

const TABS: { id: Tab; label: string }[] = [
  { id: "ideas", label: "Ideas" },
  { id: "schedule", label: "Schedule" },
  { id: "expenses", label: "Expenses" },
  { id: "stops", label: "Stops" },
  { id: "mates", label: "Mates" },
];

export default function TripHubPage() {
  const params = useParams<{ tripId: string }>();
  const tripId = params.tripId;
  const router = useRouter();

  const [tab, setTab] = useState<Tab>("ideas");
  const [me, setMe] = useState<Traveler | null>(null);
  const [trip, setTrip] = useState<TripDetail | null>(null);
  const [stops, setStops] = useState<TripStop[]>([]);
  const [mates, setMates] = useState<Tripmate[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<TripmateRole>("contributor");
  const [lastInviteToken, setLastInviteToken] = useState<string | null>(null);
  const [stopName, setStopName] = useState("");

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/login");
      return;
    }

    async function load() {
      try {
        const [traveler, tripDetail, stopList, mateList] = await Promise.all([
          api.me(),
          api.getTrip(tripId),
          api.listStops(tripId),
          api.listTripmates(tripId),
        ]);
        setMe(traveler);
        setTrip(tripDetail);
        setStops(stopList);
        setMates(mateList);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          router.replace("/login");
          return;
        }
        setError(err instanceof ApiError ? err.detail : "Failed to load trip");
      }
    }

    load();
  }, [router, tripId]);

  async function invite(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLastInviteToken(null);
    try {
      const res = await api.inviteTripmate(tripId, {
        email: inviteEmail,
        role: inviteRole,
      });
      setLastInviteToken(res.invite_token);
      setInviteEmail("");
      setMates(await api.listTripmates(tripId));
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Invite failed");
    }
  }

  async function addStop(e: FormEvent) {
    e.preventDefault();
    if (!stopName.trim()) return;
    setError(null);
    try {
      await api.createStop(tripId, { location_name: stopName.trim() });
      setStopName("");
      setStops(await api.listStops(tripId));
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Could not add stop");
    }
  }

  const isAdmin = trip?.my_role === "administrator";

  return (
    <div className="min-h-screen">
      <AppHeader email={me?.email} />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <div className="mb-4">
          <Link href="/trips" className="text-sm text-teal-700 hover:underline">
            ← All trips
          </Link>
        </div>

        {trip ? (
          <div className="mb-6">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h1 className="text-2xl font-semibold text-slate-900">{trip.name}</h1>
                {trip.description ? (
                  <p className="mt-1 text-sm text-slate-500">{trip.description}</p>
                ) : null}
                <p className="mt-2 text-xs text-slate-400">
                  {trip.start_date || "No start"} → {trip.end_date || "No end"} · Your role:{" "}
                  <span className="capitalize">{trip.my_role}</span>
                </p>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-slate-500">Loading trip…</p>
        )}

        <nav className="flex flex-wrap gap-1 border-b border-slate-200">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setTab(t.id)}
              className={`rounded-t-md px-3 py-2 text-sm font-medium ${
                tab === t.id
                  ? "border border-b-white border-slate-200 bg-white text-teal-800"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>

        <section className="rounded-b-xl rounded-tr-xl border border-t-0 border-slate-200 bg-white p-6 shadow-sm">
          {error ? <p className="mb-4 text-sm text-red-600">{error}</p> : null}

          {tab === "ideas" && me && trip ? (
            <IdeasPanel tripId={tripId} myRole={trip.my_role} myTravelerId={me.id} />
          ) : null}

          {tab === "schedule" && (
            <Placeholder
              title="Schedule"
              body="Combined and personal schedule views, travel legs, and plan-from-idea come in Phase 3."
            />
          )}

          {tab === "expenses" && (
            <Placeholder
              title="Expenses"
              body="Shared expenses, splits, and settlement status come in Phase 4. Payout handles live on Traveler profiles."
            />
          )}

          {tab === "stops" && (
            <div className="space-y-4">
              <h2 className="font-medium text-slate-900">Trip stops</h2>
              {isAdmin ? (
                <form onSubmit={addStop} className="flex max-w-md gap-2">
                  <input
                    value={stopName}
                    onChange={(e) => setStopName(e.target.value)}
                    placeholder="City or region"
                    className="flex-1 rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-teal-600"
                  />
                  <button
                    type="submit"
                    className="rounded-md bg-teal-700 px-3 py-2 text-sm font-medium text-white hover:bg-teal-800"
                  >
                    Add stop
                  </button>
                </form>
              ) : null}
              {stops.length === 0 ? (
                <p className="text-sm text-slate-500">No stops yet.</p>
              ) : (
                <ul className="divide-y divide-slate-100 rounded-lg border border-slate-200">
                  {stops.map((s) => (
                    <li key={s.id} className="flex items-center justify-between px-3 py-2 text-sm">
                      <span>{s.location_name}</span>
                      <span className="text-xs text-slate-400">#{s.sort_order}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {tab === "mates" && (
            <div className="space-y-6">
              <div>
                <h2 className="font-medium text-slate-900">TripMates</h2>
                <ul className="mt-3 divide-y divide-slate-100 rounded-lg border border-slate-200">
                  {mates.map((m) => (
                    <li key={m.id} className="flex items-center justify-between gap-3 px-3 py-2 text-sm">
                      <div>
                        <div className="font-medium text-slate-800">
                          {m.traveler_display || m.invite_email || "Unknown"}
                        </div>
                        <div className="text-xs text-slate-400">{m.invite_status}</div>
                      </div>
                      <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs capitalize text-slate-600">
                        {m.role}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              {isAdmin ? (
                <div>
                  <h3 className="text-sm font-medium text-slate-900">Invite TripMate</h3>
                  <form onSubmit={invite} className="mt-2 flex flex-col gap-2 sm:flex-row">
                    <input
                      type="email"
                      required
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      placeholder="email@example.com"
                      className="flex-1 rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-teal-600"
                    />
                    <select
                      value={inviteRole}
                      onChange={(e) => setInviteRole(e.target.value as TripmateRole)}
                      className="rounded-md border border-slate-300 px-3 py-2"
                    >
                      <option value="viewer">Viewer</option>
                      <option value="commenter">Commenter</option>
                      <option value="contributor">Contributor</option>
                      <option value="administrator">Administrator</option>
                    </select>
                    <button
                      type="submit"
                      className="rounded-md bg-teal-700 px-3 py-2 text-sm font-medium text-white hover:bg-teal-800"
                    >
                      Invite
                    </button>
                  </form>
                  {lastInviteToken ? (
                    <p className="mt-2 break-all text-xs text-slate-500">
                      Invite token (dev): <code>{lastInviteToken}</code>
                      <br />
                      Accept via <code>POST /api/v1/invites/{lastInviteToken}/accept</code> while logged
                      in as the invitee.
                    </p>
                  ) : null}
                </div>
              ) : null}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function Placeholder({ title, body }: { title: string; body: string }) {
  return (
    <div>
      <h2 className="font-medium text-slate-900">{title}</h2>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">{body}</p>
    </div>
  );
}
