export function formatCurrency(value: number): string {
  if (value >= 1_000_000) {
    const m = value / 1_000_000;
    return `€${m % 1 === 0 ? m.toFixed(0) : m.toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `€${(value / 1_000).toFixed(0)}K`;
  }
  return `€${value.toLocaleString()}`;
}

export function formatPct(value: number, showSign = true): string {
  const sign = showSign && value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-GB', {
    month: 'short',
    year: 'numeric',
  });
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0])
    .join('')
    .toUpperCase();
}

export interface ColorPair {
  bg: string;
  text: string;
  border: string;
}

export function getPositionColors(position: string): ColorPair {
  switch (position) {
    case 'FW':
      return { bg: '#fff3ed', text: '#c2410c', border: '#fed7aa' };
    case 'MF':
      return { bg: '#eff6ff', text: '#1d4ed8', border: '#bfdbfe' };
    case 'DF':
      return { bg: '#e8f7f0', text: '#15803d', border: '#bbf7d0' };
    case 'GK':
      return { bg: '#faf5ff', text: '#7e22ce', border: '#e9d5ff' };
    default:
      return { bg: '#f3f4f6', text: '#4b5563', border: '#e5e7eb' };
  }
}

export interface TierStyle {
  color: string;
  bg: string;
  label: string;
}

export function getTierStyle(tier: string): TierStyle {
  switch (tier) {
    case 'Tier 1':
      return { color: '#92400e', bg: '#fef3c7', label: 'Tier 1' };
    case 'Tier 2':
      return { color: '#374151', bg: '#f3f4f6', label: 'Tier 2' };
    case 'Tier 3':
      return { color: '#78350f', bg: '#fef3c7', label: 'Tier 3' };
    case 'Tier 4':
      return { color: '#4b5563', bg: '#f9fafb', label: 'Tier 4' };
    default:
      return { color: '#6b7280', bg: '#f9fafb', label: tier };
  }
}

export function getConfidenceColors(level: string): ColorPair {
  switch (level) {
    case 'High':
      return { bg: '#e8f7f0', text: '#15803d', border: '#bbf7d0' };
    case 'Medium':
      return { bg: '#fffbeb', text: '#92400e', border: '#fde68a' };
    case 'Low':
      return { bg: '#fff1f2', text: '#be123c', border: '#fecdd3' };
    default:
      return { bg: '#f3f4f6', text: '#4b5563', border: '#e5e7eb' };
  }
}
