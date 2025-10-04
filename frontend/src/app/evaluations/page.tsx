/**
 * Evaluation Hub Page
 * Main page for running manual evaluations and viewing results
 * Part of Phase 3, Module 3: The Manual Evaluation Engine
 */
"use client";

import { useState, useEffect } from "react";
import { TestTube2, RefreshCw } from "lucide-react";
import ManualEvaluationForm from "@/components/ManualEvaluationForm";
import EvaluationResultsTable from "@/components/EvaluationResultsTable";
import { listEvaluations, getPrompts, getScenarios } from "@/lib/api";
import { EvaluationWithDetails } from "@/types/evaluation";
import { Prompt } from "@/types/library";
import { Scenario } from "@/types/scenario";

export default function EvaluationHubPage() {
  const [evaluations, setEvaluations] = useState<EvaluationWithDetails[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  // For enriching evaluations with names
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch evaluations, prompts, and scenarios in parallel
      const [evaluationsData, promptsResponse, scenariosData] = await Promise.all([
        listEvaluations(),
        getPrompts(),
        getScenarios(),
      ]);
      
      setPrompts(promptsResponse.prompts);
      setScenarios(scenariosData);
      
      // Enrich evaluations with prompt and scenario names
      const enriched: EvaluationWithDetails[] = evaluationsData.map((evaluation) => {
        const prompt = promptsResponse.prompts.find((p) => p._id === evaluation.prompt_id);
        const scenario = scenariosData.find((s) => s._id === evaluation.scenario_id);
        
        return {
          ...evaluation,
          prompt_name: prompt?.name,
          scenario_title: scenario?.title,
        };
      });
      
      setEvaluations(enriched);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError(err instanceof Error ? err.message : "Failed to load evaluations");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEvaluationCreated = (resultId: string) => {
    setSuccessMessage(`✅ Evaluation started! ID: ${resultId}`);
    
    // Clear success message after 5 seconds
    setTimeout(() => setSuccessMessage(null), 5000);
    
    // Refresh the evaluations list
    fetchData();
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    setTimeout(() => setError(null), 5000);
  };

  const handleDelete = (id: string) => {
    // Optimistically remove from UI
    setEvaluations((prev) => prev.filter((e) => e._id !== id));
    setSuccessMessage("✅ Evaluation deleted successfully");
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  return (
    <div className="h-screen overflow-hidden bg-black p-8">
      <div className="mx-auto flex h-full max-w-7xl flex-col space-y-8">
        {/* Header */}
        <div className="flex flex-shrink-0 items-center justify-between">
          <div className="flex items-center gap-3">
            <TestTube2 className="h-8 w-8 text-white" />
            <div>
              <h1 className="text-3xl font-bold text-white">Evaluation Hub</h1>
              <p className="text-gray-400">
                Run manual evaluations and analyze agent performance
              </p>
            </div>
          </div>
          
          <button
            onClick={fetchData}
            disabled={isLoading}
            className="flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2 text-sm text-white transition-colors hover:bg-zinc-700 disabled:opacity-50"
            title="Refresh evaluations"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="flex-shrink-0 rounded-lg border border-green-900 bg-green-950/20 p-4">
            <p className="text-green-400">{successMessage}</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="flex-shrink-0 rounded-lg border border-red-900 bg-red-950/20 p-4">
            <p className="text-red-400">❌ {error}</p>
          </div>
        )}

        {/* Main Content */}
        <div className="grid min-h-0 flex-1 grid-cols-1 gap-8 lg:grid-cols-3">
          {/* Left: Evaluation Form */}
          <div className="lg:col-span-1 overflow-y-auto space-y-4">
            <ManualEvaluationForm
              onEvaluationCreated={handleEvaluationCreated}
              onError={handleError}
            />
            
            {/* Info Box */}
            <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
              <h3 className="mb-2 font-medium text-white">How it works:</h3>
              <ol className="list-inside list-decimal space-y-1 text-sm text-gray-400">
                <li>Select an agent prompt and a test scenario</li>
                <li>Click "Run Evaluation" to start a conversation simulation</li>
                <li>The system will automatically evaluate the transcript and provide scores</li>
                <li>View detailed results by clicking the eye icon on completed evaluations</li>
              </ol>
            </div>
          </div>

          {/* Right: Results Table */}
          <div className="lg:col-span-2 flex flex-col min-h-0">
            <div className="flex flex-col flex-1 rounded-lg border border-zinc-800 bg-zinc-900 p-6 shadow-xl overflow-hidden">
              <div className="mb-4 flex flex-shrink-0 items-center justify-between">
                <h2 className="text-xl font-semibold text-white">
                  Evaluation Results
                </h2>
                <span className="text-sm text-gray-400">
                  {evaluations.length} evaluation{evaluations.length !== 1 ? "s" : ""}
                </span>
              </div>
              
              <div className="flex-1 overflow-y-auto min-h-0">
                <EvaluationResultsTable
                  evaluations={evaluations}
                  onDelete={handleDelete}
                  onRefresh={fetchData}
                  isLoading={isLoading}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

