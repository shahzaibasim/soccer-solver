interface BadgeProps {
  children: React.ReactNode;
  bg?: string;
  color?: string;
  border?: string;
  size?: 'sm' | 'md';
}

export function Badge({ children, bg = '#f3f4f6', color = '#4b5563', border, size = 'md' }: BadgeProps) {
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: size === 'sm' ? '2px 7px' : '3px 10px',
        borderRadius: 20,
        fontSize: size === 'sm' ? 11 : 12,
        fontWeight: 600,
        letterSpacing: '0.02em',
        background: bg,
        color,
        border: border ? `1px solid ${border}` : 'none',
        whiteSpace: 'nowrap' as const,
      }}
    >
      {children}
    </span>
  );
}
