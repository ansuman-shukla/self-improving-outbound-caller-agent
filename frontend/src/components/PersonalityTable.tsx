/**
 * PersonalityTable Component
 * Displays all personalities in a table format with edit and delete actions
 */
"use client";

import { useState } from "react";
import { Personality } from "@/types/library";
import { Pencil, Trash2, Eye } from "lucide-react";
import { format } from "date-fns";

interface PersonalityTableProps {
  personalities: Personality[];
  onEdit: (personality: Personality) => void;
  onDelete: (id: string) => void;
  isLoading?: boolean;
}

export default function PersonalityTable({
  personalities,
  onEdit,
  onDelete,
  isLoading = false,
}: PersonalityTableProps) {
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent"></div>
          <p className="mt-2 text-gray-400">Loading personalities...</p>
        </div>
      </div>
    );
  }

  if (personalities.length === 0) {
    return (
      <div className="rounded-lg border border-white/10 bg-zinc-900 p-8 text-center">
        <p className="text-gray-400">
          No personalities found. Create your first personality to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-white/10 bg-zinc-900 shadow-xl">
      <table className="min-w-full divide-y divide-white/10">
        <thead className="bg-zinc-950">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
              Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
              Description
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
              Amount (₹)
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
              Core Traits
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
              Created
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-400">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/10 bg-zinc-900">
          {personalities.map((personality) => (
            <tr key={personality._id} className="hover:bg-zinc-800 transition-colors">
              <td className="px-6 py-4">
                <div className="text-sm font-medium text-white">
                  {personality.name}
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="max-w-xs text-sm text-gray-400">
                  {personality.description}
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="text-sm text-gray-300">
                  {personality.amount ? (
                    <span className="inline-flex items-center rounded-md bg-green-950/50 px-2 py-1 text-xs font-medium text-green-300 border border-green-500/30">
                      ₹{personality.amount.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                  ) : (
                    <span className="text-gray-500 text-xs">Not set</span>
                  )}
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="flex flex-wrap gap-1">
                  {Object.entries(personality.core_traits)
                    .slice(0, 2)
                    .map(([key, value]) => (
                      <span
                        key={key}
                        className="inline-flex items-center rounded-full bg-indigo-950/50 px-2.5 py-0.5 text-xs font-medium text-indigo-300 border border-indigo-500/30"
                        title={`${key}: ${value}`}
                      >
                        {key}
                      </span>
                    ))}
                  {Object.keys(personality.core_traits).length > 2 && (
                    <button
                      onClick={() => toggleExpand(personality._id)}
                      className="inline-flex items-center rounded-full bg-accent px-2.5 py-0.5 text-xs font-medium text-muted-foreground hover:bg-muted hover:text-foreground border border-border transition-colors"
                    >
                      <Eye className="mr-1 h-3 w-3" />
                      +{Object.keys(personality.core_traits).length - 2} more
                    </button>
                  )}
                </div>
                {expandedId === personality._id && (
                  <div className="mt-2 space-y-1 rounded-lg bg-zinc-950 p-3 border border-white/10">
                    {Object.entries(personality.core_traits).map(
                      ([key, value]) => (
                        <div key={key} className="text-xs">
                          <span className="font-medium text-gray-300">
                            {key}:
                          </span>{" "}
                          <span className="text-gray-400">{value}</span>
                        </div>
                      )
                    )}
                  </div>
                )}
              </td>
              <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-400">
                {format(new Date(personality.created_at), "MMM d, yyyy")}
              </td>
              <td className="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => onEdit(personality)}
                    className="text-primary hover:text-primary/80 transition-colors"
                    title="Edit personality"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(personality._id)}
                    className={`transition-colors ${
                      deleteConfirmId === personality._id
                        ? "text-destructive hover:text-destructive/80"
                        : "text-muted-foreground hover:text-destructive"
                    }`}
                    title={
                      deleteConfirmId === personality._id
                        ? "Click again to confirm"
                        : "Delete personality"
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
