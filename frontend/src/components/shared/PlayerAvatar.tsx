import { getInitials } from '../../utils/formatters';

interface PlayerAvatarProps {
  imageUrl: string | null;
  name: string;
  size?: number;
}

export function PlayerAvatar({ imageUrl, name, size = 40 }: PlayerAvatarProps) {
  const initials = getInitials(name);

  if (imageUrl) {
    return (
      <img
        src={imageUrl}
        alt={name}
        width={size}
        height={size}
        style={{
          borderRadius: '50%',
          objectFit: 'cover',
          flexShrink: 0,
          border: '2px solid #e4ece8',
          background: '#f4f6f5',
        }}
        onError={(e) => {
          const target = e.currentTarget;
          target.style.display = 'none';
          const sibling = target.nextElementSibling as HTMLElement | null;
          if (sibling) sibling.style.display = 'flex';
        }}
      />
    );
  }

  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: '50%',
        background: '#e8f7f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: size * 0.35,
        fontWeight: 700,
        color: '#15803d',
        flexShrink: 0,
        border: '2px solid #bbf7d0',
      }}
    >
      {initials}
    </div>
  );
}
