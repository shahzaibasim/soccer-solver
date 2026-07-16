import { SearchX, AlertCircle } from 'lucide-react';

interface EmptyStateProps {
  type?: 'no-results' | 'error' | 'idle';
  title: string;
  body?: string;
  action?: React.ReactNode;
}

export function EmptyState({ type = 'idle', title, body, action }: EmptyStateProps) {
  const Icon = type === 'error' ? AlertCircle : SearchX;
  const iconColor = type === 'error' ? '#be123c' : '#94a3a0';

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px 32px',
        textAlign: 'center',
        gap: 12,
      }}
    >
      <div
        style={{
          width: 56,
          height: 56,
          borderRadius: 16,
          background: type === 'error' ? '#fff1f2' : '#e8f7f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Icon size={24} color={iconColor} />
      </div>
      <p
        style={{
          fontSize: 16,
          fontWeight: 600,
          color: '#0f1f1b',
          marginTop: 4,
        }}
      >
        {title}
      </p>
      {body && (
        <p style={{ fontSize: 13, color: '#5c7069', maxWidth: 320, lineHeight: 1.5 }}>
          {body}
        </p>
      )}
      {action && <div style={{ marginTop: 8 }}>{action}</div>}
    </div>
  );
}
