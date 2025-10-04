"use client";

import { useEffect, useState } from "react";
import { X, Loader2, AlertCircle, Award, TrendingUp, AlertTriangle, Smile, HandshakeIcon } from "lucide-react";
import { TranscriptResponse } from "@/types/call";
import { getCallTranscript } from "@/lib/api";
import { format } from "date-fns";

interface TranscriptSidebarProps {
  callId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function TranscriptSidebar({
  callId,
  isOpen,
  onClose,
}: TranscriptSidebarProps) {
  const [transcript, setTranscript] = useState<TranscriptResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch transcript when callId changes
  useEffect(() => {
    const fetchTranscript = async () => {
      if (!callId || !isOpen) {
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const data = await getCallTranscript(callId);
        setTranscript(data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to load transcript";
        setError(errorMessage);
        console.error("Error fetching transcript:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTranscript();
  }, [callId, isOpen]);

  // Reset state when sidebar closes
  useEffect(() => {
    if (!isOpen) {
      setTranscript(null);
      setError(null);
    }
  }, [isOpen]);

  if (!isOpen) {
    return null;
  }

  return (
    <>
      {/* Backdrop overlay with blur effect */}
      <div
        className={`fixed inset-0 z-40 transition-all duration-300 ${
          isOpen ? "opacity-100 visible" : "opacity-0 invisible"
        }`}
        onClick={onClose}
        style={{
          backdropFilter: isOpen ? "blur(8px)" : "none",
          WebkitBackdropFilter: isOpen ? "blur(8px)" : "none",
          backgroundColor: "rgba(0, 0, 0, 0.6)",
        }}
      />

      {/* Modal - Centered */}
      <div
        className={`fixed inset-0 z-50 flex items-center justify-center p-4 transition-all duration-300 pointer-events-none ${
          isOpen ? "opacity-100" : "opacity-0"
        }`}
      >
        <div
          className={`bg-card border border-border rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col transform transition-transform duration-300 pointer-events-auto ${
            isOpen ? "scale-100" : "scale-95"
          }`}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-primary/90 to-primary text-primary-foreground p-6 rounded-t-2xl flex justify-between items-start">
            <div className="flex-1">
              <h2 className="text-2xl font-bold mb-2">Call Transcript</h2>
              {transcript && (
                <div className="text-sm opacity-90 space-y-1">
                  <p className="font-semibold">{transcript.name}</p>
                  <p>{transcript.phone_number}</p>
                  <p className="font-mono">Amount: ${transcript.amount.toFixed(2)}</p>
                  <p className="text-xs mt-2">
                    {format(new Date(transcript.created_at), "MMM d, yyyy, h:mm a")}
                  </p>
                </div>
              )}
            </div>
            <button
              onClick={onClose}
              className="ml-4 p-2 hover:bg-primary-foreground/20 rounded-lg transition-colors"
              aria-label="Close modal"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6 bg-background">
            {loading && (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                <Loader2 className="w-12 h-12 animate-spin mb-4" />
                <p className="text-lg">Loading transcript...</p>
              </div>
            )}

            {error && (
              <div className="flex flex-col items-center justify-center h-full">
                <div className="bg-destructive/20 border border-destructive/30 rounded-lg p-6 max-w-md">
                  <div className="flex items-start">
                    <AlertCircle className="w-6 h-6 text-destructive mr-3 flex-shrink-0 mt-0.5" />
                    <div>
                      <h3 className="text-lg font-semibold text-destructive mb-2">
                        Error Loading Transcript
                      </h3>
                      <p className="text-destructive/90 text-sm">{error}</p>
                      {error.includes("in progress") && (
                        <p className="text-destructive/80 text-xs mt-2">
                          Please wait for the call to complete and try again.
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {!loading && !error && transcript && (
              <div className="space-y-4">
                {/* Transcript Messages */}
                {transcript.transcript.length === 0 ? (
                  <div className="text-center text-muted-foreground py-8">
                    <p>No transcript messages available</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {transcript.transcript.map((message, index) => (
                      <div
                        key={index}
                        className={`flex ${
                          message.role === "user" ? "justify-end" : "justify-start"
                        }`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg p-4 shadow-sm ${
                            message.role === "user"
                              ? "bg-primary text-primary-foreground"
                              : "bg-card text-card-foreground border border-border"
                          }`}
                        >
                          {/* Role Label */}
                          <div
                            className={`text-xs font-semibold mb-1 ${
                              message.role === "user" ? "opacity-80" : "text-muted-foreground"
                            }`}
                          >
                            {message.role === "user" ? "Customer" : "Agent"}
                          </div>

                          {/* Message Content */}
                          <p className="text-sm leading-relaxed whitespace-pre-wrap">
                            {message.message}
                          </p>

                          {/* Timestamp - only show if available */}
                          {message.timestamp && (
                            <div
                              className={`text-xs mt-2 ${
                                message.role === "user" ? "opacity-70" : "text-muted-foreground"
                              }`}
                            >
                              {format(new Date(message.timestamp), "h:mm:ss a")}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Footer - Risk Matrices Dashboard */}
          {!loading && !error && transcript && (
            <div className="border-t border-border bg-card p-4 rounded-b-2xl">
              <h3 className="text-sm font-bold text-card-foreground mb-3 flex items-center">
                <Award className="w-4 h-4 mr-2 text-primary" />
                Risk Assessment
              </h3>
              
              <div className="grid grid-cols-5 gap-3">
                {/* Loan Recovery Score */}
                <CompactScoreCard
                  title="Loan Recovery"
                  score={transcript.loan_recovery_score}
                  icon={<Award className="w-3.5 h-3.5" />}
                  color="green"
                />

                {/* Willingness to Pay Score */}
                <CompactScoreCard
                  title="Willingness"
                  score={transcript.willingness_to_pay_score}
                  icon={<TrendingUp className="w-3.5 h-3.5" />}
                  color="blue"
                />

                {/* Escalation Risk Score */}
                <CompactScoreCard
                  title="Escalation Risk"
                  score={transcript.escalation_risk_score}
                  icon={<AlertTriangle className="w-3.5 h-3.5" />}
                  color="orange"
                />

                {/* Customer Sentiment Score */}
                <CompactScoreCard
                  title="Sentiment"
                  score={transcript.customer_sentiment_score}
                  icon={<Smile className="w-3.5 h-3.5" />}
                  color="purple"
                />

                {/* Promise to Pay Reliability Index */}
                <CompactScoreCard
                  title="Reliability"
                  score={transcript.promise_to_pay_reliability_index}
                  icon={<HandshakeIcon className="w-3.5 h-3.5" />}
                  color="indigo"
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

// Helper component for compact score cards
interface CompactScoreCardProps {
  title: string;
  score?: number;
  icon: React.ReactNode;
  color: "green" | "blue" | "orange" | "purple" | "indigo";
}

function CompactScoreCard({ title, score, icon, color }: CompactScoreCardProps) {
  // Color configurations
  const colorConfig = {
    green: {
      bg: "bg-green-500/20",
      border: "border-green-500/30",
      text: "text-green-400",
    },
    blue: {
      bg: "bg-blue-500/20",
      border: "border-blue-500/30",
      text: "text-blue-400",
    },
    orange: {
      bg: "bg-orange-500/20",
      border: "border-orange-500/30",
      text: "text-orange-400",
    },
    purple: {
      bg: "bg-purple-500/20",
      border: "border-purple-500/30",
      text: "text-purple-400",
    },
    indigo: {
      bg: "bg-indigo-500/20",
      border: "border-indigo-500/30",
      text: "text-indigo-400",
    },
  };

  const colors = colorConfig[color];

  if (score === undefined || score === null) {
    return (
      <div className={`${colors.bg} border ${colors.border} rounded-lg p-3 opacity-60`}>
        <div className="flex items-center gap-1.5 mb-2">
          <div className={colors.text}>{icon}</div>
          <p className="text-xs font-medium text-card-foreground truncate">{title}</p>
        </div>
        <p className="text-xs text-muted-foreground italic text-center">Analyzing...</p>
      </div>
    );
  }

  return (
    <div className={`${colors.bg} border ${colors.border} rounded-lg p-3 transition-all hover:scale-105`}>
      <div className="flex items-center gap-1.5 mb-2">
        <div className={colors.text}>{icon}</div>
        <p className="text-xs font-medium text-card-foreground truncate">{title}</p>
      </div>
      <div className="text-center">
        <p className={`text-lg font-bold ${colors.text}`}>
          {score.toFixed(0)}/100
        </p>
      </div>
    </div>
  );
}
