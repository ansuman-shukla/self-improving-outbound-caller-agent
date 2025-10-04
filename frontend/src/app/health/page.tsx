"use client";

import { useEffect, useState } from "react";
import axios from "axios";

interface HealthStatus {
  status: string;
  loading: boolean;
  error: string | null;
}

export default function HealthCheckPage() {
  const [health, setHealth] = useState<HealthStatus>({
    status: "",
    loading: true,
    error: null,
  });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await axios.get("/api/health");
        setHealth({
          status: response.data.status,
          loading: false,
          error: null,
        });
      } catch (error) {
        setHealth({
          status: "",
          loading: false,
          error: error instanceof Error ? error.message : "Failed to connect to API",
        });
      }
    };

    checkHealth();
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-lg">
        <h1 className="mb-6 text-center text-3xl font-bold text-gray-900">
          API Health Check
        </h1>

        <div className="space-y-4">
          <div className="rounded-lg border border-gray-200 p-4">
            <h2 className="mb-2 text-sm font-semibold text-gray-700">
              Backend API Status
            </h2>
            {health.loading ? (
              <div className="flex items-center gap-2">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600"></div>
                <p className="text-sm text-gray-500">Checking connection...</p>
              </div>
            ) : health.error ? (
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-red-500"></div>
                <p className="text-sm text-red-600">{health.error}</p>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-green-500"></div>
                <p className="text-sm text-green-600">
                  Status: <span className="font-semibold">{health.status}</span>
                </p>
              </div>
            )}
          </div>

          <div className="rounded-lg bg-blue-50 p-4">
            <h3 className="mb-2 text-sm font-semibold text-blue-900">
              Test Endpoint
            </h3>
            <p className="text-sm text-blue-700">
              GET /api/health
            </p>
            <p className="mt-2 text-xs text-blue-600">
              This endpoint confirms the FastAPI backend is running and accessible from the Next.js frontend.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
