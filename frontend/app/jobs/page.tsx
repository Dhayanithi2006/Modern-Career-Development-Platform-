"use client";

import { useQuery } from "@tanstack/react-query";
import { Search, Briefcase, Building2, MapPin, CheckCircle, AlertTriangle } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/layout/page-header";
import { apiFetch } from "@/lib/api/client";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

export default function JobsPage() {
  const [query, setQuery] = useState("");
  const [matches, setMatches] = useState<any[]>([]);
  const [isMatching, setIsMatching] = useState(false);
  const { data, refetch, isLoading, error } = useQuery({
    queryKey: ["jobs", query],
    queryFn: () => apiFetch<any[]>(`/jobs/search${query ? `?q=${encodeURIComponent(query)}` : ""}`)
  });

  async function generateMatches() {
    setIsMatching(true);
    try {
      const result = await apiFetch<any[]>("/jobs/match", { method: "POST", body: JSON.stringify({ limit: 10 }) });
      setMatches(result);
    } catch (e) {
      console.error(e);
    } finally {
      setIsMatching(false);
    }
  }

  return (
    <>
      <PageHeader title="Job Dashboard" description="Find jobs that match your exact skills and let AI explain why you are a fit." />
      
      <div className="mb-6 flex gap-3">
        <Input placeholder="Search by role (e.g. Software Engineer)" value={query} onChange={(event) => setQuery(event.target.value)} className="max-w-md" />
        <Button onClick={() => refetch()}><Search className="mr-2 h-4 w-4" /> Search Jobs</Button>
        <Button variant="primary" className="bg-indigo-600 hover:bg-indigo-700 text-white" disabled={isMatching} onClick={generateMatches}>
          {isMatching ? "AI is Matching..." : "Match My Resume"}
        </Button>
      </div>

      {isLoading ? <div className="text-muted-foreground p-4">Loading jobs...</div> : null}
      {error ? <div className="text-red-600 p-4 border rounded bg-red-50">Could not load jobs. Check your login and backend server.</div> : null}
      
      {matches.length > 0 && (
        <div className="mb-10">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <CheckCircle className="h-6 w-6 text-indigo-600" /> AI Recommended Jobs
          </h2>
          <div className="grid gap-6 md:grid-cols-2">
            {matches.map((match) => (
              <Card key={match.id} className="p-5 flex flex-col justify-between border-t-4 border-t-indigo-500 hover:shadow-md transition-shadow">
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-lg text-slate-800">{match.job_title}</h3>
                    <Badge variant={match.overall_score > 75 ? "default" : "secondary"} className={match.overall_score > 75 ? "bg-emerald-500" : ""}>
                      {Math.round(match.overall_score)}% Match
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-slate-500 mb-4">
                    <Building2 className="h-4 w-4" /> {match.company_name}
                  </div>
                  
                  <div className="mb-4">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-medium text-slate-600">Match Progress</span>
                      <span>{Math.round(match.overall_score)}/100</span>
                    </div>
                    <Progress value={match.overall_score} className="h-2" />
                  </div>

                  {match.match_explanation && (
                    <div className="mb-4 bg-slate-50 p-3 rounded-md border text-sm text-slate-700 whitespace-pre-wrap">
                      <span className="font-semibold block mb-1">AI Explanation:</span>
                      {match.match_explanation}
                    </div>
                  )}

                  {match.missing_skills?.length > 0 && (
                    <div className="mb-4">
                      <span className="text-xs font-semibold uppercase text-slate-500 flex items-center gap-1 mb-2">
                        <AlertTriangle className="h-3 w-3" /> Missing Skills
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {match.missing_skills.map((skill: string) => (
                          <Badge key={skill} variant="outline" className="text-amber-700 border-amber-200 bg-amber-50">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                <Button className="w-full mt-4" variant="secondary">View Details</Button>
              </Card>
            ))}
          </div>
        </div>
      )}

      <div>
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Briefcase className="h-6 w-6 text-slate-700" /> All Available Jobs
        </h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {(data ?? []).map((job) => (
            <Card key={job.id} className="p-4 hover:shadow-sm transition-shadow">
              <h3 className="font-semibold text-slate-800 line-clamp-1">{job.title}</h3>
              <div className="flex items-center gap-1 text-sm text-slate-500 mt-2">
                <Building2 className="h-3 w-3" /> {job.company}
              </div>
              <div className="flex items-center gap-1 text-sm text-slate-500 mt-1">
                <MapPin className="h-3 w-3" /> {job.location ?? "Remote"}
              </div>
            </Card>
          ))}
          {data?.length === 0 ? (
            <div className="col-span-full p-8 text-center text-slate-500 border rounded-lg bg-slate-50 dashed border-slate-300">
              No jobs found. Add JSearch credentials or seed jobs in PostgreSQL.
            </div>
          ) : null}
        </div>
      </div>
    </>
  );
}
