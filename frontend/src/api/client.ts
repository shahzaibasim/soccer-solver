import type {
  PlayerSearchResponse,
  PlayerProfileResponse,
  TransitionPrediction,
  ApiError,
} from '../types/api';

const BASE = '/api';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const err: ApiError = await res
      .json()
      .catch(() => ({ detail: `HTTP ${res.status}: ${res.statusText}` }));
    throw err;
  }
  return res.json() as Promise<T>;
}

export async function searchPlayers(
  q: string,
  limit = 20,
  offset = 0,
): Promise<PlayerSearchResponse> {
  const params = new URLSearchParams({
    q,
    limit: String(limit),
    offset: String(offset),
  });
  const res = await fetch(`${BASE}/players/search?${params}`);
  return handleResponse<PlayerSearchResponse>(res);
}

export async function getPlayerProfile(
  playerId: number,
): Promise<PlayerProfileResponse> {
  const res = await fetch(`${BASE}/players/${playerId}`);
  return handleResponse<PlayerProfileResponse>(res);
}

export async function simulateTransition(
  playerId: number,
  destinationTier: string,
  destinationClub?: string,
): Promise<TransitionPrediction> {
  const params = new URLSearchParams({ destination_tier: destinationTier });
  if (destinationClub?.trim()) params.set('destination_club', destinationClub.trim());
  const res = await fetch(`${BASE}/players/${playerId}/transitions/simulate?${params}`);
  return handleResponse<TransitionPrediction>(res);
}
