/**
 * EvaluationResultsTable Component
 * Displays all evaluations with status, scores, and actions
 * Automatically polls for running evaluations
 * Part of Phase 3, Module 3: The Manual Evaluation Engine
 */
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { EvaluationWithDetails, EvaluationStatus } from "@/types/evaluation";
import { Eye, Trash2, Loader2, CheckCircle2, XCircle, Clock } from "lucide-react";
import { format } from "date-fns";
import { deleteEvaluation } from "@/lib/api";

interface EvaluationResultsTableProps {
  evaluations: EvaluationWithDetails[];
  onDelete: (id: string) => void;
  onRefresh: () => void;
  isLoading?: boolean;
}

export default function EvaluationResultsTable({
  evaluations,
  onDelete,
  onRefresh,
  isLoading = false,
}: EvaluationResultsTableProps) {
  const router = useRouter();
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Auto-refresh if there are any running evaluations
  useEffect(() => {
    const hasRunningEvals = evaluations.some(
      (e) => e.status === "PENDING" || e.status === "RUNNING"
    );

    if (hasRunningEvals) {
      const interval = setInterval(() => {
        onRefresh();
      }, 3000); // Poll every 3 seconds

      return () => clearInterval(interval);
    }
  }, [evaluations, onRefresh]);

  const handleDelete = async (id: string) => {
    if (deleteConfirmId === id) {
      // Confirmed, proceed with deletion
      try {
        setDeletingId(id);
        await deleteEvaluation(id);
        onDelete(id);
        setDeleteConfirmId(null);
      } catch (err) {
        console.error("Delete failed:", err);
      } finally {
        setDeletingId(null);
      }
    } else {
      // Show confirmation
      setDeleteConfirmId(id);
      // Auto-cancel after 3 seconds
      setTimeout(() => setDeleteConfirmId(null), 3000);
    }
  };

  const handleView = (id: string) => {
    router.push(`/evaluations/${id}`);
  };

  const getStatusBadge = (status: EvaluationStatus) => {
    switch (status) {
      case "PENDING":
        return (
          <span className="inline-flex items-center gap-1 rounded-full bg-yellow-900/30 px-2.5 py-0.5 text-xs font-medium text-yellow-400">
            <Clock className="h-3 w-3" />
            Pending
          </span>
        );
      case "RUNNING":
        return (
          <span className="inline-flex items-center gap-1 rounded-full bg-blue-900/30 px-2.5 py-0.5 text-xs font-medium text-blue-400">
            <Loader2 className="h-3 w-3 animate-spin" />
            Running
          </span>
        );
      case "COMPLETED":
        return (
          <span className="inline-flex items-center gap-1 rounded-full bg-green-900/30 px-2.5 py-0.5 text-xs font-medium text-green-400">
            <CheckCircle2 className="h-3 w-3" />
            Completed
          </span>
        );
      case "FAILED":
        return (
          <span className="inline-flex items-center gap-1 rounded-full bg-red-900/30 px-2.5 py-0.5 text-xs font-medium text-red-400">
            <XCircle className="h-3 w-3" />
            Failed
          </span>
        );
    }
  };

  const getScoreDisplay = (evaluation: EvaluationWithDetails) => {
    if (evaluation.status === "COMPLETED" && evaluation.scores) {
      const avg = Math.round(
        (evaluation.scores.task_completion + evaluation.scores.conversation_efficiency) / 2
      );
      const colorClass =
        avg >= 80
          ? "text-green-400"
          : avg >= 60
          ? "text-yellow-400"
          : "text-red-400";
      
      return (
        <div className="text-sm">
          <div className={`font-semibold ${colorClass}`}>{avg}%</div>
          <div className="text-xs text-gray-500">
            TC: {evaluation.scores.task_completion}% | CE: {evaluation.scores.conversation_efficiency}%
          </div>
        </div>
      );
    }
    return <span className="text-gray-500">-</span>;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Loader2 className="inline-block h-8 w-8 animate-spin text-white" />
          <p className="mt-2 text-gray-400">Loading evaluations...</p>
        </div>
      </div>
    );
  }

  if (evaluations.length === 0) {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-8 text-center">
        <p className="text-gray-400">
          No evaluations found. Start a new evaluation to see results here.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-zinc-800 bg-zinc-900 shadow-xl">
      <table className="min-w-full divide-y divide-zinc-800">
        <thead className="bg-zinc-950 sticky top-0 z-10">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
              Prompt
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
              Scenario
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
              Score
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
              Created
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-400">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800">
          {evaluations.map((evaluation) => (
            <tr
              key={evaluation._id}
              className="transition-colors hover:bg-zinc-800/50"
            >
              <td className="px-6 py-4">
                <div className="text-sm font-medium text-white">
                  {evaluation.prompt_name || "Unknown Prompt"}
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="max-w-xs truncate text-sm text-gray-300">
                  {evaluation.scenario_title || "Unknown Scenario"}
                </div>
              </td>
              <td className="px-6 py-4">{getStatusBadge(evaluation.status)}</td>
              <td className="px-6 py-4">{getScoreDisplay(evaluation)}</td>
              <td className="px-6 py-4 text-sm text-gray-400">
                {format(new Date(evaluation.created_at), "MMM d, yyyy HH:mm")}
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                  {/* View Button - Only for completed evaluations */}
                  {evaluation.status === "COMPLETED" && (
                    <button
                      onClick={() => handleView(evaluation._id)}
                      className="rounded p-1.5 text-gray-400 transition-colors hover:bg-zinc-700 hover:text-white"
                      title="View details"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                  )}

                  {/* Delete Button */}
                  <button
                    onClick={() => handleDelete(evaluation._id)}
                    disabled={deletingId === evaluation._id}
                    className={`rounded p-1.5 transition-colors ${
                      deleteConfirmId === evaluation._id
                        ? "bg-red-600 text-white"
                        : "text-gray-400 hover:bg-zinc-700 hover:text-red-400"
                    } disabled:opacity-50`}
                    title={
                      deleteConfirmId === evaluation._id
                        ? "Click again to confirm"
                        : "Delete evaluation"
                    }
                  >
                    {deletingId === evaluation._id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
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
