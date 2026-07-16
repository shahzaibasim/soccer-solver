import { useState, useEffect } from 'react';
import { getPlayerProfile } from '../api/client';
import type { PlayerProfileResponse, ApiError } from '../types/api';

export function usePlayerProfile(playerId: number) {
  const [data, setData] = useState<PlayerProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setData(null);
    getPlayerProfile(playerId)
      .then(setData)
      .catch((err: ApiError) => setError(err))
      .finally(() => setLoading(false));
  }, [playerId]);

  return { data, loading, error };
}
