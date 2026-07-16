export function LoadingSpinner({ size = 32 }: { size?: number }) {
  return (
    <div
      style={{
        width: size,
        height: size,
        border: `3px solid #e4ece8`,
        borderTopColor: '#1db87a',
        borderRadius: '50%',
        animation: 'spin 0.7s linear infinite',
        flexShrink: 0,
      }}
    />
  );
}

export function PageLoader() {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        minHeight: 300,
        flexDirection: 'column',
        gap: 16,
      }}
    >
      <LoadingSpinner size={40} />
      <p style={{ color: '#5c7069', fontSize: 14 }}>Loading…</p>
    </div>
  );
}
