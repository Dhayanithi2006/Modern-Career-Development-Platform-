"use client";

import { FormEvent, useState } from "react";
import { Map, Zap, CheckCircle2, BookOpen, Presentation, Calendar, BriefcaseBusiness, Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/layout/page-header";
import { apiFetch } from "@/lib/api/client";
import { Badge } from "@/components/ui/badge";

export default function RoadmapPage() {
  const [roadmap, setRoadmap] = useState<any>(null);
  const [gap, setGap] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsGenerating(true);
    const form = new FormData(event.currentTarget);
    const targetRole = String(form.get("target_role"));
    
    try {
      const gapResult = await apiFetch("/skill-gap/analyze", {
        method: "POST",
        body: JSON.stringify({ target_role: targetRole })
      });
      setGap(gapResult);
      
      const result = await apiFetch("/roadmaps/generate", {
        method: "POST",
        body: JSON.stringify({
          target_role: targetRole,
          duration_weeks: Number(form.get("duration_weeks"))
        })
      });
      setRoadmap(result);
    } catch (e) {
      console.error(e);
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <>
      <PageHeader title="AI Roadmap Generator" description="Generate a role-specific week-by-week plan from your skill gaps." />
      
      <Card className="mb-6 p-5">
        <form className="grid gap-3 md:grid-cols-[1fr_160px_auto]" onSubmit={onSubmit}>
          <Input name="target_role" placeholder="Target role, e.g. Frontend Developer" required />
          <Input name="duration_weeks" type="number" defaultValue={4} min={1} max={52} />
          <Button type="submit" variant="primary" disabled={isGenerating}>
            <Map className="mr-2 h-4 w-4" /> {isGenerating ? "Generating..." : "Generate Plan"}
          </Button>
        </form>
      </Card>

      {/* USER REQUESTED TEXT BANNER */}
      {gap && gap.missing_skills?.length > 0 && (
        <div className="mb-6 bg-gradient-to-r from-emerald-500 to-teal-600 text-white p-4 rounded-xl shadow-sm flex items-start gap-3">
          <Zap className="h-6 w-6 mt-1 shrink-0 text-yellow-300 fill-yellow-300" />
          <div>
            <h3 className="font-bold text-lg">AI Hiring Insight</h3>
            <p className="opacity-90 mt-1 font-medium">
              If you learn {gap.missing_skills.slice(0, 2).join(" and ")}{gap.missing_skills.length > 2 ? ` and a few other missing tools` : ''}, you will get hired soon! Focus on these core gaps to drastically boost your ATS score.
            </p>
          </div>
        </div>
      )}

      {roadmap && roadmap.content?.weeks && (
        <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
          {roadmap.content.weeks.map((weekData: any, idx: number) => (
            <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
              <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-white bg-indigo-600 text-white font-bold shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                {weekData.week || (idx + 1)}
              </div>
              
              <Card className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-5 hover:shadow-md transition-shadow">
                <h3 className="text-xl font-bold text-slate-800 mb-4">{weekData.learning_goals || `Week ${idx + 1} Goals`}</h3>
                
                {weekData.courses && weekData.courses.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-slate-500 flex items-center gap-1 mb-2"><BookOpen className="h-4 w-4" /> Recommended Courses</h4>
                    <ul className="text-sm text-slate-700 list-disc pl-5 space-y-1">
                      {weekData.courses.map((c: string, i: number) => <li key={i}>{c}</li>)}
                    </ul>
                  </div>
                )}

                {weekData.projects && weekData.projects.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-slate-500 flex items-center gap-1 mb-2"><BriefcaseBusiness className="h-4 w-4" /> Projects to Build</h4>
                    <ul className="text-sm text-slate-700 list-disc pl-5 space-y-1">
                      {weekData.projects.map((c: string, i: number) => <li key={i}>{c}</li>)}
                    </ul>
                  </div>
                )}

                {weekData.practice_websites && weekData.practice_websites.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-slate-500 flex items-center gap-1 mb-2"><Globe className="h-4 w-4" /> Where to Practice</h4>
                    <div className="flex flex-wrap gap-2">
                      {weekData.practice_websites.map((c: string, i: number) => <Badge key={i} variant="secondary">{c}</Badge>)}
                    </div>
                  </div>
                )}

                {weekData.interview_preparation && weekData.interview_preparation.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-slate-500 flex items-center gap-1 mb-2"><Presentation className="h-4 w-4" /> Interview Prep</h4>
                    <ul className="text-sm text-slate-700 list-disc pl-5 space-y-1">
                      {weekData.interview_preparation.map((c: string, i: number) => <li key={i}>{c}</li>)}
                    </ul>
                  </div>
                )}
              </Card>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
