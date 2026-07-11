"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { clearTokens } from "@/lib/api";

export function AppHeader({ email }: { email?: string | null }) {
  const router = useRouter();

  function logout() {
    clearTokens();
    router.replace("/login");
  }

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link href="/trips" className="text-lg font-semibold tracking-tight text-teal-700">
          Trippy
        </Link>
        <div className="flex items-center gap-4 text-sm text-slate-600">
          {email ? <span className="hidden sm:inline">{email}</span> : null}
          <button
            type="button"
            onClick={logout}
            className="rounded-md border border-slate-200 px-3 py-1.5 hover:bg-slate-50"
          >
            Log out
          </button>
        </div>
      </div>
    </header>
  );
}
