"use client";

import { useState, useEffect } from "react";
import { getCalls } from "@/lib/api";
import { CallRecord } from "@/types/call";
import { format } from "date-fns";
import { Phone, Clock, CheckCircle2, XCircle, Loader2, RefreshCw } from "lucide-react";

interface CallsListProps {
  onCallClick: (callId: string) => void;
  refreshTrigger?: number;
}

export default function CallsList({ onCallClick, refreshTrigger = 0 }: CallsListProps) {
  const [calls, setCalls] = useState<CallRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Fetch calls
  const fetchCalls = async (isManualRefresh = false) => {
    try {
      if (isManualRefresh) {
        setIsRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const response = await getCalls();
      setCalls(response.calls);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load calls");
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  // Load calls on mount and when refreshTrigger changes
  useEffect(() => {
    fetchCalls();
  }, [refreshTrigger]);

  // Handle manual refresh
  const handleRefresh = () => {
    fetchCalls(true);
  };

  // Format currency
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      minimumFractionDigits: 2,
    }).format(amount);
  };

  // Format date
  const formatDate = (dateString: string): string => {
    try {
      return format(new Date(dateString), "MMM d, yyyy, h:mm a");
    } catch {
      return dateString;
    }
  };

  // Get status badge
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "in_progress":
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-400">
            <Clock className="w-3 h-3" />
            In Progress
          </span>
        );
      case "completed":
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
            <CheckCircle2 className="w-3 h-3" />
            Completed
          </span>
        );
      case "failed":
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-red-500/20 text-red-400">
            <XCircle className="w-3 h-3" />
            Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-secondary text-secondary-foreground">
            {status}
          </span>
        );
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <span className="ml-3 text-muted-foreground">Loading calls...</span>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="text-center py-8">
        <XCircle className="w-12 h-12 text-destructive mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-foreground mb-2">Failed to Load Calls</h3>
        <p className="text-sm text-destructive mb-4">{error}</p>
        <button
          onClick={() => fetchCalls()}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Calls count */}
      <div className="mb-2">
        <p className="text-sm text-muted-foreground">
          {calls.length} {calls.length === 1 ? "call" : "calls"} total
        </p>
      </div>

      {/* Empty state */}
      {calls.length === 0 ? (
        <div className="text-center py-12">
          <Phone className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-foreground mb-2">No calls yet</h3>
          <p className="text-sm text-muted-foreground">
            Make your first call using the form on the left
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {/* Call Cards */}
          {calls.map((call) => (
            <div
              key={call.call_id}
              onClick={() => call.status === "completed" && onCallClick(call.call_id)}
              className={`bg-card border-2 border-border rounded-lg p-4 transition-all shadow-md ${
                call.status === "completed"
                  ? "cursor-pointer hover:shadow-xl hover:border-primary/50 hover:scale-[1.01]"
                  : "cursor-default opacity-75"
              }`}
            >
              {/* Card Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-card-foreground">{call.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <Phone className="w-3.5 h-3.5 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">
                      {call.phone_number}
                    </p>
                  </div>
                </div>
                {getStatusBadge(call.status)}
              </div>

              {/* Card Body */}
              <div className="flex items-center justify-between pt-3 border-t border-border">
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Amount</p>
                  <p className="text-lg font-bold text-foreground">
                    {formatCurrency(call.amount)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Date</p>
                  <p className="text-sm text-card-foreground">{formatDate(call.created_at)}</p>
                </div>
              </div>

              {/* Click hint for completed calls */}
              {call.status === "completed" && (
                <div className="mt-3 pt-3 border-t border-border">
                  <p className="text-xs text-primary text-center">
                    Click to view transcript →
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
