"use client";

import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";
import { apiFetch } from "@/lib/api/client";
import { Clock, Trophy, Target, BookOpen, UserCircle, Briefcase } from "lucide-react";

const metrics = [
  { key: "ats_score", label: "Resume ATS Score", icon: UserCircle, color: "bg-emerald-500", track: "bg-emerald-100" },
  { key: "skill_score", label: "Skill Readiness", icon: BookOpen, color: "bg-blue-500", track: "bg-blue-100" },
  { key: "job_match_score", label: "Job Compatibility", icon: Target, color: "bg-indigo-500", track: "bg-indigo-100" },
  { key: "interview_score", label: "Mock Interviews", icon: Briefcase, color: "bg-purple-500", track: "bg-purple-100" }
];

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: () => apiFetch<Record<string, any>>("/dashboard/summary")
  });

  return (
    <>
      <PageHeader title="Command Center" description="Track your AI readiness signals and learning progress." />
      
      {isLoading ? <div className="text-muted-foreground p-4">Loading dashboard...</div> : null}
      
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <Card className="p-6 md:col-span-2 border-l-4 border-l-teal-500 shadow-sm flex flex-col justify-center">
          <div className="flex items-center gap-2 mb-2">
            <Trophy className="h-5 w-5 text-teal-600" />
            <h3 className="font-semibold text-slate-700">Overall Placement Readiness</h3>
          </div>
          <p className="mt-2 text-5xl font-bold text-slate-800">{data?.overall_readiness_score ?? 0}<span className="text-3xl text-slate-500">%</span></p>
          <div className="mt-4 h-3 rounded-full bg-slate-100">
            <div className="h-3 rounded-full bg-teal-600 transition-all duration-1000" style={{ width: `${Math.min(100, Number(data?.overall_readiness_score ?? 0))}%` }} />
          </div>
          <p className="text-xs text-slate-500 mt-2">Based on your resume, matched jobs, and mock interview performance.</p>
        </Card>

        {/* MOCKED LEARNING TIME AS REQUESTED BY USER */}
        <Card className="p-6 border-l-4 border-l-amber-500 shadow-sm flex flex-col justify-center bg-gradient-to-br from-amber-50 to-white">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-5 w-5 text-amber-600" />
            <h3 className="font-semibold text-slate-700">Time Spent Learning</h3>
          </div>
          <p className="mt-2 text-4xl font-bold text-slate-800">{data?.learning_hours ?? 0}<span className="text-2xl text-slate-500 font-medium">h</span> {data?.learning_minutes ?? 0}<span className="text-2xl text-slate-500 font-medium">m</span></p>
          <p className="text-sm text-slate-600 mt-1 font-medium">Based on your platform activity</p>
          <p className="text-xs text-slate-500 mt-4">Keep grinding your AI roadmap courses to hit your 20h weekly goal!</p>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-4 mb-8">
        {metrics.map(({ key, label, icon: Icon, color, track }) => (
          <Card key={key} className="p-5 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm font-medium text-slate-600">{label}</p>
              <Icon className={`h-5 w-5 ${color.replace('bg-', 'text-')}`} />
            </div>
            <p className="text-3xl font-bold text-slate-800 mb-4">{data?.[key] ?? 0}%</p>
            <div className={`h-2 rounded-full ${track}`}>
              <div className={`h-2 rounded-full ${color}`} style={{ width: `${Math.min(100, Number(data?.[key] ?? 0))}%` }} />
            </div>
          </Card>
        ))}
      </div>

      <Card className="p-6 shadow-sm">
        <h3 className="font-semibold text-slate-800 text-lg mb-4">Recommended Next Actions</h3>
        <div className="grid gap-3 md:grid-cols-3">
          {(data?.next_actions ?? ["Upload a resume", "Generate your roadmap", "Take a mock interview"]).map((action: string, i: number) => (
            <div className="rounded-lg border bg-slate-50 p-4 text-sm font-medium text-indigo-900 flex items-start gap-3 hover:bg-slate-100 transition-colors" key={i}>
              <div className="bg-indigo-100 text-indigo-600 rounded-full w-6 h-6 flex items-center justify-center shrink-0">
                {i + 1}
              </div>
              {action}
            </div>
          ))}
        </div>
      </Card>
    </>
  );
}
