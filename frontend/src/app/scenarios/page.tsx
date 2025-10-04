/**
 * Scenario Designer Page
 * Main page for generating and managing test scenarios using AI
 * Part of Phase 2, Module 2: The Scenario Designer
 */
"use client";

import { useState, useEffect } from "react";
import { Sparkles, Plus } from "lucide-react";
import ScenarioCard from "@/components/ScenarioCard";
import GenerateScenarioModal from "@/components/GenerateScenarioModal";
import EditScenarioModal from "@/components/EditScenarioModal";
import {
  getPersonalities,
  getScenarios,
  generateScenario,
  updateScenario,
  deleteScenario,
} from "@/lib/api";
import { Personality } from "@/types/library";
import {
  Scenario,
  ScenarioCreate,
  ScenarioUpdate,
  ScenarioWithPersonality,
} from "@/types/scenario";

export default function ScenarioDesignerPage() {
  // State for personalities (needed for dropdown)
  const [personalities, setPersonalities] = useState<Personality[]>([]);
  const [isLoadingPersonalities, setIsLoadingPersonalities] = useState(true);

  // State for scenarios
  const [scenarios, setScenarios] = useState<ScenarioWithPersonality[]>([]);
  const [isLoadingScenarios, setIsLoadingScenarios] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

  // State for modals
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingScenario, setEditingScenario] = useState<Scenario | null>(null);

  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Fetch personalities on mount
  useEffect(() => {
    fetchPersonalities();
  }, []);

  // Fetch scenarios on mount
  useEffect(() => {
    fetchScenarios();
  }, []);

  const fetchPersonalities = async () => {
    try {
      setIsLoadingPersonalities(true);
      setError(null);
      const response = await getPersonalities();
      setPersonalities(response.personalities);
    } catch (err) {
      console.error("Error fetching personalities:", err);
      setError(
        err instanceof Error ? err.message : "Failed to load personalities"
      );
    } finally {
      setIsLoadingPersonalities(false);
    }
  };

  const fetchScenarios = async () => {
    try {
      setIsLoadingScenarios(true);
      setError(null);
      const scenariosData = await getScenarios();
      
      // Enrich scenarios with personality names
      const enrichedScenarios: ScenarioWithPersonality[] = scenariosData.map(
        (scenario) => {
          const personality = personalities.find(
            (p) => p._id === scenario.personality_id
          );
          return {
            ...scenario,
            personality_name: personality?.name || "Unknown",
          };
        }
      );
      
      setScenarios(enrichedScenarios);
    } catch (err) {
      console.error("Error fetching scenarios:", err);
      setError(err instanceof Error ? err.message : "Failed to load scenarios");
    } finally {
      setIsLoadingScenarios(false);
    }
  };

  // Re-enrich scenarios when personalities change
  useEffect(() => {
    if (personalities.length > 0 && scenarios.length > 0) {
      const enrichedScenarios: ScenarioWithPersonality[] = scenarios.map(
        (scenario) => {
          const personality = personalities.find(
            (p) => p._id === scenario.personality_id
          );
          return {
            ...scenario,
            personality_name: personality?.name || "Unknown",
          };
        }
      );
      setScenarios(enrichedScenarios);
    }
  }, [personalities]);

  const handleGenerateScenario = async (data: ScenarioCreate) => {
    try {
      setIsGenerating(true);
      setError(null);
      setSuccessMessage(null);
      
      const newScenario = await generateScenario(data);
      
      // Enrich with personality name
      const personality = personalities.find((p) => p._id === newScenario.personality_id);
      const enrichedScenario: ScenarioWithPersonality = {
        ...newScenario,
        personality_name: personality?.name || "Unknown",
      };
      
      setScenarios([enrichedScenario, ...scenarios]);
      setSuccessMessage(
        `✨ Scenario "${newScenario.title}" generated successfully!`
      );
      
      // Close the modal
      setIsGenerateModalOpen(false);
      
      // Clear success message after 5 seconds
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      console.error("Error generating scenario:", err);
      setError(
        err instanceof Error ? err.message : "Failed to generate scenario"
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleUpdateScenario = async (data: ScenarioUpdate) => {
    if (!editingScenario) return;
    
    try {
      const updated = await updateScenario(editingScenario._id, data);
      
      // Enrich with personality name
      const personality = personalities.find((p) => p._id === updated.personality_id);
      const enrichedUpdated: ScenarioWithPersonality = {
        ...updated,
        personality_name: personality?.name || "Unknown",
      };
      
      setScenarios(
        scenarios.map((s) => (s._id === enrichedUpdated._id ? enrichedUpdated : s))
      );
      setEditingScenario(null);
      setSuccessMessage(`✅ Scenario "${updated.title}" updated successfully!`);
      
      // Clear success message after 5 seconds
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      console.error("Error updating scenario:", err);
      setError(err instanceof Error ? err.message : "Failed to update scenario");
    }
  };

  const handleDeleteScenario = async (id: string) => {
    try {
      await deleteScenario(id);
      setScenarios(scenarios.filter((s) => s._id !== id));
      setSuccessMessage("🗑️ Scenario deleted successfully!");
      
      // Clear success message after 5 seconds
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      console.error("Error deleting scenario:", err);
      setError(err instanceof Error ? err.message : "Failed to delete scenario");
    }
  };

  const handleEditScenario = (scenario: ScenarioWithPersonality) => {
    setEditingScenario(scenario);
    setIsEditModalOpen(true);
  };

  return (
    <main className="min-h-screen bg-zinc-950 text-white p-8">
      <div className="max-w-7xl mx-auto pb-24">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <Sparkles className="w-8 h-8 text-white" />
              <h1 className="text-4xl font-bold text-white">Scenarios</h1>
            </div>
            <div className="px-3 py-1.5 bg-zinc-800 border border-zinc-700 text-zinc-300 text-sm rounded-full">
              {scenarios.length} {scenarios.length === 1 ? "scenario" : "scenarios"}
            </div>
          </div>
          <p className="text-zinc-400 text-lg">
            AI-generated test scenarios with detailed backstories and objectives for realistic outbound call simulations.
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-zinc-800 border border-zinc-700 rounded-lg">
            <p className="text-zinc-300">{error}</p>
          </div>
        )}

        {/* Success Message */}
        {successMessage && (
          <div className="mb-6 p-4 bg-zinc-800 border border-zinc-700 rounded-lg">
            <p className="text-white">{successMessage}</p>
          </div>
        )}

        {/* Scenarios Grid */}
        {isLoadingScenarios ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-white border-r-transparent mb-4"></div>
              <p className="text-zinc-400">Loading scenarios...</p>
            </div>
          </div>
        ) : scenarios.length === 0 ? (
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-12 text-center">
            <Sparkles className="h-12 w-12 text-zinc-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No scenarios yet</h3>
            <p className="text-zinc-400 mb-6">
              Click the "Generate Scenario" button to create your first AI-powered test scenario.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scenarios.map((scenario) => (
              <ScenarioCard
                key={scenario._id}
                scenario={scenario}
                onEdit={handleEditScenario}
                onDelete={handleDeleteScenario}
              />
            ))}
          </div>
        )}

        {/* Floating Action Button */}
        <button
          onClick={() => setIsGenerateModalOpen(true)}
          className="fixed bottom-8 right-8 bg-white hover:bg-zinc-200 text-black font-medium px-6 py-4 rounded-full shadow-2xl flex items-center gap-2 transition-all hover:scale-105 z-40"
          title="Generate new scenario"
        >
          <Plus className="w-5 h-5" />
          <span>Generate Scenario</span>
        </button>

        {/* Generate Modal */}
        <GenerateScenarioModal
          isOpen={isGenerateModalOpen}
          onClose={() => setIsGenerateModalOpen(false)}
          personalities={personalities}
          onGenerate={handleGenerateScenario}
          isLoading={isGenerating}
        />

        {/* Edit Modal */}
        <EditScenarioModal
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false);
            setEditingScenario(null);
          }}
          onSubmit={handleUpdateScenario}
          scenario={editingScenario}
        />
      </div>
    </main>
  );
}

