"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { apiFetch } from "@/lib/api/client";
import { useAuthStore } from "@/stores/auth-store";

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      const result = await apiFetch<{ access_token: string; user: any }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: form.get("email"),
          password: form.get("password")
        })
      });
      setAuth(result.access_token, result.user);
      router.push("/dashboard");
    } catch {
      setError("Invalid email or password.");
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-slate-50 p-4">
      <Card className="w-full max-w-md">
        <h1 className="text-2xl font-semibold">Welcome back</h1>
        <p className="mt-1 text-sm text-muted-foreground">Sign in to continue your placement preparation.</p>
        <form className="mt-6 space-y-4" onSubmit={onSubmit}>
          <Input name="email" type="email" placeholder="Email" required />
          <Input name="password" type="password" placeholder="Password" required />
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          <Button className="w-full" type="submit">Sign in</Button>
        </form>
        <p className="mt-4 text-sm text-muted-foreground">
          New here? <Link className="font-medium text-teal-700" href="/auth/register">Create an account</Link>
        </p>
      </Card>
    </main>
  );
}
