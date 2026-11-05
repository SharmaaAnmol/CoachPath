import * as React from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'intelligence';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading = false, children, disabled, ...props }, ref) => {
    const baseStyles =
      'inline-flex items-center justify-center font-medium rounded-xl dark:rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-lav dark:focus:ring-offset-black disabled:opacity-50 disabled:pointer-events-none active:scale-[0.98] select-none';

    const variants = {
      primary: 'bg-brand-600 text-white hover:bg-brand-700 hover:shadow-glow focus:ring-brand-500 shadow-sm dark:bg-lav dark:text-lav-ink dark:hover:bg-lav-light dark:hover:shadow-none',
      intelligence:
        'bg-intelligence-600 text-white hover:bg-intelligence-700 hover:shadow-glow-purple focus:ring-intelligence-500 shadow-sm dark:bg-lav-violet dark:hover:bg-lav-deep dark:hover:shadow-none',
      secondary: 'bg-slate-100 text-slate-800 hover:bg-slate-200 focus:ring-slate-400 dark:bg-white/[0.07] dark:text-ink-fg dark:hover:bg-white/10',
      outline:
        'border border-slate-300/80 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-400 focus:ring-slate-400 dark:border-white/15 dark:bg-white/[0.04] dark:text-ink-fg dark:hover:bg-white/[0.07]',
      ghost: 'bg-transparent text-slate-600 hover:bg-slate-100 focus:ring-slate-400 dark:text-ink-fg/80 dark:hover:bg-white/[0.07]',
      destructive: 'bg-gap-600 text-white hover:bg-gap-700 focus:ring-gap-500 shadow-sm dark:bg-crimson dark:hover:bg-crimson/85',
    };

    const sizes = {
      sm: 'text-xs px-2.5 py-1.5 h-8 gap-1.5',
      md: 'text-sm px-4 py-2 h-10 gap-2',
      lg: 'text-base px-6 py-2.5 h-12 gap-2.5',
      icon: 'h-9 w-9 p-0 flex items-center justify-center',
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {isLoading && <Loader2 className="w-4 h-4 animate-spin shrink-0" />}
        {children}
      </button>
    );
  }
);
Button.displayName = 'Button';
