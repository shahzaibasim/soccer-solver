import { Badge } from '../ui/Badge';
import { getTierStyle } from '../../utils/formatters';

interface TierBadgeProps {
  tier: string;
  size?: 'sm' | 'md';
}

export function TierBadge({ tier, size = 'md' }: TierBadgeProps) {
  const { color, bg, label } = getTierStyle(tier);
  return (
    <Badge bg={bg} color={color} size={size}>
      {label}
    </Badge>
  );
}
