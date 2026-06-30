"use client";

import { FormEvent, useState } from "react";
import { Mic, CheckCircle2, AlertTriangle, ArrowRight, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/layout/page-header";
import { apiFetch } from "@/lib/api/client";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

export default function InterviewPage() {
  const [interview, setInterview] = useState<any>(null);
  const [feedback, setFeedback] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsGenerating(true);
    const form = new FormData(event.currentTarget);
    try {
      const result = await apiFetch("/interviews/start", {
        method: "POST",
        body: JSON.stringify({
          target_role: form.get("target_role"),
          difficulty: form.get("difficulty"),
          interview_type: form.get("interview_type")
        })
      });
      setInterview(result);
      setFeedback(null);
      setCurrentQuestionIndex(0);
    } catch (e) {
      console.error(e);
    } finally {
      setIsGenerating(false);
    }
  }

  async function submitAnswer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!interview?.questions?.[currentQuestionIndex]) return;
    setIsSubmitting(true);
    const form = new FormData(event.currentTarget);
    try {
      const result = await apiFetch(`/interviews/${interview.id}/answer`, {
        method: "POST",
        body: JSON.stringify({ question_id: interview.questions[currentQuestionIndex].id, answer: form.get("answer") })
      });
      setFeedback(result);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmitting(false);
    }
  }

  const nextQuestion = () => {
    setFeedback(null);
    setCurrentQuestionIndex((prev) => Math.min(prev + 1, interview.questions.length - 1));
  };

  return (
    <>
      <PageHeader title="AI Mock Interview" description="Sharpen your skills with a Gemini AI mock interview tailored to your target role." />
      
      <Card className="p-5 mb-6">
        <form className="grid gap-3 md:grid-cols-[1fr_160px_160px_auto]" onSubmit={onSubmit}>
          <Input name="target_role" placeholder="Target role, e.g. Backend Dev" required />
          <Input name="difficulty" defaultValue="medium" placeholder="Difficulty" />
          <Input name="interview_type" defaultValue="mixed" placeholder="Type" />
          <Button type="submit" variant="primary" disabled={isGenerating}>
            <Mic className="mr-2 h-4 w-4" /> {isGenerating ? "Preparing..." : "Start Interview"}
          </Button>
        </form>
      </Card>

      {interview?.questions?.length > 0 && (
        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-6">
            <Card className="p-6 border-t-4 border-t-blue-500">
              <div className="flex items-center justify-between mb-4">
                <Badge variant="secondary" className="bg-blue-50 text-blue-700">
                  Question {currentQuestionIndex + 1} of {interview.questions.length}
                </Badge>
                <Badge variant="outline" className="uppercase tracking-wider text-xs">
                  {interview.questions[currentQuestionIndex].category}
                </Badge>
              </div>
              <h2 className="text-xl font-medium text-slate-800 mb-6 leading-relaxed">
                {interview.questions[currentQuestionIndex].question}
              </h2>
              
              {!feedback ? (
                <form className="space-y-4" onSubmit={submitAnswer}>
                  <textarea 
                    name="answer" 
                    className="w-full min-h-[120px] rounded-md border border-slate-300 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Type your detailed answer here..." 
                    required 
                  />
                  <div className="flex justify-end">
                    <Button type="submit" variant="primary" disabled={isSubmitting}>
                      {isSubmitting ? "Evaluating..." : "Submit Answer"}
                    </Button>
                  </div>
                </form>
              ) : (
                <div className="space-y-6">
                  <div className="bg-slate-50 border rounded-lg p-4">
                    <h4 className="text-sm font-bold text-slate-700 mb-2 flex items-center gap-2">
                      <Activity className="h-4 w-4" /> AI Evaluation Feedback
                    </h4>
                    <p className="text-sm text-slate-600 whitespace-pre-wrap">{feedback.feedback}</p>
                  </div>
                  
                  {currentQuestionIndex < interview.questions.length - 1 ? (
                    <div className="flex justify-end">
                      <Button onClick={nextQuestion} variant="secondary">
                        Next Question <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <div className="text-center p-4 bg-emerald-50 text-emerald-700 rounded-lg font-medium border border-emerald-200">
                      Interview Complete! Check your Dashboard for updated readiness scores.
                    </div>
                  )}
                </div>
              )}
            </Card>
          </div>

          <div className="md:col-span-1">
            {feedback && (
              <Card className="p-5 sticky top-4">
                <h3 className="font-bold text-slate-800 mb-4 border-b pb-2">Scorecard</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-xs font-semibold text-slate-600 mb-1">
                      <span>Technical Accuracy</span>
                      <span>{feedback.technical_score}/100</span>
                    </div>
                    <Progress value={feedback.technical_score} className="h-2 [&>div]:bg-blue-600" />
                  </div>
                  <div>
                    <div className="flex justify-between text-xs font-semibold text-slate-600 mb-1">
                      <span>Communication</span>
                      <span>{feedback.communication_score}/100</span>
                    </div>
                    <Progress value={feedback.communication_score} className="h-2 [&>div]:bg-indigo-500" />
                  </div>
                  <div>
                    <div className="flex justify-between text-xs font-semibold text-slate-600 mb-1">
                      <span>Confidence</span>
                      <span>{feedback.confidence_score}/100</span>
                    </div>
                    <Progress value={feedback.confidence_score} className="h-2 [&>div]:bg-emerald-500" />
                  </div>
                  <div>
                    <div className="flex justify-between text-xs font-semibold text-slate-600 mb-1">
                      <span>Grammar</span>
                      <span>{feedback.grammar_score}/100</span>
                    </div>
                    <Progress value={feedback.grammar_score} className="h-2 [&>div]:bg-amber-500" />
                  </div>
                </div>
              </Card>
            )}
          </div>
        </div>
      )}
    </>
  );
}
