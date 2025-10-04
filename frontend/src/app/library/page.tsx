/**
 * Library Hub Page
 * Main page for managing Personalities and Prompts
 * Features a two-tab layout for easy navigation between the two types of assets
 */
"use client";

import { useState, useEffect } from "react";
import { Plus } from "lucide-react";
import PersonalityTable from "@/components/PersonalityTable";
import PersonalityModal from "@/components/PersonalityModal";
import PromptTable from "@/components/PromptTable";
import PromptModal from "@/components/PromptModal";
import {
  getPersonalities,
  createPersonality,
  updatePersonality,
  deletePersonality,
  getPrompts,
  createPrompt,
  updatePrompt,
  deletePrompt,
} from "@/lib/api";
import {
  Personality,
  PersonalityCreate,
  Prompt,
  PromptCreate,
} from "@/types/library";

type TabType = "personalities" | "prompts";

export default function LibraryPage() {
  const [activeTab, setActiveTab] = useState<TabType>("personalities");

  // Personalities state
  const [personalities, setPersonalities] = useState<Personality[]>([]);
  const [isLoadingPersonalities, setIsLoadingPersonalities] = useState(true);
  const [isPersonalityModalOpen, setIsPersonalityModalOpen] = useState(false);
  const [editingPersonality, setEditingPersonality] =
    useState<Personality | null>(null);

  // Prompts state
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [isLoadingPrompts, setIsLoadingPrompts] = useState(true);
  const [isPromptModalOpen, setIsPromptModalOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);

  const [error, setError] = useState<string | null>(null);

  // Fetch personalities on mount
  useEffect(() => {
    fetchPersonalities();
  }, []);

  // Fetch prompts on mount
  useEffect(() => {
    fetchPrompts();
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

  const fetchPrompts = async () => {
    try {
      setIsLoadingPrompts(true);
      setError(null);
      const response = await getPrompts();
      setPrompts(response.prompts);
    } catch (err) {
      console.error("Error fetching prompts:", err);
      setError(err instanceof Error ? err.message : "Failed to load prompts");
    } finally {
      setIsLoadingPrompts(false);
    }
  };

  // Personality handlers
  const handleCreatePersonality = async (data: PersonalityCreate) => {
    const newPersonality = await createPersonality(data);
    setPersonalities([...personalities, newPersonality]);
  };

  const handleUpdatePersonality = async (data: PersonalityCreate) => {
    if (!editingPersonality) return;
    const updated = await updatePersonality(editingPersonality._id, data);
    setPersonalities(
      personalities.map((p) => (p._id === updated._id ? updated : p))
    );
    setEditingPersonality(null);
  };

  const handleDeletePersonality = async (id: string) => {
    try {
      await deletePersonality(id);
      setPersonalities(personalities.filter((p) => p._id !== id));
    } catch (err) {
      console.error("Error deleting personality:", err);
      setError(
        err instanceof Error ? err.message : "Failed to delete personality"
      );
    }
  };

  const handleEditPersonality = (personality: Personality) => {
    setEditingPersonality(personality);
    setIsPersonalityModalOpen(true);
  };

  // Prompt handlers
  const handleCreatePrompt = async (data: PromptCreate) => {
    const newPrompt = await createPrompt(data);
    setPrompts([...prompts, newPrompt]);
  };

  const handleUpdatePrompt = async (data: PromptCreate) => {
    if (!editingPrompt) return;
    const updated = await updatePrompt(editingPrompt._id, data);
    setPrompts(prompts.map((p) => (p._id === updated._id ? updated : p)));
    setEditingPrompt(null);
  };

  const handleDeletePrompt = async (id: string) => {
    try {
      await deletePrompt(id);
      setPrompts(prompts.filter((p) => p._id !== id));
    } catch (err) {
      console.error("Error deleting prompt:", err);
      setError(err instanceof Error ? err.message : "Failed to delete prompt");
    }
  };

  const handleEditPrompt = (prompt: Prompt) => {
    setEditingPrompt(prompt);
    setIsPromptModalOpen(true);
  };

  const closePersonalityModal = () => {
    setIsPersonalityModalOpen(false);
    setEditingPersonality(null);
  };

  const closePromptModal = () => {
    setIsPromptModalOpen(false);
    setEditingPrompt(null);
  };

  return (
    <div className="min-h-screen bg-black p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Library Hub</h1>
        <p className="mt-2 text-gray-400">
          Manage debtor personalities and agent prompts for your evaluations
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 rounded-lg border border-red-500/50 bg-red-950/30 p-4 text-red-400">
          <p className="font-medium">Error</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex space-x-1 rounded-lg bg-card p-1 shadow-sm border border-border">
          <button
            onClick={() => setActiveTab("personalities")}
            className={`rounded-lg px-6 py-2 text-sm font-medium transition-colors ${
              activeTab === "personalities"
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-accent"
            }`}
          >
            Personalities
            <span className={`ml-2 rounded-full px-2 py-0.5 text-xs ${
              activeTab === "personalities" 
                ? "bg-primary-foreground/20" 
                : "bg-muted text-muted-foreground"
            }`}>
              {personalities.length}
            </span>
          </button>
          <button
            onClick={() => setActiveTab("prompts")}
            className={`rounded-lg px-6 py-2 text-sm font-medium transition-colors ${
              activeTab === "prompts"
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-accent"
            }`}
          >
            Agent Prompts
            <span className={`ml-2 rounded-full px-2 py-0.5 text-xs ${
              activeTab === "prompts" 
                ? "bg-primary-foreground/20" 
                : "bg-muted text-muted-foreground"
            }`}>
              {prompts.length}
            </span>
          </button>
        </div>

        {/* Create Button */}
        <button
          onClick={() => {
            if (activeTab === "personalities") {
              setEditingPersonality(null);
              setIsPersonalityModalOpen(true);
            } else {
              setEditingPrompt(null);
              setIsPromptModalOpen(true);
            }
          }}
          className="flex items-center gap-2 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground font-medium px-4 py-2 transition-colors"
        >
          <Plus className="h-5 w-5" />
          Create New {activeTab === "personalities" ? "Personality" : "Prompt"}
        </button>
      </div>

      {/* Content */}
      {activeTab === "personalities" ? (
        <PersonalityTable
          personalities={personalities}
          onEdit={handleEditPersonality}
          onDelete={handleDeletePersonality}
          isLoading={isLoadingPersonalities}
        />
      ) : (
        <PromptTable
          prompts={prompts}
          onEdit={handleEditPrompt}
          onDelete={handleDeletePrompt}
          isLoading={isLoadingPrompts}
        />
      )}

      {/* Modals */}
      <PersonalityModal
        isOpen={isPersonalityModalOpen}
        onClose={closePersonalityModal}
        onSubmit={
          editingPersonality ? handleUpdatePersonality : handleCreatePersonality
        }
        personality={editingPersonality}
      />

      <PromptModal
        isOpen={isPromptModalOpen}
        onClose={closePromptModal}
        onSubmit={editingPrompt ? handleUpdatePrompt : handleCreatePrompt}
        prompt={editingPrompt}
      />
    </div>
  );
}

