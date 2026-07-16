import { Badge } from '../ui/Badge';
import { getConfidenceColors } from '../../utils/formatters';

interface ConfidenceBadgeProps {
  level: string;
  score?: number;
}

export function ConfidenceBadge({ level, score }: ConfidenceBadgeProps) {
  const { bg, text, border } = getConfidenceColors(level);
  return (
    <Badge bg={bg} color={text} border={border}>
      {level} Confidence{score !== undefined ? ` · ${(score * 100).toFixed(0)}%` : ''}
    </Badge>
  );
}
