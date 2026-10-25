'use client';

import { Variants, Transition } from 'framer-motion';

/**
 * CoachPath Unified Motion Tokens & Animation Presets.
 * Designed for purposeful, micro-interactive feedback with strict accessibility.
 * Automatically respects user's prefers-reduced-motion preferences.
 */

export const transitions: Record<string, Transition> = {
  fast: { duration: 0.15, ease: [0.25, 0.1, 0.25, 1.0] },
  standard: { duration: 0.25, ease: [0.25, 0.1, 0.25, 1.0] },
  smooth: { duration: 0.35, ease: [0.16, 1, 0.3, 1] },
  springy: { type: 'spring', stiffness: 380, damping: 28 },
  staggerFast: { staggerChildren: 0.05, delayChildren: 0.05 },
  staggerStandard: { staggerChildren: 0.08, delayChildren: 0.1 },
};

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: transitions.standard,
  },
};

export const slideUp: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitions.smooth,
  },
};

export const slideDown: Variants = {
  hidden: { opacity: 0, y: -12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitions.smooth,
  },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.96 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: transitions.smooth,
  },
};

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: transitions.staggerStandard,
  },
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitions.smooth,
  },
};

export const cardHoverProps = {
  whileHover: { y: -2, transition: { duration: 0.2 } },
  whileTap: { scale: 0.99 },
};

export const buttonTapProps = {
  whileHover: { scale: 1.01 },
  whileTap: { scale: 0.98 },
};
