/**
 * PromptModal Component
 * Modal for creating and editing agent system prompts
 */
"use client";

import { useState, useEffect } from "react";
import { Prompt, PromptCreate } from "@/types/library";
import { X } from "lucide-react";

interface PromptModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: PromptCreate) => Promise<void>;
  prompt?: Prompt | null; // If provided, modal is in edit mode
}

export default function PromptModal({
  isOpen,
  onClose,
  onSubmit,
  prompt,
}: PromptModalProps) {
  const isEditMode = !!prompt;

  const [formData, setFormData] = useState<PromptCreate>({
    name: "",
    prompt_text: "",
    version: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when modal opens/closes or prompt changes
  useEffect(() => {
    if (isOpen) {
      if (prompt) {
        // Edit mode - populate with existing data
        setFormData({
          name: prompt.name,
          prompt_text: prompt.prompt_text,
          version: prompt.version,
        });
      } else {
        // Create mode - reset to empty
        setFormData({
          name: "",
          prompt_text: "",
          version: "",
        });
      }
      setErrors({});
    }
  }, [isOpen, prompt]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
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

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    } else if (formData.name.length > 100) {
      newErrors.name = "Name must be 100 characters or less";
    }

    if (!formData.version.trim()) {
      newErrors.version = "Version is required";
    } else if (formData.version.length > 50) {
      newErrors.version = "Version must be 50 characters or less";
    }

    if (!formData.prompt_text.trim()) {
      newErrors.prompt_text = "Prompt text is required";
    } else if (formData.prompt_text.length < 10) {
      newErrors.prompt_text = "Prompt text must be at least 10 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      console.error("Error submitting prompt:", error);
      setErrors({
        submit: error instanceof Error ? error.message : "Failed to save prompt",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-lg bg-zinc-900 shadow-2xl border border-white/10">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 p-6 bg-zinc-950">
          <h2 className="text-2xl font-bold text-white">
            {isEditMode ? "Edit Prompt" : "Create New Prompt"}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
            disabled={isSubmitting}
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          {errors.submit && (
            <div className="mb-4 rounded-lg border border-red-500/50 bg-red-950/30 p-4 text-sm text-red-400">
              {errors.submit}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            {/* Name */}
            <div className="mb-4">
              <label
                htmlFor="name"
                className="mb-2 block text-sm font-medium text-gray-300"
              >
                Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className={`w-full rounded-lg border ${
                  errors.name ? "border-red-500" : "border-white/10"
                } bg-zinc-950 text-white px-4 py-2 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20`}
                placeholder="e.g., v1.1-empathetic"
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-400">{errors.name}</p>
              )}
            </div>

            {/* Version */}
            <div className="mb-4">
              <label
                htmlFor="version"
                className="mb-2 block text-sm font-medium text-gray-300"
              >
                Version <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="version"
                name="version"
                value={formData.version}
                onChange={handleInputChange}
                className={`w-full rounded-lg border ${
                  errors.version ? "border-red-500" : "border-white/10"
                } bg-zinc-950 text-white px-4 py-2 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20`}
                placeholder="e.g., 1.1"
              />
              {errors.version && (
                <p className="mt-1 text-sm text-red-400">{errors.version}</p>
              )}
            </div>
          </div>

          {/* Prompt Text */}
          <div className="mb-6">
            <label
              htmlFor="prompt_text"
              className="mb-2 block text-sm font-medium text-gray-300"
            >
              System Prompt <span className="text-red-500">*</span>
            </label>
            <textarea
              id="prompt_text"
              name="prompt_text"
              value={formData.prompt_text}
              onChange={handleInputChange}
              rows={12}
              className={`w-full rounded-lg border ${
                errors.prompt_text ? "border-red-500" : "border-white/10"
              } bg-zinc-950 text-white px-4 py-2 font-mono text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20`}
              placeholder="You are an empathetic debt collection agent. Your goal is to help customers find a payment solution while maintaining a respectful and understanding tone..."
            />
            {errors.prompt_text && (
              <p className="mt-1 text-sm text-red-400">{errors.prompt_text}</p>
            )}
            <p className="mt-2 text-xs text-gray-400">
              {formData.prompt_text.length} characters
            </p>
          </div>

          {/* Buttons */}
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-border px-6 py-2 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground font-medium px-6 py-2 disabled:opacity-50 transition-colors"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? "Saving..."
                : isEditMode
                ? "Update Prompt"
                : "Create Prompt"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
