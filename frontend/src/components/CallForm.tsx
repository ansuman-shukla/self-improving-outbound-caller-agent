"use client";

import { useState, useEffect } from "react";
import { getCountries, makeCall } from "@/lib/api";
import { Country, CallRequest, CallResponse } from "@/types/call";
import { Phone, User, DollarSign, Loader2 } from "lucide-react";

interface CallFormProps {
  onSuccess?: (response: CallResponse) => void;
}

export default function CallForm({ onSuccess }: CallFormProps) {
  // Form state
  const [formData, setFormData] = useState({
    name: "",
    amount: "",
    countryCode: "+91", // Default to India
    phoneNumber: "",
  });

  // UI state
  const [countries, setCountries] = useState<Country[]>([]);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<CallResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Load countries on mount
  useEffect(() => {
    const loadCountries = async () => {
      try {
        const data = await getCountries();
        setCountries(data);
      } catch (err) {
        console.error("Failed to load countries:", err);
        setError("Failed to load country codes");
      }
    };

    loadCountries();
  }, []);

  // Handle input changes
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear errors when user starts typing
    if (error) setError(null);
    if (response) setResponse(null);
  };

  // Form validation
  const validateForm = (): string | null => {
    if (!formData.name.trim()) {
      return "Please enter customer name";
    }
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      return "Please enter a valid amount";
    }
    if (!formData.phoneNumber.trim()) {
      return "Please enter phone number";
    }
    if (!/^\d+$/.test(formData.phoneNumber)) {
      return "Phone number should contain only digits";
    }
    return null;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate form
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      // Prepare call request
      const callRequest: CallRequest = {
        name: formData.name.trim(),
        phone_number: formData.phoneNumber.trim(),
        country_code: formData.countryCode,
        amount: parseFloat(formData.amount),
      };

      // Make the call
      const result = await makeCall(callRequest);
      setResponse(result);

      // Clear form on success
      setFormData({
        name: "",
        amount: "",
        countryCode: formData.countryCode, // Keep selected country
        phoneNumber: "",
      });

      // Trigger success callback
      if (onSuccess) {
        onSuccess(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to initiate call");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-card rounded-lg shadow-md p-6 border border-border">
      <h2 className="text-2xl font-semibold mb-6 text-foreground">
        Initiate Outbound Call
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Customer Name */}
        <div>
          <label
            htmlFor="name"
            className="block text-sm font-medium text-card-foreground mb-1"
          >
            Customer Name
          </label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="w-full pl-10 pr-4 py-2 bg-input border border-border text-foreground rounded-md focus:ring-2 focus:ring-ring focus:border-transparent outline-none transition placeholder:text-muted-foreground"
              placeholder="Enter customer name"
              disabled={loading}
            />
          </div>
        </div>

        {/* Amount */}
        <div>
          <label
            htmlFor="amount"
            className="block text-sm font-medium text-card-foreground mb-1"
          >
            Bill Amount
          </label>
          <div className="relative">
            <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
            <input
              type="number"
              id="amount"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              step="0.01"
              min="0"
              className="w-full pl-10 pr-4 py-2 bg-input border border-border text-foreground rounded-md focus:ring-2 focus:ring-ring focus:border-transparent outline-none transition placeholder:text-muted-foreground"
              placeholder="Enter amount"
              disabled={loading}
            />
          </div>
        </div>

        {/* Phone Number with Country Code */}
        <div>
          <label
            htmlFor="phoneNumber"
            className="block text-sm font-medium text-card-foreground mb-1"
          >
            Phone Number
          </label>
          <div className="flex gap-2">
            {/* Country Code Dropdown */}
            <div className="relative flex-shrink-0">
              <select
                name="countryCode"
                value={formData.countryCode}
                onChange={handleChange}
                className="appearance-none pl-3 pr-8 py-2 bg-input border border-border text-foreground rounded-md focus:ring-2 focus:ring-ring focus:border-transparent outline-none transition cursor-pointer h-full"
                disabled={loading || countries.length === 0}
              >
                {countries.length === 0 ? (
                  <option value="">Loading...</option>
                ) : (
                  countries.map((country) => (
                    <option key={country.iso} value={country.code}>
                      {country.flag} {country.code}
                    </option>
                  ))
                )}
              </select>
              <div className="absolute inset-y-0 right-2 flex items-center pointer-events-none">
                <svg
                  className="w-4 h-4 text-muted-foreground"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </div>
            </div>

            {/* Phone Number Input */}
            <div className="relative flex-1">
              <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
              <input
                type="tel"
                id="phoneNumber"
                name="phoneNumber"
                value={formData.phoneNumber}
                onChange={handleChange}
                className="w-full pl-10 pr-4 py-2 bg-input border border-border text-foreground rounded-md focus:ring-2 focus:ring-ring focus:border-transparent outline-none transition placeholder:text-muted-foreground"
                placeholder="Enter phone number"
                disabled={loading}
              />
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Enter phone number without country code
          </p>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-medium py-2 px-4 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Initiating Call...
            </>
          ) : (
            <>
              <Phone className="w-5 h-5" />
              Make Call
            </>
          )}
        </button>
      </form>

      {/* Success Message */}
      {response && (
        <div className="mt-4 p-4 bg-green-500/20 border border-green-500/30 rounded-md">
          <h3 className="font-semibold text-green-400 mb-2">
            ✓ Call Initiated Successfully!
          </h3>
          <div className="text-sm text-green-300 space-y-1">
            <p>
              <span className="font-medium">Room Name:</span>{" "}
              {response.room_name}
            </p>
            <p>
              <span className="font-medium">Dispatch ID:</span>{" "}
              {response.dispatch_id}
            </p>
            <p>
              <span className="font-medium">Call ID:</span> {response.call_id}
            </p>
            <p className="text-xs mt-2 text-green-400">{response.message}</p>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-4 bg-destructive/20 border border-destructive/30 rounded-md">
          <h3 className="font-semibold text-destructive mb-1">✗ Error</h3>
          <p className="text-sm text-destructive/90">{error}</p>
        </div>
      )}
    </div>
  );
}
