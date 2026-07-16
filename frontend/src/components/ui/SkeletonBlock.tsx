interface SkeletonBlockProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: number;
  style?: React.CSSProperties;
}

export function SkeletonBlock({
  width = '100%',
  height = 16,
  borderRadius = 6,
  style,
}: SkeletonBlockProps) {
  return (
    <div
      className="skeleton"
      style={{ width, height, borderRadius, ...style }}
    />
  );
}

export function SkeletonRow() {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        padding: '14px 24px',
        borderBottom: '1px solid #e4ece8',
      }}
    >
      <SkeletonBlock width={40} height={40} borderRadius={20} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
        <SkeletonBlock width="45%" height={13} />
        <SkeletonBlock width="28%" height={11} />
      </div>
      <SkeletonBlock width={60} height={22} borderRadius={20} />
      <SkeletonBlock width={80} height={14} />
    </div>
  );
}
