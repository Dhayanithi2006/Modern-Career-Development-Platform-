"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { Briefcase, FileText, LayoutDashboard, Map, MessageSquare, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";

const items = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/resume", label: "Resume", icon: FileText },
  { href: "/jobs", label: "Jobs", icon: Search },
  { href: "/roadmap", label: "Roadmap", icon: Map },
  { href: "/assistant", label: "Assistant", icon: MessageSquare },
  { href: "/interview", label: "Interview", icon: Briefcase }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const token = useAuthStore((state) => state.accessToken);
  const logout = useAuthStore((state) => state.logout);

  useEffect(() => {
    if (!token) {
      router.replace("/auth/login");
    }
  }, [router, token]);

  return (
    <div className="min-h-screen bg-slate-50">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r bg-white p-4 md:block">
        <div className="mb-8">
          <p className="text-lg font-semibold">AI Career Copilot</p>
          <p className="text-sm text-muted-foreground">Placement readiness</p>
        </div>
        <nav className="space-y-1">
          {items.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-slate-700",
                  pathname === item.href && "bg-teal-50 text-teal-800"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="md:pl-64">
        <header className="flex h-16 items-center justify-between border-b bg-white px-5">
          <div>
            <p className="text-sm text-muted-foreground">Student Workspace</p>
            <h1 className="font-semibold">Career readiness command center</h1>
          </div>
          <Button
            variant="secondary"
            onClick={() => {
              logout();
              router.push("/auth/login");
            }}
          >
            Sign out
          </Button>
        </header>
        <div className="p-5">{children}</div>
      </main>
    </div>
  );
}
