"use client";

import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import { getCountries, healthCheck } from "@/lib/api";
import { Country, CallResponse } from "@/types/call";
import CallForm from "@/components/CallForm";
import CallsList from "@/components/CallsList";
import TranscriptSidebar from "@/components/TranscriptSidebar";

export default function Home() {
  const [apiStatus, setApiStatus] = useState<string>("Checking...");
  const [countries, setCountries] = useState<Country[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [selectedCallId, setSelectedCallId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const testAPI = async () => {
      try {
        // Test health check
        const health = await healthCheck();
        setApiStatus(health.status);

        // Test countries endpoint
        const countriesData = await getCountries();
        setCountries(countriesData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
        setApiStatus("Failed");
      }
    };

    testAPI();
  }, []);

  const handleCallSuccess = (response: CallResponse) => {
    console.log("Call initiated successfully:", response);
    // Refresh the calls list
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleCallClick = (callId: string) => {
    console.log("Call clicked:", callId);
    setSelectedCallId(callId);
    setSidebarOpen(true);
  };

  const handleSidebarClose = () => {
    setSidebarOpen(false);
    setSelectedCallId(null);
  };

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-start justify-between">
          <h1 className="text-3xl font-bold text-foreground pl-[30px] pt-[20px]">
            Outbound Caller Dashboard
          </h1>
          
          {/* API Status Indicator - Top Right */}
          <div className="flex items-center gap-2 pt-[20px]">
            <span className="text-sm text-muted-foreground">Backend Status:</span>
            <span
              className={`px-3 py-1.5 rounded-full text-xs font-medium flex items-center gap-2 ${
                apiStatus === "ok"
                  ? "bg-green-500/20 text-green-400"
                  : apiStatus === "Failed"
                  ? "bg-red-500/20 text-red-400"
                  : "bg-yellow-500/20 text-yellow-400"
              }`}
            >
              {apiStatus === "ok" && (
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              )}
              {apiStatus}
            </span>
            {error && (
              <span className="text-xs text-destructive">({error})</span>
            )}
          </div>
        </div>
      </header>

      {/* Main Content - Two Column Layout */}
      <main className="flex-1 min-h-0 max-w-7xl w-full mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
          {/* Left Panel - Call Form (Fixed Height, No Scroll) */}
          <div className="lg:col-span-1 space-y-4 overflow-y-auto min-h-0">
            <CallForm onSuccess={handleCallSuccess} />
            
            {/* API Debug - Collapsed */}
            <details className="bg-card rounded-lg shadow-md border border-border">
              <summary className="px-4 py-3 text-sm font-semibold text-card-foreground cursor-pointer hover:bg-accent">
                API Test: Countries ({countries.length})
              </summary>
              <div className="px-4 pb-4 pt-2 max-h-60 overflow-y-auto">
                {countries.length > 0 ? (
                  <div className="space-y-2">
                    {countries.map((country) => (
                      <div
                        key={country.iso}
                        className="flex items-center gap-2 text-sm"
                      >
                        <span className="text-lg">{country.flag}</span>
                        <span className="font-medium text-foreground">{country.code}</span>
                        <span className="text-muted-foreground">{country.name}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-sm">Loading...</p>
                )}
              </div>
            </details>
          </div>

          {/* Right Panel - Calls List (Scrollable Container) */}
          <div className="lg:col-span-2 flex flex-col min-h-0">
            <div className="bg-card rounded-lg shadow-md flex flex-col h-full overflow-hidden border border-border">
              <div className="flex-shrink-0 p-4 border-b border-border flex justify-between items-center">
                <h2 className="text-xl font-semibold text-foreground">Call History</h2>
                <button
                  onClick={() => setRefreshTrigger((prev) => prev + 1)}
                  className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium"
                  aria-label="Refresh calls list"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refresh
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-4 min-h-0">
                <CallsList onCallClick={handleCallClick} refreshTrigger={refreshTrigger} />
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Transcript Sidebar - Overlay */}
      <TranscriptSidebar
        callId={selectedCallId}
        isOpen={sidebarOpen}
        onClose={handleSidebarClose}
      />
    </div>
  );
}
