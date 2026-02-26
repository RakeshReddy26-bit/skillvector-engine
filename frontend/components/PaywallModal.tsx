"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useGeoPrice } from "@/lib/use-geo-price";

interface PaywallModalProps {
  open: boolean;
  onClose: () => void;
}

const PRO_FEATURES = [
  "Unlimited skill gap analyses",
  "PDF, DOCX, and image resume uploads",
  "Evidence project generator",
  "Interview prep materials",
  "Priority support",
];

export default function PaywallModal({ open, onClose }: PaywallModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [billing, setBilling] = useState<"monthly" | "yearly">("monthly");
  const geo = useGeoPrice();

  if (!open) return null;

  const isYearly = billing === "yearly";
  const monthlySaving = Math.round(((geo.price * 12 - geo.yearlyPrice) / (geo.price * 12)) * 100);

  const handleUpgrade = async () => {
    setError("");
    setLoading(true);
    try {
      const { checkout_url } = await api.createCheckout();
      window.location.href = checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not start checkout.");
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative w-full max-w-md mx-4 bg-[#0d1117] border border-white/10 rounded-xl p-8 animate-fade-up">
        {/* Close */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-[#5a6478] hover:text-white transition-colors text-lg"
        >
          &times;
        </button>

        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-block font-mono text-[10px] tracking-widest text-[#7c6fff] bg-[#7c6fff]/10 border border-[#7c6fff]/20 px-3 py-1 rounded-sm mb-4">
            FREE LIMIT REACHED
          </div>
          <h2 className="text-2xl font-extrabold tracking-tight">
            Upgrade to <span className="text-[#00e5a0]">Pro</span>
          </h2>
          <p className="mt-2 font-mono text-sm text-[#5a6478]">
            You&apos;ve used all 3 free analyses this month.
          </p>
        </div>

        {/* Billing Toggle */}
        <div className="flex items-center justify-center gap-1 mb-6 bg-[#080b10] rounded-lg p-1">
          <button
            onClick={() => setBilling("monthly")}
            className={`flex-1 py-2 text-[11px] font-bold rounded-md transition-all ${
              !isYearly
                ? "bg-[#00e5a0]/10 text-[#00e5a0] border border-[#00e5a0]/20"
                : "text-[#5a6478] hover:text-white border border-transparent"
            }`}
          >
            MONTHLY
          </button>
          <button
            onClick={() => setBilling("yearly")}
            className={`flex-1 py-2 text-[11px] font-bold rounded-md transition-all relative ${
              isYearly
                ? "bg-[#00e5a0]/10 text-[#00e5a0] border border-[#00e5a0]/20"
                : "text-[#5a6478] hover:text-white border border-transparent"
            }`}
          >
            YEARLY
            <span className="ml-1 text-[9px] text-[#f59e0b]">SAVE {monthlySaving}%</span>
          </button>
        </div>

        {/* Price */}
        <div className="text-center mb-8">
          <span className="text-4xl font-extrabold">
            {isYearly ? geo.yearlyLabel : geo.label}
          </span>
          <span className="text-[#5a6478] font-mono text-sm">
            {isYearly ? "/year" : "/month"}
          </span>
          {isYearly && (
            <p className="mt-1 font-mono text-[10px] text-[#00e5a0]">
              That&apos;s just {geo.symbol}{Math.round(geo.yearlyPrice / 12)}/month
            </p>
          )}
          {geo.countryCode !== "XX" && (
            <p className="mt-1 font-mono text-[10px] text-[#5a6478]">
              Pricing for {geo.country}
            </p>
          )}
        </div>

        {/* Features */}
        <ul className="space-y-3 mb-8">
          {PRO_FEATURES.map((f) => (
            <li key={f} className="flex items-center gap-3 font-mono text-sm">
              <span className="text-[#00e5a0] text-xs">&#10003;</span>
              <span className="text-[#e8edf5]">{f}</span>
            </li>
          ))}
        </ul>

        {error && (
          <div className="text-sm text-[#fca5a5] font-mono bg-[#ef4444]/5 border border-[#ef4444]/20 rounded-lg px-4 py-3 mb-4">
            {error}
          </div>
        )}

        <button
          onClick={handleUpgrade}
          disabled={loading}
          className="w-full py-3 bg-[#00e5a0] text-black font-bold text-sm rounded-lg hover:bg-[#00ffb3] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "REDIRECTING..." : "UPGRADE TO PRO"}
        </button>

        <p className="mt-4 text-center font-mono text-[10px] text-[#5a6478]">
          Cancel anytime. Secure payment.
        </p>
      </div>
    </div>
  );
}
