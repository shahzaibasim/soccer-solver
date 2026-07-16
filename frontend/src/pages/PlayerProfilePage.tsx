import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, TrendingUp, MapPin, Calendar, Activity } from 'lucide-react';
import { usePlayerProfile } from '../hooks/usePlayerProfile';
import { PlayerAvatar } from '../components/shared/PlayerAvatar';
import { PositionBadge } from '../components/shared/PositionBadge';
import { TierBadge } from '../components/shared/TierBadge';
import { PercentileBar } from '../components/shared/PercentileBar';
import { Card, CardHeader } from '../components/ui/Card';
import { PageLoader } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { formatCurrency } from '../utils/formatters';

export function PlayerProfilePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const playerId = Number(id);

  const { data, loading, error } = usePlayerProfile(playerId);

  if (loading) return <PageLoader />;

  if (error || !data) {
    return (
      <div className="page-body">
        <EmptyState
          type="error"
          title="Player not found"
          body={error?.detail ?? 'This player does not exist in the dataset.'}
          action={
            <button className="btn-ghost" onClick={() => navigate('/search')}>
              ← Back to search
            </button>
          }
        />
      </div>
    );
  }

  return (
    <div className="page-fade-in">
      {/* Page header */}
      <div className="page-header">
        <Link to="/search" className="back-link">
          <ArrowLeft size={15} />
          Back to search
        </Link>
      </div>

      <div className="page-body" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* Hero card */}
        <Card>
          <div className="profile-hero">
            <PlayerAvatar imageUrl={data.image_url} name={data.player_name} size={88} />
            <div className="profile-hero-info">
              <div className="profile-badges">
                <PositionBadge position={data.position} />
                <TierBadge tier={data.current_league_tier} />
              </div>
              <h1 className="profile-name">{data.player_name}</h1>
              <div className="profile-meta">
                <span className="profile-meta-item">
                  <MapPin size={13} />
                  {data.current_club}
                </span>
                <span className="profile-meta-sep">·</span>
                <span className="profile-meta-item">
                  <Activity size={13} />
                  {data.current_league}
                </span>
                <span className="profile-meta-sep">·</span>
                <span className="profile-meta-item">
                  <Calendar size={13} />
                  Age {data.age}
                </span>
              </div>
            </div>
            <div className="profile-value-block">
              <p className="profile-value-label">Market Value</p>
              <p className="profile-value">{formatCurrency(data.current_market_value_eur)}</p>
            </div>
          </div>
        </Card>

        {/* Raw metrics row */}
        <div className="stats-row">
          <div className="stat-card">
            <p className="stat-value">{data.metrics.goals}</p>
            <p className="stat-label">Goals</p>
          </div>
          <div className="stat-card">
            <p className="stat-value">{data.metrics.assists}</p>
            <p className="stat-label">Assists</p>
          </div>
          <div className="stat-card">
            <p className="stat-value">{data.metrics.minutes_played.toLocaleString()}</p>
            <p className="stat-label">Minutes</p>
          </div>
          <div className="stat-card stat-card-highlight">
            <p className="stat-value stat-value-accent">
              {formatCurrency(data.current_market_value_eur)}
            </p>
            <p className="stat-label">Market Value</p>
          </div>
        </div>

        {/* Percentiles grid */}
        <div className="percentiles-grid">
          <Card>
            <CardHeader
              title="vs Position Peers"
              subtitle={`All ${data.position} players globally`}
            />
            <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <PercentileBar
                label="Goals"
                value={data.position_percentiles.goals_percentile}
                sampleSize={data.position_percentiles.sample_size}
              />
              <PercentileBar
                label="Assists"
                value={data.position_percentiles.assists_percentile}
                sampleSize={data.position_percentiles.sample_size}
              />
              <PercentileBar
                label="Minutes Played"
                value={data.position_percentiles.minutes_percentile}
                sampleSize={data.position_percentiles.sample_size}
              />
            </div>
          </Card>

          <Card>
            <CardHeader
              title="vs League Peers"
              subtitle={`${data.position} players in ${data.current_league}`}
            />
            <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <PercentileBar
                label="Goals"
                value={data.league_percentiles.goals_percentile}
                sampleSize={data.league_percentiles.sample_size}
              />
              <PercentileBar
                label="Assists"
                value={data.league_percentiles.assists_percentile}
                sampleSize={data.league_percentiles.sample_size}
              />
              <PercentileBar
                label="Minutes Played"
                value={data.league_percentiles.minutes_percentile}
                sampleSize={data.league_percentiles.sample_size}
              />
            </div>
          </Card>
        </div>

        {/* Transition CTA */}
        <Card className="cta-card">
          <div className="cta-inner">
            <div className="cta-icon">
              <TrendingUp size={22} color="#1db87a" />
            </div>
            <div>
              <p className="cta-title">Ready to explore a transfer?</p>
              <p className="cta-body">
                Run the Transition Simulator to see a predicted value range and comparable
                historical moves for {data.player_name.split(' ')[0]}.
              </p>
            </div>
            <Link
              to={`/players/${data.player_id}/simulate`}
              className="btn-primary"
              style={{ whiteSpace: 'nowrap', marginLeft: 'auto' }}
            >
              Simulate Transfer →
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
