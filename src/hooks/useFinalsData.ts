import { useState, useEffect } from "react";
import type { Final, Meta } from "../types";

interface FinalsDataResult {
  finals: Final[];
  loading: boolean;
  error: string | null;
  meta: Meta | null;
}

export function useFinalsData(): FinalsDataResult {
  const [finals, setFinals] = useState<Final[]>([]);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const base = import.meta.env.BASE_URL;

    async function load() {
      try {
        const [finalsRes, metaRes] = await Promise.all([
          fetch(`${base}data/finals.json`),
          fetch(`${base}data/meta.json`).catch(() => null),
        ]);

        if (!finalsRes.ok) {
          throw new Error(`Failed to load finals data (HTTP ${finalsRes.status})`);
        }

        const finalsData: Final[] = await finalsRes.json();
        setFinals(finalsData);

        if (metaRes?.ok) {
          const metaData: Meta = await metaRes.json();
          setMeta(metaData);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error loading data");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  return { finals, loading, error, meta };
}
