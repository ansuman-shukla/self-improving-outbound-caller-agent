/**
 * ScenarioTable Component
 * Displays all scenarios in a table format with view, edit and delete actions
 */
"use client";

import { useState } from "react";
import { ScenarioWithPersonality } from "@/types/scenario";
import { Pencil, Trash2, Eye, Star } from "lucide-react";
import { format } from "date-fns";

interface ScenarioTableProps {
  scenarios: ScenarioWithPersonality[];
  onEdit: (scenario: ScenarioWithPersonality) => void;
  onDelete: (id: string) => void;
  isLoading?: boolean;
}

export default function ScenarioTable({
  scenarios,
  onEdit,
  onDelete,
  isLoading = false,
}: ScenarioTableProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const handleDelete = (id: string) => {
    if (deleteConfirmId === id) {
      // Confirmed, proceed with deletion
      onDelete(id);
      setDeleteConfirmId(null);
    } else {
      // Show confirmation
      setDeleteConfirmId(id);
      // Auto-cancel after 3 seconds
      setTimeout(() => setDeleteConfirmId(null), 3000);
    }
  };

  const renderWeightStars = (weight: number) => {
    return (
      <div className="flex items-center gap-0.5" title={`Weight: ${weight}/5`}>
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            className={`h-3 w-3 ${
              i < weight
                ? "fill-white text-white"
                : "fill-zinc-700 text-zinc-700"
            }`}
          />
        ))}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-white border-r-transparent"></div>
          <p className="mt-2 text-gray-400">Loading scenarios...</p>
        </div>
      </div>
    );
  }

  if (scenarios.length === 0) {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-8 text-center">
        <p className="text-gray-400">
          No scenarios found. Generate your first scenario to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-zinc-800 bg-zinc-900 shadow-xl">
      <table className="min-w-full divide-y divide-zinc-800">
        <thead className="bg-zinc-950">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
              Title
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
              Personality
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
              Brief
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
              Weight
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
              Created
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-zinc-400">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800 bg-zinc-900">
          {scenarios.map((scenario) => (
            <tr key={scenario._id} className="hover:bg-zinc-800 transition-colors">
              <td className="px-6 py-4">
                <div className="max-w-xs">
                  <div className="text-sm font-medium text-white truncate">
                    {scenario.title}
                  </div>
                  {expandedId === scenario._id && (
                    <div className="mt-3 space-y-3 rounded-lg bg-zinc-950 p-4 border border-zinc-800">
                      <div>
                        <div className="text-xs font-medium text-zinc-400 mb-1">
                          BACKSTORY:
                        </div>
                        <div className="text-sm text-zinc-300 leading-relaxed">
                          {scenario.backstory}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs font-medium text-zinc-400 mb-1">
                          OBJECTIVE:
                        </div>
                        <div className="text-sm text-zinc-300 leading-relaxed">
                          {scenario.objective}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="text-sm text-zinc-400">
                  {scenario.personality_name || "Unknown"}
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="max-w-xs text-sm text-zinc-500 truncate" title={scenario.brief}>
                  {scenario.brief}
                </div>
              </td>
              <td className="px-6 py-4">
                {renderWeightStars(scenario.weight)}
              </td>
              <td className="whitespace-nowrap px-6 py-4 text-sm text-zinc-400">
                {format(new Date(scenario.created_at), "MMM d, yyyy")}
              </td>
              <td className="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => toggleExpand(scenario._id)}
                    className="text-zinc-400 hover:text-white transition-colors"
                    title={expandedId === scenario._id ? "Hide details" : "View details"}
                  >
                    <Eye className={`h-4 w-4 ${expandedId === scenario._id ? "fill-white" : ""}`} />
                  </button>
                  <button
                    onClick={() => onEdit(scenario)}
                    className="text-zinc-400 hover:text-white transition-colors"
                    title="Edit scenario"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(scenario._id)}
                    className={`${
                      deleteConfirmId === scenario._id
                        ? "text-zinc-300 animate-pulse"
                        : "text-zinc-400 hover:text-white"
                    } transition-colors`}
                    title={
                      deleteConfirmId === scenario._id
                        ? "Click again to confirm"
                        : "Delete scenario"
                    }
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
