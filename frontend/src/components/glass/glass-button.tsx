import * as React from 'react';
import Link from 'next/link';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

type Variant = 'primary' | 'glass' | 'lime' | 'ghost';
type Size = 'sm' | 'md' | 'lg';

const base =
  'relative inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full font-medium select-none ' +
  'transition-[transform,background,box-shadow,color] duration-200 ease-out-expo ' +
  'hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.97] ' +
  'disabled:pointer-events-none disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lav focus-visible:ring-offset-2 focus-visible:ring-offset-black';

const variants: Record<Variant, string> = {
  primary: 'bg-gradient-to-b from-lav-light to-lav text-lav-ink shadow-lift hover:from-[#EEE8FF] hover:to-lav-light',
  glass: 'liquid-glass text-ink-fg',
  lime: 'bg-lime text-lime-ink shadow-lift hover:bg-lime-soft',
  ghost: 'text-ink-muted hover:text-ink-fg hover:bg-white/5',
};

const sizes: Record<Size, string> = {
  sm: 'h-9 px-4 text-[13px]',
  md: 'h-11 px-5 text-sm',
  lg: 'h-12 px-6 text-[15px]',
};

interface Common {
  variant?: Variant;
  size?: Size;
  className?: string;
  children?: React.ReactNode;
}

export type GlassButtonProps =
  | (Common & { href: string } & Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, 'href' | 'className' | 'children'>)
  | (Common & { href?: undefined; isLoading?: boolean } & Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'className' | 'children'>);

/** One button system for the redesign: lavender primary, glass secondary, lime for "continue", ghost for quiet actions. */
export function GlassButton(props: GlassButtonProps) {
  const { variant = 'primary', size = 'md', className, children } = props;
  const cls = cn(base, variants[variant], sizes[size], className);

  if (props.href !== undefined) {
    const { variant: _v, size: _s, className: _c, children: _ch, href, ...rest } = props;
    return (
      <Link href={href} className={cls} {...rest}>
        {children}
      </Link>
    );
  }

  const { variant: _v, size: _s, className: _c, children: _ch, isLoading, disabled, ...rest } = props;
  return (
    <button className={cls} disabled={disabled || isLoading} aria-busy={isLoading || undefined} {...rest}>
      {isLoading && <Loader2 className="h-4 w-4 shrink-0 animate-spin" aria-hidden />}
      {children}
    </button>
  );
}
