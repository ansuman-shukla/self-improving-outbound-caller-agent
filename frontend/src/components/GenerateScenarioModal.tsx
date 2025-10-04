/**
 * GenerateScenarioModal Component
 * Modal for generating new scenarios using AI
 */
"use client";

import { useState, useEffect } from "react";
import { Personality } from "@/types/library";
import { ScenarioCreate } from "@/types/scenario";
import { Sparkles, Loader2, X } from "lucide-react";

interface GenerateScenarioModalProps {
  isOpen: boolean;
  onClose: () => void;
  personalities: Personality[];
  onGenerate: (data: ScenarioCreate) => Promise<void>;
  isLoading: boolean;
}

export default function GenerateScenarioModal({
  isOpen,
  onClose,
  personalities,
  onGenerate,
  isLoading,
}: GenerateScenarioModalProps) {
  const [formData, setFormData] = useState<ScenarioCreate>({
    personality_id: "",
    brief: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setFormData({
        personality_id: "",
        brief: "",
      });
      setErrors({});
    }
  }, [isOpen]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.personality_id) {
      newErrors.personality_id = "Please select a personality";
    }

    if (!formData.brief.trim()) {
      newErrors.brief = "Brief is required";
    } else if (formData.brief.length > 500) {
      newErrors.brief = "Brief must be 500 characters or less";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      await onGenerate(formData);
      onClose();
    } catch (error) {
      console.error("Error generating scenario:", error);
      setErrors({ submit: error instanceof Error ? error.message : "Failed to generate scenario" });
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="relative w-full max-w-2xl bg-zinc-900 rounded-lg shadow-2xl border border-zinc-800 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-white" />
            <h2 className="text-2xl font-bold text-white">Generate New Scenario with AI</h2>
          </div>
          <button
            onClick={handleClose}
            disabled={isLoading}
            className="text-zinc-400 hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Body - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Personality Dropdown */}
            <div>
              <label htmlFor="personality_id" className="block text-sm font-medium text-zinc-300 mb-2">
                Select Personality <span className="text-white">*</span>
              </label>
              <select
                id="personality_id"
                name="personality_id"
                value={formData.personality_id}
                onChange={handleInputChange}
                disabled={isLoading}
                className={`w-full px-4 py-3 bg-zinc-800 border ${
                  errors.personality_id ? "border-zinc-600" : "border-zinc-700"
                } rounded-md text-white focus:outline-none focus:ring-2 focus:ring-white disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                <option value="">Choose a personality...</option>
                {personalities.map((personality) => (
                  <option key={personality._id} value={personality._id}>
                    {personality.name}
                  </option>
                ))}
              </select>
              {errors.personality_id && (
                <p className="mt-1 text-sm text-zinc-400">{errors.personality_id}</p>
              )}
              {personalities.length === 0 && (
                <p className="mt-1 text-sm text-zinc-400">
                  No personalities available. Create one in the Library first.
                </p>
              )}
            </div>

            {/* Brief Input */}
            <div>
              <label htmlFor="brief" className="block text-sm font-medium text-zinc-300 mb-2">
                Situation Brief <span className="text-white">*</span>
              </label>
              <textarea
                id="brief"
                name="brief"
                value={formData.brief}
                onChange={handleInputChange}
                disabled={isLoading}
                rows={4}
                placeholder="e.g., just lost their job, medical emergency, going through divorce..."
                className={`w-full px-4 py-3 bg-zinc-800 border ${
                  errors.brief ? "border-zinc-600" : "border-zinc-700"
                } rounded-md text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-white resize-none disabled:opacity-50 disabled:cursor-not-allowed`}
              />
              <div className="flex justify-between mt-1">
                <div>
                  {errors.brief && (
                    <p className="text-sm text-zinc-400">{errors.brief}</p>
                  )}
                </div>
                <p className="text-sm text-zinc-500">
                  {formData.brief.length}/500
                </p>
              </div>
              <p className="mt-1 text-xs text-zinc-500">
                Provide a brief description of the debtor's situation. AI will generate a detailed backstory and objective.
              </p>
            </div>

            {/* Submit Error */}
            {errors.submit && (
              <div className="p-3 bg-zinc-800 border border-zinc-700 rounded-md">
                <p className="text-sm text-zinc-300">{errors.submit}</p>
              </div>
            )}

            {/* Info Box */}
            {isLoading && (
              <div className="p-4 bg-zinc-800 border border-zinc-700 rounded-md">
                <p className="text-sm text-zinc-300">
                  🤖 AI is generating a detailed scenario based on your personality and brief. This usually takes 6-11 seconds...
                </p>
              </div>
            )}
          </form>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-zinc-800 bg-zinc-950">
          <button
            type="button"
            onClick={handleClose}
            disabled={isLoading}
            className="px-4 py-2 border border-zinc-700 text-zinc-300 rounded-md hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={(e) => handleSubmit(e as any)}
            disabled={isLoading || personalities.length === 0}
            className="px-6 py-2 bg-white hover:bg-zinc-200 disabled:bg-zinc-700 disabled:cursor-not-allowed text-black font-medium rounded-md transition-colors flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate Scenario</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
