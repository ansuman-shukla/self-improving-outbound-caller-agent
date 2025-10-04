/**
 * PromptTable Component
 * Displays all agent prompts in a table format with edit and delete actions
 */
"use client";

import { useState } from "react";
import { Prompt } from "@/types/library";
import { Pencil, Trash2, Eye, EyeOff } from "lucide-react";
import { format } from "date-fns";

interface PromptTableProps {
  prompts: Prompt[];
  onEdit: (prompt: Prompt) => void;
  onDelete: (id: string) => void;
  isLoading?: boolean;
}

export default function PromptTable({
  prompts,
  onEdit,
  onDelete,
  isLoading = false,
}: PromptTableProps) {
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

  const truncateText = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent"></div>
          <p className="mt-2 text-gray-400">Loading prompts...</p>
        </div>
      </div>
    );
  }

  if (prompts.length === 0) {
    return (
      <div className="rounded-lg border border-white/10 bg-zinc-900 p-8 text-center">
        <p className="text-gray-400">
          No prompts found. Create your first agent prompt to get started.
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
              Version
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
              Prompt Text
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
          {prompts.map((prompt) => (
            <tr key={prompt._id} className="hover:bg-zinc-800 transition-colors">
              <td className="px-6 py-4">
                <div className="text-sm font-medium text-white">
                  {prompt.name}
                </div>
              </td>
              <td className="whitespace-nowrap px-6 py-4">
                <span className="inline-flex rounded-full bg-emerald-950/50 px-3 py-1 text-xs font-semibold text-emerald-300 border border-emerald-500/30">
                  v{prompt.version}
                </span>
              </td>
              <td className="px-6 py-4">
                <div className="max-w-md">
                  <div className="text-sm text-gray-400">
                    {expandedId === prompt._id ? (
                      <div className="whitespace-pre-wrap rounded-lg bg-zinc-950 p-3 font-mono text-xs border border-white/10">
                        {prompt.prompt_text}
                      </div>
                    ) : (
                      <div className="font-mono text-xs">
                        {truncateText(prompt.prompt_text, 150)}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => toggleExpand(prompt._id)}
                    className="mt-2 flex items-center gap-1 text-xs text-primary hover:text-primary/80 transition-colors"
                  >
                    {expandedId === prompt._id ? (
                      <>
                        <EyeOff className="h-3 w-3" />
                        Show Less
                      </>
                    ) : (
                      <>
                        <Eye className="h-3 w-3" />
                        Show Full Prompt
                      </>
                    )}
                  </button>
                </div>
              </td>
              <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-400">
                {format(new Date(prompt.created_at), "MMM d, yyyy")}
              </td>
              <td className="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => onEdit(prompt)}
                    className="text-primary hover:text-primary/80 transition-colors"
                    title="Edit prompt"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(prompt._id)}
                    className={`transition-colors ${
                      deleteConfirmId === prompt._id
                        ? "text-destructive hover:text-destructive/80"
                        : "text-muted-foreground hover:text-destructive"
                    }`}
                    title={
                      deleteConfirmId === prompt._id
                        ? "Click again to confirm"
                        : "Delete prompt"
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
