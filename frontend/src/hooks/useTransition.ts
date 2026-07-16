import { useState } from 'react';
import { simulateTransition } from '../api/client';
import type { TransitionPrediction, ApiError } from '../types/api';

export function useTransition(playerId: number) {
  const [data, setData] = useState<TransitionPrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const simulate = async (destinationTier: string, destinationClub?: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await simulateTransition(playerId, destinationTier, destinationClub);
      setData(result);
    } catch (err) {
      setError(err as ApiError);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setData(null);
    setError(null);
  };

  return { data, loading, error, simulate, reset };
}
