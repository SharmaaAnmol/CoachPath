import * as React from 'react';
import { cn } from '@/lib/utils';

const tones = {
  violet: 'bg-lav-deep',
  lavender: 'bg-[#A78BFA]',
  lime: 'bg-[#84CC16] !opacity-[0.18]',
  crimson: 'bg-[#BE123C] !opacity-[0.22]',
} as const;

export interface LightFieldProps {
  tone?: keyof typeof tones;
  className?: string;
  style?: React.CSSProperties;
}

/** A soft blurred light placed behind glass so the blur has something to bend. Decorative only. */
export function LightField({ tone = 'violet', className, style }: LightFieldProps) {
  return <span aria-hidden className={cn('light-field', tones[tone], className)} style={style} />;
}
