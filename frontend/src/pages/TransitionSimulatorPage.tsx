import { useState, type FormEvent } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, BarChart2 } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { usePlayerProfile } from '../hooks/usePlayerProfile';
import { useTransition } from '../hooks/useTransition';
import { PlayerAvatar } from '../components/shared/PlayerAvatar';
import { PositionBadge } from '../components/shared/PositionBadge';
import { TierBadge } from '../components/shared/TierBadge';
import { ConfidenceBadge } from '../components/shared/ConfidenceBadge';
import { ValueRangeDisplay } from '../components/shared/ValueRangeDisplay';
import { Card, CardHeader } from '../components/ui/Card';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { formatCurrency, formatPct, formatDate } from '../utils/formatters';
import type { SimilarTransition } from '../types/api';

const VALID_TIERS = ['Tier 1', 'Tier 2', 'Tier 3', 'Tier 4'] as const;

export function TransitionSimulatorPage() {
  const { id } = useParams<{ id: string }>();
  const playerId = Number(id);

  const { data: player, loading: playerLoading } = usePlayerProfile(playerId);
  const { data: prediction, loading: simLoading, error: simError, simulate } = useTransition(playerId);

  const [destinationTier, setDestinationTier] = useState<string>('Tier 1');
  const [destinationClub, setDestinationClub] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    simulate(destinationTier, destinationClub || undefined);
  };

  return (
    <div className="page-fade-in">
      <div className="page-header">
        {player && (
          <Link to={`/players/${playerId}`} className="back-link">
            <ArrowLeft size={15} />
            Back to {player.player_name.split(' ')[0]}'s profile
          </Link>
        )}
        {!player && (
          <Link to="/search" className="back-link">
            <ArrowLeft size={15} />
            Back to search
          </Link>
        )}
      </div>

      <div className="page-body">
        <div className="simulator-grid">
          {/* ── Left: Input panel ─────────────────────────────────────── */}
          <Card style={{ height: 'fit-content' }}>
            <CardHeader title="Transition Simulator" subtitle="Set a destination and run the model" />
            <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

              {/* Player chip */}
              {playerLoading && (
                <div style={{ display: 'flex', justifyContent: 'center', padding: 20 }}>
                  <LoadingSpinner />
                </div>
              )}
              {player && (
                <div className="player-chip">
                  <PlayerAvatar imageUrl={player.image_url} name={player.player_name} size={48} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p className="player-chip-name">{player.player_name}</p>
                    <div style={{ display: 'flex', gap: 6, marginTop: 4, flexWrap: 'wrap' as const }}>
                      <PositionBadge position={player.position} size="sm" />
                      <TierBadge tier={player.current_league_tier} size="sm" />
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' as const, flexShrink: 0 }}>
                    <p className="player-chip-value">{formatCurrency(player.current_market_value_eur)}</p>
                    <p style={{ fontSize: 11, color: '#94a3a0' }}>current value</p>
                  </div>
                </div>
              )}

              <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
                {/* Destination tier */}
                <div className="form-field">
                  <label className="form-label" htmlFor="destination-tier">
                    Destination League Tier
                  </label>
                  <select
                    id="destination-tier"
                    className="form-select"
                    value={destinationTier}
                    onChange={(e) => setDestinationTier(e.target.value)}
                  >
                    {VALID_TIERS.map((tier) => (
                      <option key={tier} value={tier}>
                        {tier}
                      </option>
                    ))}
                  </select>
                  {player && (
                    <p className="form-hint">
                      Currently in {player.current_league_tier}
                      {destinationTier === player.current_league_tier
                        ? ' — lateral move'
                        : parseInt(destinationTier.slice(-1)) < parseInt(player.current_league_tier.slice(-1))
                        ? ' — ↑ step up'
                        : ' — ↓ step down'}
                    </p>
                  )}
                </div>

                {/* Destination club (optional) */}
                <div className="form-field">
                  <label className="form-label" htmlFor="destination-club">
                    Destination Club{' '}
                    <span style={{ fontWeight: 400, color: '#94a3a0' }}>(optional)</span>
                  </label>
                  <input
                    id="destination-club"
                    className="form-input"
                    type="text"
                    placeholder="e.g. Arsenal FC"
                    value={destinationClub}
                    onChange={(e) => setDestinationClub(e.target.value)}
                  />
                  <p className="form-hint">Used in the narrative summary only.</p>
                </div>

                <button
                  className="btn-primary btn-full"
                  type="submit"
                  disabled={simLoading || playerLoading}
                  id="run-simulation-btn"
                >
                  {simLoading ? (
                    <span style={{ display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'center' }}>
                      <LoadingSpinner size={16} />
                      Running model…
                    </span>
                  ) : (
                    'Run Simulation →'
                  )}
                </button>
              </form>
            </div>
          </Card>

          {/* ── Right: Results panel ───────────────────────────────────── */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Idle state */}
            {!prediction && !simLoading && !simError && (
              <Card>
                <EmptyState
                  type="idle"
                  title="No simulation yet"
                  body="Select a destination tier and click 'Run Simulation' to see the predicted value range and comparable historical transfers."
                />
              </Card>
            )}

            {/* Loading */}
            {simLoading && (
              <Card>
                <div style={{ padding: 48, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
                  <LoadingSpinner size={36} />
                  <p style={{ fontSize: 14, color: '#5c7069' }}>Analysing comparable transfers…</p>
                </div>
              </Card>
            )}

            {/* Error */}
            {!simLoading && simError && (
              <Card>
                <EmptyState
                  type="error"
                  title="Simulation failed"
                  body={simError.detail}
                />
              </Card>
            )}

            {/* Results */}
            {!simLoading && prediction && (
              <>
                {/* Value range card */}
                <Card>
                  <div className="card-body">
                    <ValueRangeDisplay
                      low={prediction.value_range_low_eur}
                      high={prediction.value_range_high_eur}
                      current={prediction.current_value_eur}
                      meanChangePct={prediction.predicted_change_pct_mean}
                    />
                    <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' as const }}>
                      <ConfidenceBadge
                        level={prediction.confidence_level}
                        score={prediction.confidence_score}
                      />
                      <span style={{ fontSize: 13, color: '#5c7069' }}>
                        Based on {prediction.sample_size} comparable transfer{prediction.sample_size !== 1 ? 's' : ''}
                      </span>
                    </div>
                  </div>
                </Card>

                {/* Thin sample warning */}
                {prediction.thin_sample_warning && (
                  <div className="warning-banner">
                    <AlertTriangle size={16} color="#92400e" style={{ flexShrink: 0 }} />
                    <p>
                      <strong>{prediction.sample_size === 0 ? 'No sample:' : 'Thin sample:'}</strong>{' '}
                      {prediction.sample_size === 0
                        ? '0 comparable transfers found. The prediction is highly uncertain.'
                        : `Only ${prediction.sample_size} comparable ${
                            prediction.sample_size === 1 ? 'transfer' : 'transfers'
                          } found. Treat this range as directional, not precise.`}
                    </p>
                  </div>
                )}

                {/* Narrative card */}
                <Card>
                  <CardHeader title="Analysis" />
                  <div className="card-body">
                    <blockquote className="narrative">{prediction.narrative}</blockquote>
                  </div>
                </Card>

                {/* Comparable transitions */}
                {prediction.comparable_transitions.length > 0 && (
                  <Card>
                    <CardHeader
                      title="Comparable Transfers"
                      subtitle={`${prediction.comparable_transitions.length} historical moves matching this profile`}
                      action={<BarChart2 size={16} color="#94a3a0" />}
                    />

                    {/* Mini bar chart */}
                    <div style={{ padding: '0 24px' }}>
                      <ComparableChart transitions={prediction.comparable_transitions.slice(0, 6)} />
                    </div>

                    {/* Table */}
                    <div style={{ overflowX: 'auto' }}>
                      <table className="results-table">
                        <thead>
                          <tr>
                            <th>Player</th>
                            <th>Route</th>
                            <th>Before</th>
                            <th>After</th>
                            <th style={{ textAlign: 'right' }}>Δ Value</th>
                            <th style={{ textAlign: 'right' }}>Date</th>
                          </tr>
                        </thead>
                        <tbody>
                          {prediction.comparable_transitions.map((comp, idx) => {
                            const isUp = comp.value_change_pct >= 0;
                            return (
                              <tr key={idx} className="results-row" style={{ cursor: 'default' }}>
                                <td>
                                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <span className="player-name" style={{ fontSize: 13 }}>
                                      {comp.player_name}
                                    </span>
                                    {comp.age_at_transfer && (
                                      <span style={{ fontSize: 11, color: '#94a3a0' }}>
                                        Age {comp.age_at_transfer}
                                      </span>
                                    )}
                                  </div>
                                </td>
                                <td>
                                  <span style={{ fontSize: 12, color: '#5c7069' }}>
                                    {comp.origin_tier} → {comp.destination_tier}
                                  </span>
                                </td>
                                <td>
                                  <span style={{ fontSize: 13 }}>
                                    {formatCurrency(comp.value_before_eur)}
                                  </span>
                                </td>
                                <td>
                                  <span style={{ fontSize: 13, fontWeight: 600 }}>
                                    {formatCurrency(comp.value_after_eur)}
                                  </span>
                                </td>
                                <td style={{ textAlign: 'right' }}>
                                  <span
                                    style={{
                                      fontSize: 13,
                                      fontWeight: 700,
                                      color: isUp ? '#15803d' : '#be123c',
                                    }}
                                  >
                                    {formatPct(comp.value_change_pct)}
                                  </span>
                                </td>
                                <td style={{ textAlign: 'right', color: '#94a3a0', fontSize: 12 }}>
                                  {formatDate(comp.transfer_date)}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </Card>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Comparable bar chart ───────────────────────────────────────────────────

interface ChartDatum {
  name: string;
  before: number;
  after: number;
  pct: number;
}

function ComparableChart({ transitions }: { transitions: SimilarTransition[] }) {
  const chartData: ChartDatum[] = transitions.map((t) => ({
    name: t.player_name.split(' ').pop() ?? t.player_name,
    before: Math.round(t.value_before_eur / 1_000_000),
    after: Math.round(t.value_after_eur / 1_000_000),
    pct: t.value_change_pct,
  }));

  return (
    <div style={{ height: 160, marginBottom: 8 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} barGap={4} barCategoryGap="30%">
          <XAxis
            dataKey="name"
            tick={{ fontSize: 11, fill: '#5c7069' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#94a3a0' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v: number) => `€${v}M`}
            width={44}
          />
          <Tooltip content={<CustomBarTooltip />} />
          <Bar dataKey="before" radius={[4, 4, 0, 0]} fill="#e4ece8" />
          <Bar dataKey="after" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={index}
                fill={entry.pct >= 0 ? '#1db87a' : '#f87171'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

// ─── Custom tooltip (avoids recharts Formatter generic type issues) ─────────

interface TooltipPayload {
  name: string;
  value: number;
  color: string;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayload[];
  label?: string;
}

function CustomBarTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div
      style={{
        background: '#fff',
        border: '1px solid #e4ece8',
        borderRadius: 8,
        padding: '8px 12px',
        fontSize: 12,
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      }}
    >
      <p style={{ fontWeight: 600, marginBottom: 4, color: '#0f1f1b' }}>{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color ?? '#5c7069' }}>
          {p.name === 'before' ? 'Before' : 'After'}: €{p.value}M
        </p>
      ))}
    </div>
  );
}
