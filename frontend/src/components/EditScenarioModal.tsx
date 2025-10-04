/**
 * EditScenarioModal Component
 * Modal for editing scenario backstory and weight
 */
"use client";

import { useState, useEffect } from "react";
import { Scenario, ScenarioUpdate } from "@/types/scenario";
import { X, Star } from "lucide-react";

interface EditScenarioModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ScenarioUpdate) => Promise<void>;
  scenario: Scenario | null;
}

export default function EditScenarioModal({
  isOpen,
  onClose,
  onSubmit,
  scenario,
}: EditScenarioModalProps) {
  const [formData, setFormData] = useState<ScenarioUpdate>({
    backstory: "",
    weight: 3,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when modal opens/closes or scenario changes
  useEffect(() => {
    if (isOpen && scenario) {
      setFormData({
        backstory: scenario.backstory,
        weight: scenario.weight,
      });
      setErrors({});
    }
  }, [isOpen, scenario]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLTextAreaElement>
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

  const handleWeightChange = (weight: number) => {
    setFormData((prev) => ({ ...prev, weight }));
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.backstory?.trim()) {
      newErrors.backstory = "Backstory is required";
    } else if (formData.backstory.length < 10) {
      newErrors.backstory = "Backstory must be at least 10 characters";
    } else if (formData.backstory.length > 2000) {
      newErrors.backstory = "Backstory must be 2000 characters or less";
    }

    if (!formData.weight || formData.weight < 1 || formData.weight > 5) {
      newErrors.weight = "Weight must be between 1 and 5";
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
      setIsSubmitting(true);
      await onSubmit(formData);
      onClose();
    } catch (error) {
      console.error("Error updating scenario:", error);
      setErrors({
        submit: error instanceof Error ? error.message : "Failed to update scenario",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  if (!isOpen || !scenario) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="relative w-full max-w-3xl bg-zinc-900 rounded-lg shadow-2xl border border-zinc-800 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-zinc-800">
          <div>
            <h2 className="text-2xl font-bold text-white">Edit Scenario</h2>
            <p className="text-sm text-zinc-400 mt-1">{scenario.title}</p>
          </div>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="text-zinc-400 hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Body - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Read-only Info */}
            <div className="space-y-3 p-4 bg-zinc-950 rounded-lg border border-zinc-800">
              <div>
                <label className="block text-xs font-medium text-zinc-500 mb-1">
                  ORIGINAL BRIEF
                </label>
                <p className="text-sm text-zinc-300">{scenario.brief}</p>
              </div>
              <div>
                <label className="block text-xs font-medium text-zinc-500 mb-1">
                  OBJECTIVE (READ-ONLY)
                </label>
                <p className="text-sm text-zinc-300">{scenario.objective}</p>
              </div>
            </div>

            {/* Editable Backstory */}
            <div>
              <label
                htmlFor="backstory"
                className="block text-sm font-medium text-zinc-300 mb-2"
              >
                Backstory <span className="text-white">*</span>
              </label>
              <textarea
                id="backstory"
                name="backstory"
                value={formData.backstory}
                onChange={handleInputChange}
                disabled={isSubmitting}
                rows={8}
                className={`w-full px-4 py-3 bg-zinc-800 border ${
                  errors.backstory ? "border-zinc-600" : "border-zinc-700"
                } rounded-md text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-white resize-none disabled:opacity-50 disabled:cursor-not-allowed font-mono text-sm leading-relaxed`}
              />
              <div className="flex justify-between mt-1">
                <div>
                  {errors.backstory && (
                    <p className="text-sm text-zinc-400">{errors.backstory}</p>
                  )}
                </div>
                <p className="text-sm text-zinc-500">
                  {formData.backstory?.length || 0}/2000
                </p>
              </div>
              <p className="mt-1 text-xs text-zinc-500">
                Edit the AI-generated backstory to add more details or refine the scenario.
              </p>
            </div>

            {/* Weight Selector */}
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">
                Importance Weight <span className="text-white">*</span>
              </label>
              <div className="flex items-center gap-2">
                {[1, 2, 3, 4, 5].map((weight) => (
                  <button
                    key={weight}
                    type="button"
                    onClick={() => handleWeightChange(weight)}
                    disabled={isSubmitting}
                    className="group relative disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Star
                      className={`h-8 w-8 transition-all ${
                        formData.weight && weight <= formData.weight
                          ? "fill-white text-white"
                          : "fill-zinc-700 text-zinc-700 group-hover:fill-zinc-500 group-hover:text-zinc-500"
                      }`}
                    />
                  </button>
                ))}
                <span className="ml-2 text-sm text-zinc-400">
                  {formData.weight}/5
                </span>
              </div>
              {errors.weight && (
                <p className="mt-1 text-sm text-zinc-400">{errors.weight}</p>
              )}
              <p className="mt-1 text-xs text-zinc-500">
                Set the importance of this scenario (1 = low, 5 = critical)
              </p>
            </div>

            {/* Submit Error */}
            {errors.submit && (
              <div className="p-3 bg-zinc-800 border border-zinc-700 rounded-md">
                <p className="text-sm text-zinc-300">{errors.submit}</p>
              </div>
            )}
          </form>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-zinc-800 bg-zinc-950">
          <button
            type="button"
            onClick={handleClose}
            disabled={isSubmitting}
            className="px-4 py-2 border border-zinc-700 text-zinc-300 rounded-md hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={(e) => handleSubmit(e as any)}
            disabled={isSubmitting}
            className="px-6 py-2 bg-white hover:bg-zinc-200 disabled:bg-zinc-700 disabled:cursor-not-allowed text-black font-medium rounded-md transition-colors"
          >
            {isSubmitting ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </div>
    </div>
  );
}
