"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { apiFetch } from "@/lib/api/client";
import { useAuthStore } from "@/stores/auth-store";

export default function RegisterPage() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();
  setError("");

  const form = new FormData(event.currentTarget);

  const payload = {
    full_name: form.get("full_name"),
    email: form.get("email"),
    password: form.get("password"),
  };

  console.log("REGISTER PAYLOAD:", payload);

  try {
    const result = await apiFetch<{
      access_token: string;
      user: any;
    }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    console.log("REGISTER SUCCESS:", result);

    setAuth(result.access_token, result.user);
    router.push("/dashboard");
  } catch (err) {
    console.error("REGISTER ERROR:", err);
    setError("Could not create account. Try a different email.");
  }
}

  return (
    <main className="grid min-h-screen place-items-center bg-slate-50 p-4">
      <Card className="w-full max-w-md">
        <h1 className="text-2xl font-semibold">Create your account</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Start building your job readiness profile.
        </p>
        <form className="mt-6 space-y-4" onSubmit={onSubmit}>
          <Input name="full_name" placeholder="Full name" required />
          <Input name="email" type="email" placeholder="Email" required />
          <Input
            name="password"
            type="password"
            placeholder="Password, minimum 8 characters"
            minLength={8}
            required
          />
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          <Button className="w-full" type="submit">
            Create account
          </Button>
        </form>
        <p className="mt-4 text-sm text-muted-foreground">
          Already registered?{" "}
          <Link className="font-medium text-teal-700" href="/auth/login">
            Sign in
          </Link>
        </p>
      </Card>
    </main>
  );
}
