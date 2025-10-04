/**
 * Tuning Hub Page
 * Main page for automated tuning loops
 * Part of Phase 4, Module 4: The Automated Tuning Loop
 */
"use client";

import { useState, useEffect } from "react";
import { Zap, RefreshCw, Plus } from "lucide-react";
import TuningInitiationForm from "@/components/TuningInitiationForm";
import TuningRunsTable from "@/components/TuningRunsTable";
import { listTuningLoops, getPrompts, getScenarios } from "@/lib/api";
import { TuningLoopWithDetails } from "@/types/tuning";
import { Prompt } from "@/types/library";
import { Scenario } from "@/types/scenario";

export default function TuningHubPage() {
  const [tuningLoops, setTuningLoops] = useState<TuningLoopWithDetails[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);

  // For enriching tuning loops with names
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch tuning loops, prompts, and scenarios in parallel
      const [tuningLoopsData, promptsResponse, scenariosData] = await Promise.all([
        listTuningLoops(),
        getPrompts(),
        getScenarios(),
      ]);

      setPrompts(promptsResponse.prompts);
      setScenarios(scenariosData);

      // Enrich tuning loops with prompt and scenario names
      const enriched: TuningLoopWithDetails[] = tuningLoopsData.map((loop) => {
        // Find initial prompt name
        const initialPrompt = promptsResponse.prompts.find(
          (p) => p._id === loop.iterations[0]?.prompt_id || loop.config.scenario_weights[0]?.scenario_id
        );
        
        // For the actual initial prompt, we need to look at the first iteration
        // If no iterations yet, we can't determine the prompt name from the loop data
        let initialPromptName = "Unknown";
        if (loop.iterations.length > 0) {
          const firstIterationPrompt = promptsResponse.prompts.find(
            (p) => p._id === loop.iterations[0].prompt_id
          );
          initialPromptName = firstIterationPrompt?.name || "Unknown";
        }

        // Find final prompt name (if completed)
        let finalPromptName = undefined;
        if (loop.final_prompt_id) {
          const finalPrompt = promptsResponse.prompts.find(
            (p) => p._id === loop.final_prompt_id
          );
          finalPromptName = finalPrompt?.name || "Unknown";
        }

        // Build scenario name mapping
        const scenarioNames: { [key: string]: string } = {};
        loop.config.scenario_weights.forEach((sw) => {
          const scenario = scenariosData.find((s) => s._id === sw.scenario_id);
          if (scenario) {
            scenarioNames[sw.scenario_id] = scenario.title;
          }
        });

        return {
          ...loop,
          initial_prompt_name: initialPromptName,
          final_prompt_name: finalPromptName,
          scenario_names: scenarioNames,
        };
      });

      setTuningLoops(enriched);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError(err instanceof Error ? err.message : "Failed to load tuning loops");
    } finally {
      setIsLoading(false);
    }
  };

  const handleTuningCreated = (tuningLoopId: string) => {
    setSuccessMessage(`✅ Tuning loop started! ID: ${tuningLoopId}`);

    // Clear success message after 5 seconds
    setTimeout(() => setSuccessMessage(null), 5000);

    // Refresh the tuning loops list
    fetchData();
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    setTimeout(() => setError(null), 5000);
  };

  return (
    <div className="min-h-screen bg-black p-8">
      <div className="mx-auto max-w-7xl space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Zap className="h-8 w-8 text-white" />
            <div>
              <h1 className="text-3xl font-bold text-white">Tuning Hub</h1>
              <p className="text-gray-400">
                Automated prompt optimization with AI-powered iteration
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchData}
              disabled={isLoading}
              className="flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2 font-medium text-white hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <RefreshCw
                className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`}
              />
              Refresh
            </button>
            <button
              onClick={() => setIsFormOpen(true)}
              className="flex items-center gap-2 rounded-lg bg-white px-4 py-2 font-medium text-black hover:bg-gray-200"
            >
              <Plus className="h-4 w-4" />
              Start New Tuning Loop
            </button>
          </div>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="rounded-lg border border-green-900 bg-green-950/20 p-4">
            <p className="text-green-400">{successMessage}</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="rounded-lg border border-red-900 bg-red-950/20 p-4">
            <p className="text-red-400">❌ {error}</p>
          </div>
        )}

        {/* Info Box */}
        <div className="rounded-lg border border-blue-900 bg-blue-950/20 p-4">
          <p className="text-sm text-blue-300">
            💡 <strong>How it works:</strong> Select an initial prompt, set a target score, and choose test scenarios. 
            The system will automatically run evaluations, analyze failures, and iteratively improve the prompt using AI 
            until the target is reached or max iterations is hit.
          </p>
        </div>

        {/* Tuning Runs Table */}
        {isLoading ? (
          <div className="flex items-center justify-center rounded-lg border border-zinc-800 bg-zinc-900 p-12">
            <RefreshCw className="h-6 w-6 animate-spin text-white" />
            <span className="ml-3 text-gray-400">Loading tuning loops...</span>
          </div>
        ) : (
          <TuningRunsTable tuningLoops={tuningLoops} onUpdate={fetchData} />
        )}

        {/* Tuning Initiation Form Modal */}
        <TuningInitiationForm
          isOpen={isFormOpen}
          onClose={() => setIsFormOpen(false)}
          onTuningCreated={handleTuningCreated}
          onError={handleError}
        />
      </div>
    </div>
  );
}
