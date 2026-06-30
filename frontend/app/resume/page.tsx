"use client";

import { useState } from "react";
import { Upload, CheckCircle2, AlertCircle, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";
import { apiFetch } from "@/lib/api/client";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

export default function ResumePage() {
  const [message, setMessage] = useState("");
  const [resumeId, setResumeId] = useState<number | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [parsedSummary, setParsedSummary] = useState<any>(null);

  async function upload(formData: FormData) {
    setIsUploading(true);
    setMessage("Uploading and parsing resume...");
    setAnalysis(null);
    try {
      const resume = await apiFetch<{ id: number; parsed_summary: any }>("/resumes/upload", { method: "POST", body: formData });
      setResumeId(resume.id);
      setParsedSummary(resume.parsed_summary);
      setMessage(`Resume uploaded and parsed successfully! Found ${resume.parsed_summary?.skills?.length ?? 0} basic skills.`);
    } catch (e) {
      setMessage("Error uploading resume.");
    } finally {
      setIsUploading(false);
    }
  }

  async function analyze() {
    if (!resumeId) return;
    setIsAnalyzing(true);
    setMessage("AI is analyzing your resume deeply. This may take a minute...");
    try {
      const result = await apiFetch(`/resumes/${resumeId}/analyze`, { method: "POST" });
      setAnalysis(result);
      setMessage("Resume analysis complete! Check out your readiness score and extracted skills below.");
    } catch (e) {
      setMessage("Error analyzing resume.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <>
      <PageHeader title="Resume Intelligence" description="Upload your resume to get deep AI-driven feedback and extract all your skills." />
      
      <Card className="mb-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <form action={upload} className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-muted-foreground" />
              <input className="rounded-md border bg-white p-2 text-sm w-full md:w-auto" type="file" name="file" accept=".pdf,.txt" required />
            </div>
            <Button type="submit" disabled={isUploading}>
              <Upload className="mr-2 h-4 w-4" /> 
              {isUploading ? "Uploading..." : "Upload Resume"}
            </Button>
          </form>
          {resumeId && (
            <Button variant="primary" className="bg-emerald-600 hover:bg-emerald-700 text-white" disabled={isAnalyzing} onClick={analyze}>
              {isAnalyzing ? "Analyzing..." : "Analyze with AI"}
            </Button>
          )}
        </div>
        {message && (
          <div className="mt-4 p-3 bg-slate-50 text-sm text-slate-700 rounded-md border flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            {message}
          </div>
        )}
      </Card>

      {analysis && analysis.resume_analysis_data && (
        <div className="grid gap-6 md:grid-cols-2">
          {/* ATS Score Overview */}
          <Card className="p-6 border-t-4 border-t-emerald-500">
            <h3 className="text-xl font-semibold mb-4">ATS Suitability Score</h3>
            <div className="flex items-center justify-between mb-2">
              <span className="text-3xl font-bold text-emerald-600">{analysis.ats_score}%</span>
              <Badge variant="outline" className="bg-emerald-50 text-emerald-700">Ready</Badge>
            </div>
            <Progress value={analysis.ats_score} className="h-3 mb-6 bg-slate-100 [&>div]:bg-emerald-500" />
            
            <h4 className="font-semibold text-slate-700 mb-2 mt-4">Why you got this score:</h4>
            <p className="text-sm text-slate-600 mb-4">{analysis.resume_analysis_data.ats_score_explanation || analysis.improvements?.[0]}</p>

            <h4 className="font-semibold text-slate-700 mb-2 mt-4">AI Improvements:</h4>
            <ul className="text-sm text-slate-600 list-disc pl-4 space-y-1">
              {(analysis.resume_analysis_data.improvements || []).map((imp: string, i: number) => (
                <li key={i}>{imp}</li>
              ))}
            </ul>
          </Card>

          {/* Extracted Deep Skills */}
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-4">AI Skill Extraction</h3>
            <div className="space-y-6">
              
              {analysis.resume_analysis_data.technical_skills && analysis.resume_analysis_data.technical_skills.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-slate-500 mb-2 uppercase tracking-wider">Technical Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis.resume_analysis_data.technical_skills.map((s: string) => (
                      <Badge key={s} variant="secondary" className="bg-blue-50 text-blue-700 hover:bg-blue-100">{s}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {analysis.resume_analysis_data.programming_languages && analysis.resume_analysis_data.programming_languages.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-slate-500 mb-2 uppercase tracking-wider">Programming Languages</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis.resume_analysis_data.programming_languages.map((s: string) => (
                      <Badge key={s} variant="secondary" className="bg-indigo-50 text-indigo-700 hover:bg-indigo-100">{s}</Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {analysis.resume_analysis_data.frameworks && analysis.resume_analysis_data.frameworks.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-slate-500 mb-2 uppercase tracking-wider">Frameworks & Tools</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis.resume_analysis_data.frameworks.map((s: string) => (
                      <Badge key={s} variant="secondary" className="bg-purple-50 text-purple-700 hover:bg-purple-100">{s}</Badge>
                    ))}
                    {(analysis.resume_analysis_data.tools || []).map((s: string) => (
                      <Badge key={s} variant="secondary" className="bg-purple-50 text-purple-700 hover:bg-purple-100">{s}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {analysis.resume_analysis_data.soft_skills && analysis.resume_analysis_data.soft_skills.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-slate-500 mb-2 uppercase tracking-wider">Soft Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis.resume_analysis_data.soft_skills.map((s: string) => (
                      <Badge key={s} variant="outline">{s}</Badge>
                    ))}
                  </div>
                </div>
              )}

            </div>
          </Card>
        </div>
      )}
    </>
  );
}
