import { useState, useCallback } from 'react';
import { searchPlayers } from '../api/client';
import type { PlayerSearchResponse, ApiError } from '../types/api';

const PAGE_SIZE = 20;

interface SearchState {
  data: PlayerSearchResponse | null;
  loading: boolean;
  error: ApiError | null;
  query: string;
  page: number;
}

export function useSearch() {
  const [state, setState] = useState<SearchState>({
    data: null,
    loading: false,
    error: null,
    query: '',
    page: 0,
  });

  const search = useCallback(async (q: string, page = 0) => {
    const trimmed = q.trim();
    if (!trimmed) return;
    setState((prev) => ({ ...prev, loading: true, error: null, query: trimmed, page }));
    try {
      const data = await searchPlayers(trimmed, PAGE_SIZE, page * PAGE_SIZE);
      setState((prev) => ({ ...prev, data, loading: false }));
    } catch (err) {
      setState((prev) => ({ ...prev, error: err as ApiError, loading: false, data: null }));
    }
  }, []);

  const goToPage = useCallback(
    (page: number) => {
      search(state.query, page);
    },
    [search, state.query],
  );

  const totalPages = state.data ? Math.ceil(state.data.total / PAGE_SIZE) : 0;

  return { ...state, search, goToPage, pageSize: PAGE_SIZE, totalPages };
}
