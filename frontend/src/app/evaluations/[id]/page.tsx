/**
 * Evaluation Details Page
 * Displays full transcript, scores, and evaluator analysis for a specific evaluation
 * Part of Phase 3, Module 3: The Manual Evaluation Engine
 */
"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, MessageSquare, BarChart3, FileText, Loader2 } from "lucide-react";
import { getEvaluation, getPrompts, getScenarios } from "@/lib/api";
import { Evaluation } from "@/types/evaluation";
import { Prompt } from "@/types/library";
import { Scenario } from "@/types/scenario";
import { format } from "date-fns";

export default function EvaluationDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const evaluationId = params.id as string;

  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [prompt, setPrompt] = useState<Prompt | null>(null);
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (evaluationId) {
      fetchEvaluationDetails();
    }
  }, [evaluationId]);

  const fetchEvaluationDetails = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const evaluationData = await getEvaluation(evaluationId);
      setEvaluation(evaluationData);

      // Fetch prompt and scenario details
      const [promptsResponse, scenariosData] = await Promise.all([
        getPrompts(),
        getScenarios(),
      ]);

      const foundPrompt = promptsResponse.prompts.find(
        (p) => p._id === evaluationData.prompt_id
      );
      const foundScenario = scenariosData.find(
        (s) => s._id === evaluationData.scenario_id
      );

      setPrompt(foundPrompt || null);
      setScenario(foundScenario || null);
    } catch (err) {
      console.error("Error fetching evaluation:", err);
      setError(err instanceof Error ? err.message : "Failed to load evaluation");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black">
        <div className="text-center">
          <Loader2 className="inline-block h-8 w-8 animate-spin text-white" />
          <p className="mt-2 text-gray-400">Loading evaluation details...</p>
        </div>
      </div>
    );
  }

  if (error || !evaluation) {
    return (
      <div className="min-h-screen bg-black p-8">
        <div className="mx-auto max-w-4xl">
          <button
            onClick={() => router.push("/evaluations")}
            className="mb-4 flex items-center gap-2 text-gray-400 hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Evaluations
          </button>
          <div className="rounded-lg border border-red-900 bg-red-950/20 p-8 text-center">
            <p className="text-red-400">❌ {error || "Evaluation not found"}</p>
          </div>
        </div>
      </div>
    );
  }

  const getAverageScore = () => {
    if (evaluation.scores) {
      return Math.round(
        (evaluation.scores.task_completion + evaluation.scores.conversation_efficiency) / 2
      );
    }
    return null;
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <div className="min-h-screen bg-black p-8">
      <div className="mx-auto max-w-5xl space-y-6">
        {/* Header with Back Button */}
        <button
          onClick={() => router.push("/evaluations")}
          className="flex items-center gap-2 text-gray-400 transition-colors hover:text-white"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Evaluations
        </button>

        {/* Title Section */}
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
          <h1 className="text-2xl font-bold text-white">Evaluation Details</h1>
          <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-400">Prompt:</span>
              <p className="font-medium text-white">{prompt?.name || "Unknown"}</p>
            </div>
            <div>
              <span className="text-gray-400">Scenario:</span>
              <p className="font-medium text-white">{scenario?.title || "Unknown"}</p>
            </div>
            <div>
              <span className="text-gray-400">Status:</span>
              <p className="font-medium text-white">{evaluation.status}</p>
            </div>
            <div>
              <span className="text-gray-400">Created:</span>
              <p className="font-medium text-white">
                {format(new Date(evaluation.created_at), "MMM d, yyyy HH:mm:ss")}
              </p>
            </div>
          </div>
        </div>

        {/* Scores Section */}
        {evaluation.status === "COMPLETED" && evaluation.scores && (
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
            <div className="mb-4 flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-white" />
              <h2 className="text-xl font-semibold text-white">Performance Scores</h2>
            </div>

            <div className="grid grid-cols-3 gap-6">
              <div className="rounded-lg border border-zinc-700 bg-zinc-800 p-4 text-center">
                <p className="mb-2 text-sm text-gray-400">Task Completion</p>
                <p className={`text-4xl font-bold ${getScoreColor(evaluation.scores.task_completion)}`}>
                  {evaluation.scores.task_completion}%
                </p>
              </div>
              <div className="rounded-lg border border-zinc-700 bg-zinc-800 p-4 text-center">
                <p className="mb-2 text-sm text-gray-400">Conversation Efficiency</p>
                <p className={`text-4xl font-bold ${getScoreColor(evaluation.scores.conversation_efficiency)}`}>
                  {evaluation.scores.conversation_efficiency}%
                </p>
              </div>
              <div className="rounded-lg border border-zinc-700 bg-zinc-800 p-4 text-center">
                <p className="mb-2 text-sm text-gray-400">Average</p>
                <p className={`text-4xl font-bold ${getScoreColor(getAverageScore()!)}`}>
                  {getAverageScore()}%
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Evaluator Analysis */}
        {evaluation.status === "COMPLETED" && evaluation.evaluator_analysis && (
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
            <div className="mb-4 flex items-center gap-2">
              <FileText className="h-5 w-5 text-white" />
              <h2 className="text-xl font-semibold text-white">Evaluator Analysis</h2>
            </div>
            <div className="rounded-lg border border-zinc-700 bg-zinc-800 p-4">
              <p className="whitespace-pre-wrap text-gray-300">
                {evaluation.evaluator_analysis}
              </p>
            </div>
          </div>
        )}

        {/* Transcript Section */}
        {evaluation.status === "COMPLETED" && evaluation.transcript && (
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
            <div className="mb-4 flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-white" />
              <h2 className="text-xl font-semibold text-white">Conversation Transcript</h2>
              <span className="ml-auto text-sm text-gray-400">
                {evaluation.transcript.length} messages
              </span>
            </div>

            <div className="space-y-4">
              {evaluation.transcript.map((message, index) => (
                <div
                  key={index}
                  className={`rounded-lg p-4 ${
                    message.speaker === "agent"
                      ? "border border-blue-900 bg-blue-950/20"
                      : "border border-purple-900 bg-purple-950/20"
                  }`}
                >
                  <div className="mb-2 flex items-center gap-2">
                    <span
                      className={`text-xs font-semibold uppercase ${
                        message.speaker === "agent" ? "text-blue-400" : "text-purple-400"
                      }`}
                    >
                      {message.speaker}
                    </span>
                    <span className="text-xs text-gray-500">Message {index + 1}</span>
                  </div>
                  <p className="text-gray-300">{message.message}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error Message */}
        {evaluation.status === "FAILED" && evaluation.error_message && (
          <div className="rounded-lg border border-red-900 bg-red-950/20 p-6">
            <h2 className="mb-2 text-xl font-semibold text-red-400">Error</h2>
            <p className="text-gray-300">{evaluation.error_message}</p>
          </div>
        )}

        {/* Pending/Running Status */}
        {(evaluation.status === "PENDING" || evaluation.status === "RUNNING") && (
          <div className="rounded-lg border border-yellow-900 bg-yellow-950/20 p-6 text-center">
            <Loader2 className="inline-block h-6 w-6 animate-spin text-yellow-400" />
            <p className="mt-2 text-yellow-400">
              Evaluation is {evaluation.status.toLowerCase()}...
            </p>
            <p className="mt-1 text-sm text-gray-400">
              This page will not auto-refresh. Please return to the Evaluation Hub to check status.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
