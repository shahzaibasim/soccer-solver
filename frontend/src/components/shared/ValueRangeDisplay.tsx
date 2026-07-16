import { formatCurrency, formatPct } from '../../utils/formatters';

interface ValueRangeDisplayProps {
  low: number;
  high: number;
  current: number;
  meanChangePct: number;
}

export function ValueRangeDisplay({
  low,
  high,
  current,
  meanChangePct,
}: ValueRangeDisplayProps) {
  const isUp = meanChangePct >= 0;
  const changeColor = isUp ? '#15803d' : '#be123c';
  const changeBg = isUp ? '#e8f7f0' : '#fff1f2';

  // Position of current on the range bar (clamped)
  const rangeSpan = high - low || 1;
  const currentPos = Math.min(100, Math.max(0, ((current - low) / rangeSpan) * 100));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Value range numbers */}
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 12 }}>
        <div>
          <p style={{ fontSize: 11, fontWeight: 500, color: '#5c7069', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Projected Value Range
          </p>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
            <span style={{ fontSize: 32, fontWeight: 800, color: '#0f1f1b', lineHeight: 1 }}>
              {formatCurrency(low)}
            </span>
            <span style={{ fontSize: 20, fontWeight: 400, color: '#94a3a0' }}>–</span>
            <span style={{ fontSize: 32, fontWeight: 800, color: '#0f1f1b', lineHeight: 1 }}>
              {formatCurrency(high)}
            </span>
          </div>
          <p style={{ fontSize: 12, color: '#94a3a0', marginTop: 4 }}>
            within 6–12 months post-transfer
          </p>
        </div>

        {/* Mean change chip */}
        <div
          style={{
            marginLeft: 'auto',
            background: changeBg,
            borderRadius: 10,
            padding: '8px 14px',
            textAlign: 'center',
          }}
        >
          <p style={{ fontSize: 20, fontWeight: 800, color: changeColor, lineHeight: 1 }}>
            {formatPct(meanChangePct)}
          </p>
          <p style={{ fontSize: 11, color: changeColor, opacity: 0.8, marginTop: 2 }}>
            avg change
          </p>
        </div>
      </div>

      {/* Range bar */}
      <div>
        <div style={{ position: 'relative', height: 8, borderRadius: 4, background: '#e4ece8' }}>
          {/* Filled range */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              height: '100%',
              width: '100%',
              borderRadius: 4,
              background: 'linear-gradient(90deg, #bbf7d0, #1db87a)',
            }}
          />
          {/* Current value marker */}
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: `${currentPos}%`,
              transform: 'translate(-50%, -50%)',
              width: 16,
              height: 16,
              borderRadius: '50%',
              background: '#fff',
              border: '3px solid #0f1f1b',
              boxShadow: '0 1px 4px rgba(0,0,0,0.15)',
            }}
            title={`Current: ${formatCurrency(current)}`}
          />
        </div>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: 6,
          }}
        >
          <span style={{ fontSize: 11, color: '#5c7069' }}>p25 · {formatCurrency(low)}</span>
          <span style={{ fontSize: 11, color: '#5c7069' }}>p75 · {formatCurrency(high)}</span>
        </div>
      </div>
    </div>
  );
}
