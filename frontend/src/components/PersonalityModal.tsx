/**
 * PersonalityModal Component
 * Modal for creating and editing personalities with dynamic core traits
 */
"use client";

import { useState, useEffect } from "react";
import { Personality, PersonalityCreate } from "@/types/library";
import { X, Plus, Trash2 } from "lucide-react";

interface PersonalityModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: PersonalityCreate) => Promise<void>;
  personality?: Personality | null; // If provided, modal is in edit mode
}

export default function PersonalityModal({
  isOpen,
  onClose,
  onSubmit,
  personality,
}: PersonalityModalProps) {
  const isEditMode = !!personality;

  const [formData, setFormData] = useState<PersonalityCreate>({
    name: "",
    description: "",
    core_traits: {},
    system_prompt: "",
  });

  const [traits, setTraits] = useState<Array<{ key: string; value: string }>>([
    { key: "", value: "" },
  ]);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when modal opens/closes or personality changes
  useEffect(() => {
    if (isOpen) {
      if (personality) {
        // Edit mode - populate with existing data
        setFormData({
          name: personality.name,
          description: personality.description,
          core_traits: personality.core_traits,
          system_prompt: personality.system_prompt,
          amount: personality.amount,
        });
        // Convert core_traits object to array for UI
        const traitsArray = Object.entries(personality.core_traits).map(
          ([key, value]) => ({ key, value })
        );
        setTraits(traitsArray.length > 0 ? traitsArray : [{ key: "", value: "" }]);
      } else {
        // Create mode - reset to empty
        setFormData({
          name: "",
          description: "",
          core_traits: {},
          system_prompt: "",
          amount: undefined,
        });
        setTraits([{ key: "", value: "" }]);
      }
      setErrors({});
    }
  }, [isOpen, personality]);

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

  const handleTraitChange = (
    index: number,
    field: "key" | "value",
    value: string
  ) => {
    const newTraits = [...traits];
    newTraits[index][field] = value;
    setTraits(newTraits);

    // Update core_traits in formData
    const core_traits: Record<string, string> = {};
    newTraits.forEach((trait) => {
      if (trait.key && trait.value) {
        core_traits[trait.key] = trait.value;
      }
    });
    setFormData((prev) => ({ ...prev, core_traits }));
  };

  const addTrait = () => {
    setTraits([...traits, { key: "", value: "" }]);
  };

  const removeTrait = (index: number) => {
    if (traits.length > 1) {
      const newTraits = traits.filter((_, i) => i !== index);
      setTraits(newTraits);

      // Update core_traits
      const core_traits: Record<string, string> = {};
      newTraits.forEach((trait) => {
        if (trait.key && trait.value) {
          core_traits[trait.key] = trait.value;
        }
      });
      setFormData((prev) => ({ ...prev, core_traits }));
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    } else if (formData.name.length > 100) {
      newErrors.name = "Name must be 100 characters or less";
    }

    if (!formData.description.trim()) {
      newErrors.description = "Description is required";
    } else if (formData.description.length > 500) {
      newErrors.description = "Description must be 500 characters or less";
    }

    if (Object.keys(formData.core_traits).length === 0) {
      newErrors.core_traits = "At least one core trait is required";
    }

    if (!formData.system_prompt.trim()) {
      newErrors.system_prompt = "System prompt is required";
    } else if (formData.system_prompt.length < 10) {
      newErrors.system_prompt = "System prompt must be at least 10 characters";
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
      console.error("Error submitting personality:", error);
      setErrors({
        submit:
          error instanceof Error ? error.message : "Failed to save personality",
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
            {isEditMode ? "Edit Personality" : "Create New Personality"}
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
              placeholder="e.g., Willful Defaulter"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-400">{errors.name}</p>
            )}
          </div>

          {/* Description */}
          <div className="mb-4">
            <label
              htmlFor="description"
              className="mb-2 block text-sm font-medium text-gray-300"
            >
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows={2}
              className={`w-full rounded-lg border ${
                errors.description ? "border-red-500" : "border-white/10"
              } bg-zinc-950 text-white px-4 py-2 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20`}
              placeholder="A person who has the means to pay but is avoiding payment"
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-400">{errors.description}</p>
            )}
          </div>

          {/* Pending Debt Amount */}
          <div className="mb-4">
            <label
              htmlFor="amount"
              className="mb-2 block text-sm font-medium text-gray-300"
            >
              Pending Debt Amount (₹) <span className="text-gray-500 text-xs ml-1">(Optional)</span>
            </label>
            <input
              type="number"
              id="amount"
              name="amount"
              value={formData.amount || ""}
              onChange={(e) => {
                const value = e.target.value ? parseFloat(e.target.value) : undefined;
                setFormData((prev) => ({ ...prev, amount: value }));
              }}
              min="0"
              step="0.01"
              className={`w-full rounded-lg border ${
                errors.amount ? "border-red-500" : "border-white/10"
              } bg-zinc-950 text-white px-4 py-2 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20`}
              placeholder="e.g., 5000.00"
            />
            <p className="mt-1 text-xs text-gray-500">
              This amount will be used in conversation simulations to replace {"{amount}"} variable
            </p>
            {errors.amount && (
              <p className="mt-1 text-sm text-red-400">{errors.amount}</p>
            )}
          </div>

          {/* Core Traits */}
          <div className="mb-4">
            <label className="mb-2 block text-sm font-medium text-gray-300">
              Core Traits <span className="text-red-500">*</span>
            </label>
            <div className="space-y-2">
              {traits.map((trait, index) => (
                <div key={index} className="flex gap-2">
                  <input
                    type="text"
                    value={trait.key}
                    onChange={(e) =>
                      handleTraitChange(index, "key", e.target.value)
                    }
                    className="flex-1 rounded-lg border border-white/10 bg-zinc-950 text-white px-4 py-2 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                    placeholder="Trait name (e.g., Attitude)"
                  />
                  <input
                    type="text"
                    value={trait.value}
                    onChange={(e) =>
                      handleTraitChange(index, "value", e.target.value)
                    }
                    className="flex-1 rounded-lg border border-white/10 bg-zinc-950 text-white px-4 py-2 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                    placeholder="Trait value (e.g., Cynical)"
                  />
                  <button
                    type="button"
                    onClick={() => removeTrait(index)}
                    className="rounded-lg px-3 py-2 text-muted-foreground hover:bg-destructive/20 hover:text-destructive disabled:opacity-50 transition-colors"
                    disabled={traits.length === 1}
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={addTrait}
              className="mt-2 flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors"
            >
              <Plus className="h-4 w-4" />
              Add Another Trait
            </button>
            {errors.core_traits && (
              <p className="mt-1 text-sm text-red-400">{errors.core_traits}</p>
            )}
          </div>

          {/* System Prompt */}
          <div className="mb-6">
            <label
              htmlFor="system_prompt"
              className="mb-2 block text-sm font-medium text-gray-300"
            >
              System Prompt <span className="text-red-500">*</span>
            </label>
            <textarea
              id="system_prompt"
              name="system_prompt"
              value={formData.system_prompt}
              onChange={handleInputChange}
              rows={6}
              className={`w-full rounded-lg border ${
                errors.system_prompt ? "border-red-500" : "border-white/10"
              } bg-zinc-950 text-white px-4 py-2 font-mono text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20`}
              placeholder="You are a debtor who has the financial means to pay but is choosing not to. You make excuses and try to avoid commitment..."
            />
            {errors.system_prompt && (
              <p className="mt-1 text-sm text-red-400">{errors.system_prompt}</p>
            )}
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
                ? "Update Personality"
                : "Create Personality"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
