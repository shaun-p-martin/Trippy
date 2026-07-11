"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, api, setTokens } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await api.register({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
      });
      setTokens(tokens);
      router.replace("/trips");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold text-slate-900">Create your account</h1>
        <p className="mt-1 text-sm text-slate-500">Start planning group trips as a Traveler.</p>

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <label className="block text-sm">
              <span className="mb-1 block text-slate-700">First name</span>
              <input
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-teal-600"
              />
            </label>
            <label className="block text-sm">
              <span className="mb-1 block text-slate-700">Last name</span>
              <input
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-teal-600"
              />
            </label>
          </div>
          <label className="block text-sm">
            <span className="mb-1 block text-slate-700">Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-teal-600"
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1 block text-slate-700">Password</span>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-teal-600"
            />
          </label>
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-teal-700 px-3 py-2 font-medium text-white hover:bg-teal-800 disabled:opacity-60"
          >
            {loading ? "Creating…" : "Create account"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-600">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-teal-700 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  );
}
