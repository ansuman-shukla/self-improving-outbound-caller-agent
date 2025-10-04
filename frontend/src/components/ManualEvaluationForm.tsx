/**
 * ManualEvaluationForm Component
 * Form to start a new evaluation by selecting a prompt and scenario
 * Part of Phase 3, Module 3: The Manual Evaluation Engine
 */
"use client";

import { useState, useEffect } from "react";
import { Play, Loader2 } from "lucide-react";
import { Prompt } from "@/types/library";
import { Scenario } from "@/types/scenario";
import { getPrompts, getScenarios, createEvaluation } from "@/lib/api";

interface ManualEvaluationFormProps {
  onEvaluationCreated?: (resultId: string) => void;
  onError?: (error: string) => void;
}

export default function ManualEvaluationForm({
  onEvaluationCreated,
  onError,
}: ManualEvaluationFormProps) {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  
  const [selectedPromptId, setSelectedPromptId] = useState<string>("");
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>("");
  
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Load prompts and scenarios on mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoadingData(true);
      setLoadError(null);
      
      const [promptsResponse, scenariosData] = await Promise.all([
        getPrompts(),
        getScenarios(),
      ]);
      
      setPrompts(promptsResponse.prompts);
      setScenarios(scenariosData);
      
      // Auto-select first items if available
      if (promptsResponse.prompts.length > 0 && !selectedPromptId) {
        setSelectedPromptId(promptsResponse.prompts[0]._id);
      }
      if (scenariosData.length > 0 && !selectedScenarioId) {
        setSelectedScenarioId(scenariosData[0]._id);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to load data";
      setLoadError(errorMsg);
      if (onError) {
        onError(errorMsg);
      }
    } finally {
      setIsLoadingData(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedPromptId || !selectedScenarioId) {
      const errorMsg = "Please select both a prompt and a scenario";
      if (onError) {
        onError(errorMsg);
      }
      return;
    }
    
    try {
      setIsSubmitting(true);
      
      const response = await createEvaluation({
        prompt_id: selectedPromptId,
        scenario_id: selectedScenarioId,
      });
      
      if (onEvaluationCreated) {
        onEvaluationCreated(response.result_id);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to create evaluation";
      if (onError) {
        onError(errorMsg);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoadingData) {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
        <div className="flex items-center justify-center">
          <Loader2 className="h-5 w-5 animate-spin text-white" />
          <span className="ml-2 text-gray-400">Loading prompts and scenarios...</span>
        </div>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="rounded-lg border border-red-900 bg-red-950/20 p-6">
        <p className="text-red-400">❌ {loadError}</p>
        <button
          onClick={loadData}
          className="mt-3 text-sm text-red-300 underline hover:text-red-200"
        >
          Try again
        </button>
      </div>
    );
  }

  if (prompts.length === 0 || scenarios.length === 0) {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
        <p className="text-gray-400">
          {prompts.length === 0 && scenarios.length === 0
            ? "⚠️ No prompts or scenarios available. Please create them first in the Library and Scenario Designer."
            : prompts.length === 0
            ? "⚠️ No prompts available. Please create a prompt in the Library first."
            : "⚠️ No scenarios available. Please create a scenario in the Scenario Designer first."}
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6 shadow-xl">
      <h2 className="mb-4 text-xl font-semibold text-white">
        Start New Evaluation
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Prompt Selection */}
        <div>
          <label
            htmlFor="prompt-select"
            className="mb-2 block text-sm font-medium text-gray-300"
          >
            Select Agent Prompt
          </label>
          <select
            id="prompt-select"
            value={selectedPromptId}
            onChange={(e) => setSelectedPromptId(e.target.value)}
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2.5 text-white placeholder-gray-500 focus:border-white focus:outline-none focus:ring-1 focus:ring-white"
            disabled={isSubmitting}
          >
            {prompts.map((prompt) => (
              <option key={prompt._id} value={prompt._id}>
                {prompt.name} (v{prompt.version})
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            {prompts.length} prompt{prompts.length !== 1 ? "s" : ""} available
          </p>
        </div>

        {/* Scenario Selection */}
        <div>
          <label
            htmlFor="scenario-select"
            className="mb-2 block text-sm font-medium text-gray-300"
          >
            Select Test Scenario
          </label>
          <select
            id="scenario-select"
            value={selectedScenarioId}
            onChange={(e) => setSelectedScenarioId(e.target.value)}
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2.5 text-white placeholder-gray-500 focus:border-white focus:outline-none focus:ring-1 focus:ring-white"
            disabled={isSubmitting}
          >
            {scenarios.map((scenario) => (
              <option key={scenario._id} value={scenario._id}>
                {scenario.title}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            {scenarios.length} scenario{scenarios.length !== 1 ? "s" : ""} available
          </p>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting || !selectedPromptId || !selectedScenarioId}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-white px-4 py-2.5 font-medium text-black transition-all hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Starting Evaluation...</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4" />
              <span>Run Evaluation</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
