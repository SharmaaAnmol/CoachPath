# CoachPath — Premium Frontend Redesign Architecture & Implementation Plan

## 1. Executive Summary

This document specifies the technical design system, animation architecture, component primitives, and backend integration strategy implemented in the CoachPath premium frontend redesign (branch: `ui-redesign`).

CoachPath is an AI-powered career intelligence platform linking diagnostic skill assessments, personalized roadmaps, truthful resume diffing, and explainable job matching into one connected career graph.

---

## 2. Visual Direction & Design Tokens

### 2.1 Color Palette
- **Surfaces & Backgrounds**:
  - Light mode: Clean off-white and cool slate (`#F8FAFC`, `#FFFFFF`, `#F1F5F9`).
  - Dark mode: Deep navy/charcoal (`#0B0F19`, `#0F172A`, `#111827`, `#1E293B`).
  - Glass panels: `rgba(255, 255, 255, 0.85)` / `rgba(15, 23, 42, 0.85)` with `backdrop-filter: blur(12px)`.
- **Primary Brand**:
  - Indigo/Cobalt spectrum (`#6366F1`, `#4F46E5`, `#4338CA`) representing clarity, direction, and executive poise.
- **Intelligence & AI Accent**:
  - Violet/Purple spectrum (`#8B5CF6`, `#7C3AED`, `#6D28D9`) for AI features (Onboarding interview, Career Readiness, AI diffing).
- **Domain Status Semantics**:
  - Verified Strengths: Emerald green (`#10B981`, `#059669`) for calibrated skills and passed assessments.
  - Active Milestones: Amber (`#F59E0B`, `#D97706`) for roadmap tasks in progress.
  - Skill Gaps & Alerts: Rose (`#F43F5E`, `#E11D48`) for critical market gaps and auth errors.

### 2.2 Typography
- Primary Sans: `Inter`, system-ui, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`.
- Monospace: `JetBrains Mono`, `Fira Code` for code identifiers, target roles, and metrics.
- High-contrast hierarchy:
  - Page Titles: `text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight`
  - Section Headings: `text-xl font-bold tracking-tight`
  - Stat Numbers: `text-2xl sm:text-3xl font-extrabold tabular-nums tracking-tight`
  - Micro-labels: `text-[10px] sm:text-xs font-semibold uppercase tracking-wider`

### 2.3 Depth, Elevation & Corner Radii
- Standard cards: `rounded-2xl border border-slate-200/80 dark:border-slate-800/80 shadow-card`
- Elevated hover: `hover:border-slate-300 dark:hover:border-slate-700 hover:shadow-elevated hover:-translate-y-0.5`
- Ambient glows:
  - `shadow-glow`: `0 0 25px -5px rgba(99, 102, 241, 0.25)`
  - `shadow-glow-purple`: `0 0 25px -5px rgba(139, 92, 246, 0.25)`
  - `shadow-glow-emerald`: `0 0 25px -5px rgba(16, 185, 129, 0.2)`

---

## 3. Motion & Animation Tokens (`src/lib/motion.ts`)

Powered by `framer-motion` (v12.35.0):
- **Transitions**:
  - `fast`: `0.15s` ease-out for hover, tap, and toggle.
  - `standard`: `0.25s` ease-out for popovers and dialogs.
  - `smooth`: `0.35s` `[0.16, 1, 0.3, 1]` cubic bezier for card entrances.
  - `staggerStandard`: `0.08s` delay between child items.
- **Presets**:
  - `fadeIn`: Simple opacity reveal.
  - `slideUp`: Smooth 12px Y-translation with opacity.
  - `scaleIn`: Scale from 0.96 with opacity.
  - `staggerContainer` & `staggerItem`: Orchestrated grid loading.
- **Accessibility (`prefers-reduced-motion`)**:
  - Global CSS rule in `globals.css` sets `animation-duration: 0.01ms` and `transition-duration: 0.01ms` when reduced motion is preferred.
  - `NumberTicker` directly checks `window.matchMedia('(prefers-reduced-motion: reduce)')` to render instant numbers without counting animation.

---

## 4. Component Inventory & Architecture

### 4.1 UI Primitives (`src/components/ui/`)
- `bento-grid.tsx` *(New)*:
  - `BentoGrid`: Responsive 3-column container (`grid-cols-1 md:grid-cols-3 gap-5`).
  - `BentoCard`: Support for `colSpan={1|2|3}`, `rowSpan={1|2}`, gradient backgrounds, and subtle border hover illumination.
- `number-ticker.tsx` *(New)*:
  - Smooth requestAnimationFrame-driven numerical counter with quadratic ease-out.
  - Supports prefix, suffix, and configurable duration.
- `card.tsx`:
  - Upgraded to `rounded-2xl` with optional `hoverable` and `glass` props.
- `button.tsx`:
  - Upgraded with `rounded-xl`, subtle shadow-glow on primary/intelligence variants, and active scale feedback.
- `badge.tsx`:
  - Added `brand` variant alongside `verified`, `intelligence`, `action`, and `gap`.
- `stat-card.tsx`:
  - Upgraded to use `Card hoverable` with responsive typography.

### 4.2 Application Shell (`src/components/layout/`)
- `sidebar.tsx`:
  - Eliminated mock data dependencies (`mockReadinessData`).
  - Dark glass navigation bar (`bg-slate-950/95`).
  - Active indicator pill with subtle gradient and glow.
  - Desktop collapse/expand toggle.
  - Mobile drawer with backdrop blur.
- `topbar.tsx`:
  - Eliminated hardcoded mock readiness scores.
  - Dynamically fetches candidate target role from `profileClient.getMasterProfile()`.
  - Responsive breadcrumbs, notification popover, user menu with smooth logout flow.
- `app-shell.tsx`:
  - Fluid `<motion.main>` entrance animations on page transitions.

### 4.3 Dashboard (`src/app/(app)/dashboard/page.tsx`)
- Zero-mock architecture:
  - Connects to `profileClient.getMasterProfile()`, `onboardingClient.getSession()`, `roadmapClient.getActiveRoadmap()`, `jobMatchingClient.getRecommendations()`, `assessmentClient.listAssessments()`, and `skillGapClient.getLatestAnalysis()`.
- Bento Grid layout:
  - Hero Hub banner with dynamic target role badge and readiness ticker.
  - Onboarding prompt alert for in-progress or review states.
  - 4 Metric Stat Cards (Readiness, Verified Skills, Roadmap Sprint, Job Matches).
  - Active Roadmap Milestone card with deliverable link + zero-mock empty state.
  - Diagnostic Skill Assessments card with progress bar + test launcher.
  - Semantic Job Matches card with company, location, and fit score + zero-mock empty state.
  - Profile Evidence card with checklist and link to resume optimizer.

### 4.4 Public Pages & Auth
- `(public)/page.tsx`:
  - Hero section with ambient glows and subtle background grid.
  - Bento Grid showcasing CoachPath's 6 Core Pillars.
  - Interactive Preview tabs component (`InteractivePlatformPreview`).
  - 10-step connected career journey.
  - 3 persona cards (Student, Recent Grad, Early Pro).
  - Responsible AI and Anti-Hallucination guarantees.
  - Zero fabricated social proof.
- `(public)/login/page.tsx` & `(public)/signup/page.tsx`:
  - Ambient glow background and smooth `<motion.div>` card entrance.
  - Live interactive password requirements checklist.
  - Clear error alerts and demo autofill helper.

---

## 5. Verification & Quality Gates
- `npm run build`: Exit code 0, 25/25 static pages generated.
- `npm run lint`: Exit code 0, zero ESLint warnings or errors.
- TypeScript type checking: Passed with zero type errors.
