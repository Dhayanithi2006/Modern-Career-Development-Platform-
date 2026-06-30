"use client";

import { FormEvent, useState } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/layout/page-header";
import { apiFetch } from "@/lib/api/client";

export default function AssistantPage() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const content = String(form.get("content") ?? "");
    setMessages((current) => [...current, { role: "You", content }]);
    const result = await apiFetch<{ reply: string }>("/assistant/sessions/1/messages", {
      method: "POST",
      body: JSON.stringify({ content })
    });
    setMessages((current) => [...current, { role: "Copilot", content: result.reply }]);
    event.currentTarget.reset();
  }

  return (
    <>
      <PageHeader title="AI Career Assistant" description="Ask questions grounded in your profile, resume, jobs, and roadmap." />
      <Card className="min-h-96">
        <div className="space-y-3">
          {messages.map((message, index) => (
            <div key={`${message.role}-${index}`} className="rounded-md border bg-slate-50 p-3">
              <p className="text-xs font-medium text-muted-foreground">{message.role}</p>
              <p className="mt-1 text-sm">{message.content}</p>
            </div>
          ))}
        </div>
        <form className="mt-4 flex gap-2" onSubmit={onSubmit}>
          <Input name="content" placeholder="Ask how to improve your readiness..." required />
          <Button type="submit"><Send className="h-4 w-4" /></Button>
        </form>
      </Card>
    </>
  );
}
