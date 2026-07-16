interface PercentileBarProps {
  label: string;
  value: number;
  sampleSize?: number;
}

export function PercentileBar({ label, value, sampleSize }: PercentileBarProps) {
  const pct = Math.min(100, Math.max(0, value));
  const color =
    pct >= 75 ? '#1db87a' : pct >= 50 ? '#3b82f6' : pct >= 25 ? '#f59e0b' : '#f87171';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'baseline',
        }}
      >
        <span style={{ fontSize: 13, fontWeight: 500, color: '#0f1f1b' }}>{label}</span>
        <span style={{ fontSize: 13, fontWeight: 700, color }}>
          {pct.toFixed(1)}
          <span style={{ fontSize: 11, fontWeight: 500, color: '#5c7069' }}>th</span>
        </span>
      </div>
      <div
        style={{
          height: 6,
          borderRadius: 3,
          background: '#e4ece8',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${pct}%`,
            borderRadius: 3,
            background: color,
            transition: 'width 0.6s cubic-bezier(0.16, 1, 0.3, 1)',
          }}
        />
      </div>
      {sampleSize !== undefined && (
        <span style={{ fontSize: 11, color: '#94a3a0' }}>
          vs {sampleSize.toLocaleString()} peers
        </span>
      )}
    </div>
  );
}
