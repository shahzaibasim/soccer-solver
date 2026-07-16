import { useState, useEffect, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, ArrowRight, ChevronLeft, ChevronRight } from 'lucide-react';
import { useSearch } from '../hooks/useSearch';
import { PlayerAvatar } from '../components/shared/PlayerAvatar';
import { PositionBadge } from '../components/shared/PositionBadge';
import { TierBadge } from '../components/shared/TierBadge';
import { SkeletonRow } from '../components/ui/SkeletonBlock';
import { EmptyState } from '../components/ui/EmptyState';
import { formatCurrency } from '../utils/formatters';
import type { PlayerSearchResult } from '../types/api';

export function SearchPage() {
  const navigate = useNavigate();
  const { data, loading, error, query, page, totalPages, search, goToPage } = useSearch();
  const [inputValue, setInputValue] = useState('');

  useEffect(() => {
    // Load default results so the page isn't empty, but leave the input empty.
    search('a');
  }, [search]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    search(inputValue);
  };

  const handlePlayerClick = (player: PlayerSearchResult) => {
    navigate(`/players/${player.player_id}`);
  };

  return (
    <div className="page-fade-in">
      {/* Hero */}
      <div className="search-hero">
        <div className="pitch-watermark">
          <PitchLines />
        </div>
        <div className="search-hero-content">
          <p className="search-eyebrow">Soccer Solver</p>
          <h1 className="search-heading">Scout Smarter.</h1>
          <p className="search-subheading">
            Search across 50,000+ professional players worldwide.
          </p>
          <form className="search-form" onSubmit={handleSubmit}>
            <div className="search-input-wrap">
              <Search size={18} className="search-icon-left" color="#94a3a0" />
              <input
                id="player-search-input"
                className="search-input"
                type="text"
                placeholder="Search by player name…"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                autoFocus
              />
            </div>
            <button className="btn-primary" type="submit" disabled={loading}>
              {loading ? 'Searching…' : 'Search'}
            </button>
          </form>
        </div>
      </div>

      {/* Results */}
      <div className="page-body">
        {(data || loading || error) && (
          <div className="card" style={{ overflow: 'hidden' }}>
            {/* Results header */}
            {data && !loading && (
              <div className="results-header">
                <p className="results-count">
                  <span className="results-count-num">{data.total.toLocaleString()}</span>
                  {' '}player{data.total !== 1 ? 's' : ''} found for{' '}
                  <span className="results-query">"{query}"</span>
                </p>
                {totalPages > 1 && (
                  <span style={{ fontSize: 13, color: '#5c7069' }}>
                    Page {page + 1} of {totalPages}
                  </span>
                )}
              </div>
            )}

            {/* Loading skeletons */}
            {loading && (
              <div>
                {Array.from({ length: 8 }).map((_, i) => (
                  <SkeletonRow key={i} />
                ))}
              </div>
            )}

            {/* Error */}
            {!loading && error && (
              <EmptyState
                type="error"
                title="Something went wrong"
                body={error.detail}
              />
            )}

            {/* No results */}
            {!loading && data && data.results.length === 0 && (
              <EmptyState
                type="no-results"
                title="No players found"
                body={`No players matched "${query}". Try a different name or spelling.`}
              />
            )}

            {/* Results table */}
            {!loading && data && data.results.length > 0 && (
              <>
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>Player</th>
                      <th>Position</th>
                      <th>League</th>
                      <th>Tier</th>
                      <th style={{ textAlign: 'right' }}>Market Value</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {data.results.map((player) => (
                      <tr
                        key={player.player_id}
                        className="results-row"
                        onClick={() => handlePlayerClick(player)}
                        tabIndex={0}
                        onKeyDown={(e) => e.key === 'Enter' && handlePlayerClick(player)}
                        role="button"
                        aria-label={`View profile for ${player.player_name}`}
                      >
                        <td>
                          <div className="player-cell">
                            <PlayerAvatar
                              imageUrl={player.image_url}
                              name={player.player_name}
                              size={38}
                            />
                            <div>
                              <p className="player-name">{player.player_name}</p>
                              <p className="player-club">{player.current_club}</p>
                            </div>
                          </div>
                        </td>
                        <td>
                          <PositionBadge position={player.position} size="sm" />
                        </td>
                        <td>
                          <span className="league-code">{player.current_league}</span>
                        </td>
                        <td>
                          <TierBadge tier={player.current_league_tier} size="sm" />
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <span className="market-value">
                            {formatCurrency(player.current_market_value_eur)}
                          </span>
                        </td>
                        <td style={{ width: 36, textAlign: 'right' }}>
                          <ArrowRight size={15} color="#94a3a0" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="pagination">
                    <button
                      className="btn-ghost"
                      onClick={() => goToPage(page - 1)}
                      disabled={page === 0}
                      aria-label="Previous page"
                    >
                      <ChevronLeft size={16} />
                      Prev
                    </button>
                    <div className="pagination-dots">
                      {Array.from({ length: Math.min(totalPages, 7) }).map((_, i) => {
                        const pageNum = i;
                        return (
                          <button
                            key={pageNum}
                            className={`pagination-dot${page === pageNum ? ' active' : ''}`}
                            onClick={() => goToPage(pageNum)}
                            aria-label={`Page ${pageNum + 1}`}
                          />
                        );
                      })}
                    </div>
                    <button
                      className="btn-ghost"
                      onClick={() => goToPage(page + 1)}
                      disabled={page >= totalPages - 1}
                      aria-label="Next page"
                    >
                      Next
                      <ChevronRight size={16} />
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Idle state */}
        {!data && !loading && !error && (
          <div className="idle-hint">
            <p>Start typing a player name above to begin your search.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function PitchLines() {
  return (
    <svg
      width="100%"
      height="100%"
      viewBox="0 0 800 300"
      preserveAspectRatio="xMidYMid slice"
      fill="none"
    >
      {/* Outer boundary */}
      <rect x="40" y="20" width="720" height="260" rx="4" stroke="currentColor" strokeWidth="1.5" />
      {/* Centre line */}
      <line x1="400" y1="20" x2="400" y2="280" stroke="currentColor" strokeWidth="1.5" />
      {/* Centre circle */}
      <circle cx="400" cy="150" r="60" stroke="currentColor" strokeWidth="1.5" />
      {/* Centre dot */}
      <circle cx="400" cy="150" r="3" fill="currentColor" />
      {/* Left penalty box */}
      <rect x="40" y="70" width="100" height="160" stroke="currentColor" strokeWidth="1.5" />
      {/* Right penalty box */}
      <rect x="660" y="70" width="100" height="160" stroke="currentColor" strokeWidth="1.5" />
      {/* Left goal */}
      <rect x="40" y="110" width="36" height="80" stroke="currentColor" strokeWidth="1.5" />
      {/* Right goal */}
      <rect x="724" y="110" width="36" height="80" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}
