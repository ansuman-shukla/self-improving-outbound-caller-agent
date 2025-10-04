/**
 * TuningInitiationForm Component
 * Modal form to start a new automated tuning loop
 * Part of Phase 4, Module 4: The Automated Tuning Loop
 */
"use client";

import { useState, useEffect } from "react";
import { Play, Loader2, X, Plus, Trash2 } from "lucide-react";
import { Prompt } from "@/types/library";
import { Scenario } from "@/types/scenario";
import { ScenarioWeight } from "@/types/tuning";
import { getPrompts, getScenarios, createTuningLoop } from "@/lib/api";

interface TuningInitiationFormProps {
  isOpen: boolean;
  onClose: () => void;
  onTuningCreated?: (tuningLoopId: string) => void;
  onError?: (error: string) => void;
}

export default function TuningInitiationForm({
  isOpen,
  onClose,
  onTuningCreated,
  onError,
}: TuningInitiationFormProps) {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);

  const [initialPromptId, setInitialPromptId] = useState<string>("");
  const [targetScore, setTargetScore] = useState<number>(85);
  const [maxIterations, setMaxIterations] = useState<number>(5);
  const [selectedScenarios, setSelectedScenarios] = useState<ScenarioWeight[]>([]);

  const [isLoadingData, setIsLoadingData] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Load prompts and scenarios on mount
  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

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

      // Auto-select first prompt if available
      if (promptsResponse.prompts.length > 0 && !initialPromptId) {
        setInitialPromptId(promptsResponse.prompts[0]._id);
      }
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : "Failed to load data";
      setLoadError(errorMsg);
      if (onError) {
        onError(errorMsg);
      }
    } finally {
      setIsLoadingData(false);
    }
  };

  const handleAddScenario = () => {
    // Find first scenario not already selected
    const availableScenario = scenarios.find(
      (s) => !selectedScenarios.find((ss) => ss.scenario_id === s._id)
    );

    if (availableScenario) {
      setSelectedScenarios([
        ...selectedScenarios,
        { scenario_id: availableScenario._id, weight: 3 },
      ]);
    }
  };

  const handleRemoveScenario = (index: number) => {
    setSelectedScenarios(selectedScenarios.filter((_, i) => i !== index));
  };

  const handleScenarioChange = (index: number, scenarioId: string) => {
    const newScenarios = [...selectedScenarios];
    newScenarios[index].scenario_id = scenarioId;
    setSelectedScenarios(newScenarios);
  };

  const handleWeightChange = (index: number, weight: number) => {
    const newScenarios = [...selectedScenarios];
    newScenarios[index].weight = weight;
    setSelectedScenarios(newScenarios);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!initialPromptId) {
      const errorMsg = "Please select an initial prompt";
      if (onError) {
        onError(errorMsg);
      }
      return;
    }

    if (selectedScenarios.length === 0) {
      const errorMsg = "Please add at least one scenario";
      if (onError) {
        onError(errorMsg);
      }
      return;
    }

    // Validate all scenarios are selected (no duplicates)
    const scenarioIds = selectedScenarios.map((s) => s.scenario_id);
    const uniqueIds = new Set(scenarioIds);
    if (scenarioIds.length !== uniqueIds.size) {
      const errorMsg = "Cannot use the same scenario multiple times";
      if (onError) {
        onError(errorMsg);
      }
      return;
    }

    try {
      setIsSubmitting(true);

      const response = await createTuningLoop({
        initial_prompt_id: initialPromptId,
        target_score: targetScore,
        max_iterations: maxIterations,
        scenarios: selectedScenarios,
      });

      if (onTuningCreated) {
        onTuningCreated(response.tuning_loop_id);
      }

      // Reset form
      setInitialPromptId(prompts.length > 0 ? prompts[0]._id : "");
      setTargetScore(85);
      setMaxIterations(5);
      setSelectedScenarios([]);

      onClose();
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : "Failed to create tuning loop";
      if (onError) {
        onError(errorMsg);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4">
      <div className="w-full max-w-3xl rounded-lg border border-zinc-800 bg-zinc-900 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-800 p-6">
          <h2 className="text-2xl font-semibold text-white">
            Start New Tuning Loop
          </h2>
          <button
            onClick={onClose}
            className="rounded-lg p-2 text-gray-400 hover:bg-zinc-800 hover:text-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        <div className="max-h-[70vh] overflow-y-auto p-6">
          {isLoadingData ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-white" />
              <span className="ml-2 text-gray-400">
                Loading prompts and scenarios...
              </span>
            </div>
          ) : loadError ? (
            <div className="rounded-lg border border-red-900 bg-red-950/20 p-4">
              <p className="text-red-400">❌ {loadError}</p>
              <button
                onClick={loadData}
                className="mt-3 text-sm text-red-300 underline hover:text-red-200"
              >
                Try again
              </button>
            </div>
          ) : prompts.length === 0 || scenarios.length === 0 ? (
            <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
              <p className="text-gray-400">
                {prompts.length === 0 && scenarios.length === 0
                  ? "⚠️ No prompts or scenarios available. Please create them first."
                  : prompts.length === 0
                  ? "⚠️ No prompts available. Please create a prompt in the Library first."
                  : "⚠️ No scenarios available. Please create scenarios first."}
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Initial Prompt Selection */}
              <div>
                <label
                  htmlFor="initial-prompt"
                  className="mb-2 block text-sm font-medium text-white"
                >
                  Initial Prompt <span className="text-red-400">*</span>
                </label>
                <select
                  id="initial-prompt"
                  value={initialPromptId}
                  onChange={(e) => setInitialPromptId(e.target.value)}
                  className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2.5 text-white focus:border-white focus:outline-none focus:ring-2 focus:ring-white/20"
                  required
                >
                  {prompts.map((prompt) => (
                    <option key={prompt._id} value={prompt._id}>
                      {prompt.name} (v{prompt.version})
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-gray-400">
                  Starting point for optimization
                </p>
              </div>

              {/* Target Score */}
              <div>
                <label
                  htmlFor="target-score"
                  className="mb-2 block text-sm font-medium text-white"
                >
                  Target Score (0-100) <span className="text-red-400">*</span>
                </label>
                <input
                  type="number"
                  id="target-score"
                  value={targetScore}
                  onChange={(e) => setTargetScore(Number(e.target.value))}
                  min={0}
                  max={100}
                  step={0.1}
                  className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2.5 text-white focus:border-white focus:outline-none focus:ring-2 focus:ring-white/20"
                  required
                />
                <p className="mt-1 text-xs text-gray-400">
                  Loop stops when this weighted average is reached
                </p>
              </div>

              {/* Max Iterations */}
              <div>
                <label
                  htmlFor="max-iterations"
                  className="mb-2 block text-sm font-medium text-white"
                >
                  Max Iterations (1-10) <span className="text-red-400">*</span>
                </label>
                <input
                  type="number"
                  id="max-iterations"
                  value={maxIterations}
                  onChange={(e) => setMaxIterations(Number(e.target.value))}
                  min={1}
                  max={10}
                  className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2.5 text-white focus:border-white focus:outline-none focus:ring-2 focus:ring-white/20"
                  required
                />
                <p className="mt-1 text-xs text-gray-400">
                  Maximum number of improvement cycles
                </p>
              </div>

              {/* Scenarios with Weights */}
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <label className="block text-sm font-medium text-white">
                    Scenarios & Weights <span className="text-red-400">*</span>
                  </label>
                  <button
                    type="button"
                    onClick={handleAddScenario}
                    disabled={
                      selectedScenarios.length >= scenarios.length ||
                      scenarios.length === 0
                    }
                    className="flex items-center gap-1 rounded-lg bg-white px-3 py-1.5 text-sm font-medium text-black hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <Plus className="h-4 w-4" />
                    Add Scenario
                  </button>
                </div>

                {selectedScenarios.length === 0 ? (
                  <div className="rounded-lg border border-zinc-700 bg-zinc-800 p-4 text-center">
                    <p className="text-gray-400">
                      Click "Add Scenario" to start
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {selectedScenarios.map((scenarioWeight, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-3 rounded-lg border border-zinc-700 bg-zinc-800 p-3"
                      >
                        {/* Scenario Selector */}
                        <select
                          value={scenarioWeight.scenario_id}
                          onChange={(e) =>
                            handleScenarioChange(index, e.target.value)
                          }
                          className="flex-1 rounded-lg border border-zinc-600 bg-zinc-700 px-3 py-2 text-sm text-white focus:border-white focus:outline-none"
                        >
                          {scenarios.map((scenario) => (
                            <option key={scenario._id} value={scenario._id}>
                              {scenario.title}
                            </option>
                          ))}
                        </select>

                        {/* Weight Selector */}
                        <div className="flex items-center gap-2">
                          <label className="text-sm text-gray-400">
                            Weight:
                          </label>
                          <select
                            value={scenarioWeight.weight}
                            onChange={(e) =>
                              handleWeightChange(index, Number(e.target.value))
                            }
                            className="rounded-lg border border-zinc-600 bg-zinc-700 px-3 py-2 text-sm text-white focus:border-white focus:outline-none"
                          >
                            {[1, 2, 3, 4, 5].map((w) => (
                              <option key={w} value={w}>
                                {w}
                              </option>
                            ))}
                          </select>
                        </div>

                        {/* Remove Button */}
                        <button
                          type="button"
                          onClick={() => handleRemoveScenario(index)}
                          className="rounded-lg p-2 text-red-400 hover:bg-red-950/20 hover:text-red-300"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                <p className="mt-2 text-xs text-gray-400">
                  Weight: 1 (Low Priority) → 5 (High Priority)
                </p>
              </div>

              {/* Submit Button */}
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={onClose}
                  className="rounded-lg border border-zinc-700 bg-zinc-800 px-6 py-2.5 font-medium text-white hover:bg-zinc-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || selectedScenarios.length === 0}
                  className="flex items-center gap-2 rounded-lg bg-white px-6 py-2.5 font-medium text-black hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Starting...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4" />
                      Start Tuning Loop
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
