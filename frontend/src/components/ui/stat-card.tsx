import * as React from 'react';
import { cn } from '@/lib/utils';
import { Card } from './card';

export interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  iconColor?: 'brand' | 'verified' | 'intelligence' | 'action' | 'gap';
  trend?: {
    value: string;
    isPositive?: boolean;
    label?: string;
  };
  className?: string;
}

export function StatCard({
  title,
  value,
  subtitle,
  icon,
  iconColor = 'brand',
  trend,
  className,
}: StatCardProps) {
  const iconBg = {
    brand: 'bg-indigo-50 text-indigo-600 dark:bg-indigo-950/50 dark:text-indigo-400',
    verified: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/50 dark:text-emerald-400',
    intelligence: 'bg-purple-50 text-purple-600 dark:bg-purple-950/50 dark:text-purple-400',
    action: 'bg-amber-50 text-amber-600 dark:bg-amber-950/50 dark:text-amber-400',
    gap: 'bg-rose-50 text-rose-600 dark:bg-rose-950/50 dark:text-rose-400',
  };

  return (
    <Card className={cn('p-5 flex flex-col justify-between hover:shadow-elevated transition-shadow', className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            {title}
          </p>
          <div className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            {value}
          </div>
        </div>
        {icon && (
          <div className={cn('p-3 rounded-xl flex items-center justify-center shrink-0', iconBg[iconColor])}>
            {icon}
          </div>
        )}
      </div>

      {(subtitle || trend) && (
        <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
          {trend && (
            <div className="flex items-center gap-1 font-semibold">
              <span className={trend.isPositive ? 'text-emerald-600' : 'text-rose-600'}>
                {trend.value}
              </span>
              {trend.label && <span className="text-slate-400 font-normal">{trend.label}</span>}
            </div>
          )}
          {subtitle && <span className="text-slate-500 dark:text-slate-400 truncate">{subtitle}</span>}
        </div>
      )}
    </Card>
  );
}
