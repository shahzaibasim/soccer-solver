import { Badge } from '../ui/Badge';
import { getPositionColors } from '../../utils/formatters';

interface PositionBadgeProps {
  position: string;
  size?: 'sm' | 'md';
}

const POSITION_LABELS: Record<string, string> = {
  FW: 'Forward',
  MF: 'Midfielder',
  DF: 'Defender',
  GK: 'Goalkeeper',
};

export function PositionBadge({ position, size = 'md' }: PositionBadgeProps) {
  const { bg, text, border } = getPositionColors(position);
  const label = size === 'sm' ? position : (POSITION_LABELS[position] ?? position);
  return (
    <Badge bg={bg} color={text} border={border} size={size}>
      {label}
    </Badge>
  );
}
