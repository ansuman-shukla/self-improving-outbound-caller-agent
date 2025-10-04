/**
 * TuningRunsTable Component
 * Displays all tuning loops with live status updates via polling
 * Part of Phase 4, Module 4: The Automated Tuning Loop
 */
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, CheckCircle, XCircle, Clock, ChevronRight } from "lucide-react";
import { TuningLoopWithDetails } from "@/types/tuning";
import { getTuningLoop } from "@/lib/api";
import { usePolling } from "@/hooks/usePolling";

interface TuningRunsTableProps {
  tuningLoops: TuningLoopWithDetails[];
  onUpdate: () => void;
}

/**
 * Individual row component with polling for active tuning loops
 */
function TuningRunRow({
  tuningLoop,
  onUpdate,
}: {
  tuningLoop: TuningLoopWithDetails;
  onUpdate: () => void;
}) {
  const router = useRouter();
  const isActive =
    tuningLoop.status === "PENDING" || tuningLoop.status === "RUNNING";

  // Poll for updates if the tuning loop is active
  const { data: updatedLoop } = usePolling({
    fetchFn: () => getTuningLoop(tuningLoop._id),
    shouldStopPolling: (loop) =>
      loop.status === "COMPLETED" || loop.status === "FAILED",
    interval: 3000,
    enabled: isActive,
    onComplete: () => {
      // Refresh the parent table when this loop completes
      onUpdate();
    },
  });

  // Use updated data if available, otherwise use initial data
  // When polling returns data, merge it with initial data to preserve enriched fields
  const displayLoop: TuningLoopWithDetails = updatedLoop
    ? { ...tuningLoop, ...updatedLoop }
    : tuningLoop;

  const getStatusIcon = () => {
    switch (displayLoop.status) {
      case "PENDING":
        return <Clock className="h-5 w-5 text-yellow-400" />;
      case "RUNNING":
        return <Loader2 className="h-5 w-5 animate-spin text-blue-400" />;
      case "COMPLETED":
        return <CheckCircle className="h-5 w-5 text-green-400" />;
      case "FAILED":
        return <XCircle className="h-5 w-5 text-red-400" />;
    }
  };

  const getStatusText = () => {
    switch (displayLoop.status) {
      case "PENDING":
        return "Pending";
      case "RUNNING":
        return `Running (Iteration ${displayLoop.iterations.length})`;
      case "COMPLETED":
        return "Completed";
      case "FAILED":
        return "Failed";
    }
  };

  const getStatusColor = () => {
    switch (displayLoop.status) {
      case "PENDING":
        return "text-yellow-400";
      case "RUNNING":
        return "text-blue-400";
      case "COMPLETED":
        return "text-green-400";
      case "FAILED":
        return "text-red-400";
    }
  };

  const getCurrentScore = () => {
    if (displayLoop.iterations.length === 0) return "—";
    const latestIteration =
      displayLoop.iterations[displayLoop.iterations.length - 1];
    return latestIteration.weighted_score.toFixed(1);
  };

  const getScoreImprovement = () => {
    if (displayLoop.iterations.length < 2) return null;
    const firstScore = displayLoop.iterations[0].weighted_score;
    const latestScore =
      displayLoop.iterations[displayLoop.iterations.length - 1].weighted_score;
    const improvement = latestScore - firstScore;
    return improvement >= 0 ? `+${improvement.toFixed(1)}` : improvement.toFixed(1);
  };

  const handleClick = () => {
    router.push(`/tuning/${displayLoop._id}`);
  };

  return (
    <tr
      onClick={handleClick}
      className="cursor-pointer border-b border-zinc-800 transition-colors hover:bg-zinc-800/50"
    >
      {/* Status */}
      <td className="px-6 py-4">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <span className={`font-medium ${getStatusColor()}`}>
            {getStatusText()}
          </span>
        </div>
      </td>

      {/* Initial Prompt */}
      <td className="px-6 py-4">
        <span className="text-white">{displayLoop.initial_prompt_name || "Unknown"}</span>
      </td>

      {/* Target Score */}
      <td className="px-6 py-4 text-center">
        <span className="text-gray-300">{displayLoop.config.target_score}</span>
      </td>

      {/* Current Score */}
      <td className="px-6 py-4 text-center">
        <div className="flex items-center justify-center gap-2">
          <span className="text-white font-medium">{getCurrentScore()}</span>
          {getScoreImprovement() && (
            <span
              className={`text-xs ${
                parseFloat(getScoreImprovement()!) >= 0
                  ? "text-green-400"
                  : "text-red-400"
              }`}
            >
              ({getScoreImprovement()})
            </span>
          )}
        </div>
      </td>

      {/* Iterations */}
      <td className="px-6 py-4 text-center">
        <span className="text-gray-300">
          {displayLoop.iterations.length} / {displayLoop.config.max_iterations}
        </span>
      </td>

      {/* Scenarios */}
      <td className="px-6 py-4 text-center">
        <span className="text-gray-300">
          {displayLoop.config.scenario_weights.length}
        </span>
      </td>

      {/* Created At */}
      <td className="px-6 py-4">
        <span className="text-gray-400 text-sm">
          {new Date(displayLoop.created_at).toLocaleString()}
        </span>
      </td>

      {/* Action */}
      <td className="px-6 py-4">
        <ChevronRight className="h-5 w-5 text-gray-400" />
      </td>
    </tr>
  );
}

export default function TuningRunsTable({
  tuningLoops,
  onUpdate,
}: TuningRunsTableProps) {
  if (tuningLoops.length === 0) {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-8 text-center">
        <p className="text-gray-400">
          No tuning loops yet. Click "Start New Tuning Loop" to begin.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-zinc-800 bg-zinc-900 shadow-xl">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="border-b border-zinc-800 bg-zinc-950">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-white">
                Status
              </th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-white">
                Initial Prompt
              </th>
              <th className="px-6 py-3 text-center text-sm font-semibold text-white">
                Target
              </th>
              <th className="px-6 py-3 text-center text-sm font-semibold text-white">
                Current Score
              </th>
              <th className="px-6 py-3 text-center text-sm font-semibold text-white">
                Progress
              </th>
              <th className="px-6 py-3 text-center text-sm font-semibold text-white">
                Scenarios
              </th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-white">
                Created
              </th>
              <th className="px-6 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {tuningLoops.map((loop) => (
              <TuningRunRow key={loop._id} tuningLoop={loop} onUpdate={onUpdate} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
