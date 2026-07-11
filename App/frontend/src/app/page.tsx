"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isLoggedIn } from "@/lib/api";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    router.replace(isLoggedIn() ? "/trips" : "/login");
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center text-slate-500">
      Loading…
    </main>
  );
}
