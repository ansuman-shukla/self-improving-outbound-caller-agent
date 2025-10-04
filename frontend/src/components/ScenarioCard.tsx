/**
 * ScenarioCard Component
 * Displays individual scenario as a card with expandable details
 */
"use client";

import { useState } from "react";
import { ScenarioWithPersonality } from "@/types/scenario";
import { Pencil, Trash2, ChevronDown, ChevronUp, Star, User } from "lucide-react";
import { format } from "date-fns";

interface ScenarioCardProps {
  scenario: ScenarioWithPersonality;
  onEdit: (scenario: ScenarioWithPersonality) => void;
  onDelete: (id: string) => void;
}

export default function ScenarioCard({
  scenario,
  onEdit,
  onDelete,
}: ScenarioCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(false);

  const handleDelete = () => {
    if (deleteConfirm) {
      onDelete(scenario._id);
      setDeleteConfirm(false);
    } else {
      setDeleteConfirm(true);
      setTimeout(() => setDeleteConfirm(false), 3000);
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

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden hover:border-zinc-700 transition-colors">
      {/* Card Header */}
      <div className="p-6">
        {/* Title and Actions */}
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-semibold text-white flex-1 pr-4">
            {scenario.title}
          </h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onEdit(scenario)}
              className="text-zinc-400 hover:text-white transition-colors"
              title="Edit scenario"
            >
              <Pencil className="h-4 w-4" />
            </button>
            <button
              onClick={handleDelete}
              className={`${
                deleteConfirm
                  ? "text-zinc-300 animate-pulse"
                  : "text-zinc-400 hover:text-white"
              } transition-colors`}
              title={deleteConfirm ? "Click again to confirm" : "Delete scenario"}
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Metadata */}
        <div className="flex flex-wrap items-center gap-4 text-sm text-zinc-400 mb-4">
          <div className="flex items-center gap-1.5">
            <User className="h-3.5 w-3.5" />
            <span>{scenario.personality_name || "Unknown"}</span>
          </div>
          <div className="flex items-center gap-1.5">
            {renderWeightStars(scenario.weight)}
          </div>
          <div>
            {format(new Date(scenario.created_at), "MMM d, yyyy")}
          </div>
        </div>

        {/* Brief */}
        <div className="mb-4">
          <p className="text-sm text-zinc-500 italic">
            "{scenario.brief}"
          </p>
        </div>

        {/* Expand/Collapse Button */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors"
        >
          {isExpanded ? (
            <>
              <ChevronUp className="h-4 w-4" />
              Hide Details
            </>
          ) : (
            <>
              <ChevronDown className="h-4 w-4" />
              View Details
            </>
          )}
        </button>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="border-t border-zinc-800 bg-zinc-950 p-6 space-y-4">
          <div>
            <div className="text-xs font-medium text-zinc-500 mb-2 uppercase tracking-wider">
              Backstory
            </div>
            <div className="text-sm text-zinc-300 leading-relaxed">
              {scenario.backstory}
            </div>
          </div>
          <div>
            <div className="text-xs font-medium text-zinc-500 mb-2 uppercase tracking-wider">
              Objective
            </div>
            <div className="text-sm text-zinc-300 leading-relaxed">
              {scenario.objective}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
