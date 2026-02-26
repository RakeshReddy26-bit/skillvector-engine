"use client";

import { useEffect, useState } from "react";

export interface GeoPrice {
  country: string;
  countryCode: string;
  currency: string;
  symbol: string;
  price: number;
  label: string;
}

const REGIONAL_PRICES: Record<string, GeoPrice> = {
  IN: { country: "India", countryCode: "IN", currency: "INR", symbol: "₹", price: 199, label: "₹199" },
  US: { country: "United States", countryCode: "US", currency: "USD", symbol: "$", price: 9, label: "$9" },
  GB: { country: "United Kingdom", countryCode: "GB", currency: "GBP", symbol: "£", price: 7, label: "£7" },
  DE: { country: "Germany", countryCode: "DE", currency: "EUR", symbol: "€", price: 9, label: "€9" },
  FR: { country: "France", countryCode: "FR", currency: "EUR", symbol: "€", price: 9, label: "€9" },
  NL: { country: "Netherlands", countryCode: "NL", currency: "EUR", symbol: "€", price: 9, label: "€9" },
  BR: { country: "Brazil", countryCode: "BR", currency: "USD", symbol: "$", price: 5, label: "$5" },
  NG: { country: "Nigeria", countryCode: "NG", currency: "USD", symbol: "$", price: 3, label: "$3" },
  PK: { country: "Pakistan", countryCode: "PK", currency: "USD", symbol: "$", price: 3, label: "$3" },
  BD: { country: "Bangladesh", countryCode: "BD", currency: "USD", symbol: "$", price: 3, label: "$3" },
  PH: { country: "Philippines", countryCode: "PH", currency: "USD", symbol: "$", price: 4, label: "$4" },
};

// Default for EU countries not explicitly listed
const EU_DEFAULT: GeoPrice = { country: "Europe", countryCode: "EU", currency: "EUR", symbol: "€", price: 9, label: "€9" };
const GLOBAL_DEFAULT: GeoPrice = { country: "Global", countryCode: "XX", currency: "USD", symbol: "$", price: 9, label: "$9" };

const EU_CODES = new Set([
  "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
  "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
  "PL", "PT", "RO", "SK", "SI", "ES", "SE",
]);

export function useGeoPrice(): GeoPrice {
  const [price, setPrice] = useState<GeoPrice>(GLOBAL_DEFAULT);

  useEffect(() => {
    const cached = sessionStorage.getItem("sv_geo");
    if (cached) {
      try {
        setPrice(JSON.parse(cached));
        return;
      } catch { /* ignore */ }
    }

    fetch("https://ipapi.co/json/", { signal: AbortSignal.timeout(5000) })
      .then((res) => res.json())
      .then((data) => {
        const code = data?.country_code ?? "XX";
        let geo: GeoPrice;

        if (REGIONAL_PRICES[code]) {
          geo = REGIONAL_PRICES[code];
        } else if (EU_CODES.has(code)) {
          geo = { ...EU_DEFAULT, country: data.country_name ?? "Europe", countryCode: code };
        } else {
          geo = { ...GLOBAL_DEFAULT, country: data.country_name ?? "Global", countryCode: code };
        }

        setPrice(geo);
        sessionStorage.setItem("sv_geo", JSON.stringify(geo));
      })
      .catch(() => {
        // Fallback to default pricing on error
      });
  }, []);

  return price;
}
