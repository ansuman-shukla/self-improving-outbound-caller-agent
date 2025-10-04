/**
 * Tuning Loop Detail Page
 * Shows iteration-by-iteration results and score progression
 * Part of Phase 4, Module 4: The Automated Tuning Loop
 */
"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  Target,
  Zap,
  FileText,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { getTuningLoop, getPrompts, getScenarios, getPromptById } from "@/lib/api";
import { TuningLoopWithDetails } from "@/types/tuning";
import { Prompt } from "@/types/library";
import { Scenario } from "@/types/scenario";
import { usePolling } from "@/hooks/usePolling";

export default function TuningDetailPage() {
  const params = useParams();
  const router = useRouter();
  const tuningLoopId = params?.id as string;

  const [tuningLoop, setTuningLoop] = useState<TuningLoopWithDetails | null>(null);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [initialPrompt, setInitialPrompt] = useState<Prompt | null>(null);
  const [finalPrompt, setFinalPrompt] = useState<Prompt | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [initialPromptExpanded, setInitialPromptExpanded] = useState(false);
  const [finalPromptExpanded, setFinalPromptExpanded] = useState(false);

  // Initial load
  useEffect(() => {
    fetchData();
  }, [tuningLoopId]);

  // Poll for updates if the tuning loop is active
  const isActive =
    tuningLoop?.status === "PENDING" || tuningLoop?.status === "RUNNING";

  const { data: updatedLoop } = usePolling({
    fetchFn: () => getTuningLoop(tuningLoopId),
    shouldStopPolling: (loop) =>
      loop.status === "COMPLETED" || loop.status === "FAILED",
    interval: 3000,
    enabled: isActive,
    onData: (loop) => {
      // Update with enriched data
      enrichAndSetLoop(loop);
    },
  });

  const fetchData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [loopData, promptsResponse, scenariosData] = await Promise.all([
        getTuningLoop(tuningLoopId),
        getPrompts(),
        getScenarios(),
      ]);

      setPrompts(promptsResponse.prompts);
      setScenarios(scenariosData);
      await enrichAndSetLoop(loopData, scenariosData);
    } catch (err) {
      console.error("Error fetching tuning loop:", err);
      setError(err instanceof Error ? err.message : "Failed to load tuning loop");
    } finally {
      setIsLoading(false);
    }
  };

  const enrichAndSetLoop = async (loop: any, scenariosList?: Scenario[]) => {
    // Use provided scenarios or fall back to state
    const scenariosToUse = scenariosList || scenarios;
    
    // Find initial prompt (from first iteration)
    let initialPromptName = "Unknown";
    let initialPromptObj: Prompt | null = null;
    if (loop.iterations.length > 0) {
      const firstPromptId = loop.iterations[0].prompt_id;
      try {
        initialPromptObj = await getPromptById(firstPromptId);
        initialPromptName = initialPromptObj.name;
        setInitialPrompt(initialPromptObj);
      } catch (err) {
        console.error("Failed to fetch initial prompt:", err);
      }
    }

    // Find final prompt
    let finalPromptName = undefined;
    let finalPromptObj: Prompt | null = null;
    if (loop.final_prompt_id) {
      try {
        finalPromptObj = await getPromptById(loop.final_prompt_id);
        finalPromptName = finalPromptObj.name;
        setFinalPrompt(finalPromptObj);
      } catch (err) {
        console.error("Failed to fetch final prompt:", err);
      }
    }

    // Build scenario name mapping
    const scenarioNames: { [key: string]: string } = {};
    loop.config.scenario_weights.forEach((sw: any) => {
      const scenario = scenariosToUse.find((s) => s._id === sw.scenario_id);
      if (scenario) {
        scenarioNames[sw.scenario_id] = scenario.title;
      }
    });

    setTuningLoop({
      ...loop,
      initial_prompt_name: initialPromptName,
      final_prompt_name: finalPromptName,
      scenario_names: scenarioNames,
    });
  };

  const getStatusIcon = () => {
    if (!tuningLoop) return null;
    switch (tuningLoop.status) {
      case "PENDING":
        return <Clock className="h-6 w-6 text-yellow-400" />;
      case "RUNNING":
        return <Loader2 className="h-6 w-6 animate-spin text-blue-400" />;
      case "COMPLETED":
        return <CheckCircle className="h-6 w-6 text-green-400" />;
      case "FAILED":
        return <XCircle className="h-6 w-6 text-red-400" />;
    }
  };

  const getStatusColor = () => {
    if (!tuningLoop) return "text-gray-400";
    switch (tuningLoop.status) {
      case "PENDING":
        return "text-yellow-400";
      case "RUNNING":
        return "text-blue-400";
      case "COMPLETED":
        return "text-green-400";
      case "FAILED":
        return "text-red-400";
    }
  };

  const getScoreImprovement = () => {
    if (!tuningLoop || tuningLoop.iterations.length < 2) return null;
    const firstScore = tuningLoop.iterations[0].weighted_score;
    const latestScore =
      tuningLoop.iterations[tuningLoop.iterations.length - 1].weighted_score;
    const improvement = latestScore - firstScore;
    return improvement;
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black">
        <Loader2 className="h-8 w-8 animate-spin text-white" />
        <span className="ml-3 text-gray-400">Loading tuning loop details...</span>
      </div>
    );
  }

  if (error || !tuningLoop) {
    return (
      <div className="min-h-screen bg-black p-8">
        <div className="mx-auto max-w-7xl">
          <button
            onClick={() => router.push("/tuning")}
            className="mb-4 flex items-center gap-2 text-gray-400 hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Tuning Hub
          </button>
          <div className="rounded-lg border border-red-900 bg-red-950/20 p-8 text-center">
            <p className="text-red-400">❌ {error || "Tuning loop not found"}</p>
          </div>
        </div>
      </div>
    );
  }

  const improvement = getScoreImprovement();

  return (
    <div className="min-h-screen bg-black p-8">
      <div className="mx-auto max-w-7xl space-y-8">
        {/* Back Button */}
        <button
          onClick={() => router.push("/tuning")}
          className="flex items-center gap-2 text-gray-400 hover:text-white"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Tuning Hub
        </button>

        {/* Header */}
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              {getStatusIcon()}
              <div>
                <h1 className="text-2xl font-bold text-white">
                  Tuning Loop Details
                </h1>
                <p className={`mt-1 text-lg font-medium ${getStatusColor()}`}>
                  Status: {tuningLoop.status}
                </p>
                <p className="mt-1 text-sm text-gray-400">
                  ID: {tuningLoop._id}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-400">Created</p>
              <p className="text-white">
                {new Date(tuningLoop.created_at).toLocaleString()}
              </p>
              {tuningLoop.completed_at && (
                <>
                  <p className="mt-2 text-sm text-gray-400">Completed</p>
                  <p className="text-white">
                    {new Date(tuningLoop.completed_at).toLocaleString()}
                  </p>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Configuration Summary */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {/* Target Score */}
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
            <div className="flex items-center gap-3">
              <Target className="h-5 w-5 text-white" />
              <div>
                <p className="text-sm text-gray-400">Target Score</p>
                <p className="text-2xl font-bold text-white">
                  {tuningLoop.config.target_score}
                </p>
              </div>
            </div>
          </div>

          {/* Max Iterations */}
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
            <div className="flex items-center gap-3">
              <Zap className="h-5 w-5 text-white" />
              <div>
                <p className="text-sm text-gray-400">Progress</p>
                <p className="text-2xl font-bold text-white">
                  {tuningLoop.iterations.length} / {tuningLoop.config.max_iterations}
                </p>
              </div>
            </div>
          </div>

          {/* Score Improvement */}
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
            <div className="flex items-center gap-3">
              <TrendingUp className="h-5 w-5 text-white" />
              <div>
                <p className="text-sm text-gray-400">Improvement</p>
                <p
                  className={`text-2xl font-bold ${
                    improvement !== null && improvement >= 0
                      ? "text-green-400"
                      : "text-red-400"
                  }`}
                >
                  {improvement !== null
                    ? `${improvement >= 0 ? "+" : ""}${improvement.toFixed(1)}`
                    : "—"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Initial Prompt */}
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
          <h2 className="mb-3 text-lg font-semibold text-white">Initial Prompt</h2>
          {initialPrompt ? (
            <>
              <div className="mb-2">
                <p className="font-medium text-white">{initialPrompt.name}</p>
                <p className="text-sm text-gray-400">Version: {initialPrompt.version}</p>
              </div>
              <div className="rounded-lg border border-zinc-700 bg-zinc-800 p-4">
                <p className="whitespace-pre-wrap text-sm text-gray-300">
                  {initialPromptExpanded
                    ? initialPrompt.prompt_text
                    : initialPrompt.prompt_text.slice(0, 200) + "..."}
                </p>
                <button
                  onClick={() => setInitialPromptExpanded(!initialPromptExpanded)}
                  className="mt-3 flex items-center gap-1 text-sm text-blue-400 hover:text-blue-300"
                >
                  {initialPromptExpanded ? (
                    <>
                      <ChevronUp className="h-4 w-4" />
                      Show Less
                    </>
                  ) : (
                    <>
                      <ChevronDown className="h-4 w-4" />
                      Show More
                    </>
                  )}
                </button>
              </div>
            </>
          ) : (
            <p className="text-gray-400">Loading initial prompt...</p>
          )}
        </div>

        {/* Final Prompt (if completed) */}
        {tuningLoop.final_prompt_id && (
          <div className="rounded-lg border border-green-900 bg-green-950/20 p-6">
            <h2 className="mb-3 text-lg font-semibold text-green-400">
              Final Optimized Prompt
            </h2>
            {finalPrompt ? (
              <>
                <div className="mb-2">
                  <p className="font-medium text-green-300">{finalPrompt.name}</p>
                  <p className="text-sm text-gray-400">Version: {finalPrompt.version}</p>
                  <p className="text-sm text-gray-400">ID: {tuningLoop.final_prompt_id}</p>
                </div>
                <div className="rounded-lg border border-green-800 bg-green-950/30 p-4">
                  <p className="whitespace-pre-wrap text-sm text-gray-300">
                    {finalPromptExpanded
                      ? finalPrompt.prompt_text
                      : finalPrompt.prompt_text.slice(0, 200) + "..."}
                  </p>
                  <button
                    onClick={() => setFinalPromptExpanded(!finalPromptExpanded)}
                    className="mt-3 flex items-center gap-1 text-sm text-green-400 hover:text-green-300"
                  >
                    {finalPromptExpanded ? (
                      <>
                        <ChevronUp className="h-4 w-4" />
                        Show Less
                      </>
                    ) : (
                      <>
                        <ChevronDown className="h-4 w-4" />
                        Show More
                      </>
                    )}
                  </button>
                </div>
              </>
            ) : (
              <p className="text-gray-400">Loading final prompt...</p>
            )}
          </div>
        )}

        {/* Scenarios */}
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
          <h2 className="mb-4 text-lg font-semibold text-white">
            Test Scenarios ({tuningLoop.config.scenario_weights.length})
          </h2>
          <div className="space-y-2">
            {tuningLoop.config.scenario_weights.map((sw, index) => (
              <div
                key={index}
                className="flex items-center justify-between rounded-lg border border-zinc-700 bg-zinc-800 p-3"
              >
                <span className="text-gray-300">
                  {tuningLoop.scenario_names?.[sw.scenario_id] || "Unknown"}
                </span>
                <span className="rounded bg-zinc-700 px-3 py-1 text-sm font-medium text-white">
                  Weight: {sw.weight}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Iterations */}
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
          <h2 className="mb-4 text-lg font-semibold text-white">
            Iteration History ({tuningLoop.iterations.length})
          </h2>

          {tuningLoop.iterations.length === 0 ? (
            <p className="text-center text-gray-400 py-8">
              No iterations yet. The tuning loop is pending...
            </p>
          ) : (
            <div className="space-y-4">
              {tuningLoop.iterations.map((iteration, index) => {
                const isFirst = index === 0;
                const scoreChange =
                  !isFirst
                    ? iteration.weighted_score -
                      tuningLoop.iterations[index - 1].weighted_score
                    : 0;

                return (
                  <div
                    key={iteration.iteration_number}
                    className="rounded-lg border border-zinc-700 bg-zinc-800 p-4"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-zinc-700 font-bold text-white">
                          {iteration.iteration_number}
                        </div>
                        <div>
                          <p className="font-medium text-white">
                            Iteration {iteration.iteration_number}
                          </p>
                          <p className="text-sm text-gray-400">
                            {new Date(iteration.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-white">
                          {iteration.weighted_score.toFixed(1)}
                        </p>
                        {!isFirst && (
                          <p
                            className={`text-sm ${
                              scoreChange >= 0 ? "text-green-400" : "text-red-400"
                            }`}
                          >
                            {scoreChange >= 0 ? "+" : ""}
                            {scoreChange.toFixed(1)}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
                      <div className="rounded border border-zinc-600 bg-zinc-700 p-3">
                        <p className="text-xs text-gray-400">Prompt ID</p>
                        <p className="mt-1 font-mono text-xs text-gray-300">
                          {iteration.prompt_id}
                        </p>
                      </div>
                      <div className="rounded border border-zinc-600 bg-zinc-700 p-3">
                        <p className="text-xs text-gray-400">Evaluations</p>
                        <p className="mt-1 text-sm text-white">
                          {iteration.evaluation_ids.length} completed
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Error Message (if failed) */}
        {tuningLoop.status === "FAILED" && tuningLoop.error_message && (
          <div className="rounded-lg border border-red-900 bg-red-950/20 p-6">
            <h2 className="mb-3 text-lg font-semibold text-red-400">
              ❌ Error Details
            </h2>
            <p className="text-gray-300">{tuningLoop.error_message}</p>
          </div>
        )}
      </div>
    </div>
  );
}
