'use client';

import * as React from 'react';
import { RoadmapPhaseItem, RoadmapTaskItem } from '@/types';
import { RoadmapPhaseCard } from './RoadmapPhaseCard';

interface RoadmapPhaseListProps {
  phases: RoadmapPhaseItem[];
  onStatusChange: (taskId: string, status: 'pending' | 'in_progress' | 'completed' | 'skipped') => Promise<void>;
  onSubmitDeliverable: (task: RoadmapTaskItem) => void;
  focusedTaskId?: string | null;
}

export function RoadmapPhaseList({
  phases,
  onStatusChange,
  onSubmitDeliverable,
  focusedTaskId,
}: RoadmapPhaseListProps) {
  // Build a lookup map of all tasks for prerequisite dependency checking
  const allTaskMap = React.useMemo(() => {
    const map = new Map<string, RoadmapTaskItem>();
    for (const phase of phases) {
      for (const task of phase.tasks) {
        map.set(task.id, task);
      }
    }
    return map;
  }, [phases]);

  return (
    <div className="space-y-6">
      {phases.map((phase) => (
        <RoadmapPhaseCard
          key={phase.id}
          phase={phase}
          allTaskMap={allTaskMap}
          onStatusChange={onStatusChange}
          onSubmitDeliverable={onSubmitDeliverable}
          focusedTaskId={focusedTaskId}
        />
      ))}
    </div>
  );
}
