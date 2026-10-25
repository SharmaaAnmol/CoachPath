'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface NumberTickerProps extends React.HTMLAttributes<HTMLSpanElement> {
  value: number;
  direction?: 'up' | 'down';
  delay?: number; // in seconds
  duration?: number; // in milliseconds
  decimalPlaces?: number;
  suffix?: string;
  prefix?: string;
}

export function NumberTicker({
  value,
  direction = 'up',
  delay = 0,
  duration = 1000,
  decimalPlaces = 0,
  prefix = '',
  suffix = '',
  className,
  ...props
}: NumberTickerProps) {
  const [displayValue, setDisplayValue] = React.useState<number>(
    direction === 'down' ? value : 0
  );
  const startTimeRef = React.useRef<number | null>(null);
  const frameRef = React.useRef<number | null>(null);

  React.useEffect(() => {
    // Check for reduced motion
    const prefersReducedMotion =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
      setDisplayValue(value);
      return;
    }

    const startVal = direction === 'down' ? value : 0;
    const targetVal = value;
    const timeoutId = setTimeout(() => {
      const step = (timestamp: number) => {
        if (!startTimeRef.current) startTimeRef.current = timestamp;
        const elapsed = timestamp - startTimeRef.current;
        const progress = Math.min(elapsed / duration, 1);
        
        // Ease out quad
        const easedProgress = 1 - (1 - progress) * (1 - progress);
        const current = startVal + (targetVal - startVal) * easedProgress;
        setDisplayValue(current);

        if (progress < 1) {
          frameRef.current = requestAnimationFrame(step);
        } else {
          setDisplayValue(targetVal);
        }
      };
      frameRef.current = requestAnimationFrame(step);
    }, delay * 1000);

    return () => {
      clearTimeout(timeoutId);
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
      startTimeRef.current = null;
    };
  }, [value, direction, delay, duration]);

  const formatted =
    prefix +
    displayValue.toLocaleString('en-US', {
      minimumFractionDigits: decimalPlaces,
      maximumFractionDigits: decimalPlaces,
    }) +
    suffix;

  return (
    <span
      className={cn('inline-block tabular-nums tracking-tight', className)}
      {...props}
    >
      {formatted}
    </span>
  );
}
