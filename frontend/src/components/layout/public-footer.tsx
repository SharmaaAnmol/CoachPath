import Link from 'next/link';
import { Shield, HeartHandshake, FileCheck } from 'lucide-react';

export function PublicFooter() {
  return (
    <footer className="bg-slate-900 text-slate-400 border-t border-slate-800 text-xs dark:bg-black dark:text-ink-muted dark:border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Info */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center gap-2">
              <span className="grid h-7 w-7 place-items-center rounded-lg bg-gradient-to-b from-lav-light to-lav text-[13px] font-bold text-lav-ink">C</span>
              <span className="font-bold text-white text-base">CoachPath</span>
            </div>
            <p className="text-slate-400 leading-relaxed text-xs">
              AI-powered career intelligence platform that connects self-reported skills, diagnostic assessments, personalized roadmaps, and truthful job matching.
            </p>
            <div className="flex items-center gap-2 text-emerald-400 font-medium text-[11px] pt-1 dark:text-lime-soft">
              <Shield className="w-3.5 h-3.5" />
              <span>Evidence-grounded safeguards &bull; Human-in-the-loop</span>
            </div>
          </div>

          {/* Product links */}
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider text-[11px] mb-3">Product</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/features" className="hover:text-white transition-colors">
                  Platform Features
                </Link>
              </li>
              <li>
                <Link href="/how-it-works" className="hover:text-white transition-colors">
                  10-Step Connected Journey
                </Link>
              </li>
              <li>
                <Link href="/assessments" className="hover:text-white transition-colors">
                  Diagnostic Assessments
                </Link>
              </li>
              <li>
                <Link href="/career-readiness" className="hover:text-white transition-colors">
                  Career Readiness Index (Preview)
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="hover:text-white transition-colors">
                  Interactive Sandbox
                </Link>
              </li>
            </ul>
          </div>

          {/* Candidate Personas */}
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider text-[11px] mb-3">Target Audiences</h4>
            <ul className="space-y-2">
              <li className="hover:text-white transition-colors">University Students</li>
              <li className="hover:text-white transition-colors">Recent Computer Science Grads</li>
              <li className="hover:text-white transition-colors">Early-Career Engineers (1-3 YOE)</li>
              <li className="hover:text-white transition-colors">Technical Career Switchers</li>
            </ul>
          </div>

          {/* Trust & Ethics */}
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider text-[11px] mb-3">Trust & Transparency</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/privacy" className="hover:text-white transition-colors flex items-center gap-1">
                  <FileCheck className="w-3.5 h-3.5 text-purple-400 dark:text-lav-light" /> Privacy & Responsible AI
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:text-white transition-colors flex items-center gap-1">
                  <HeartHandshake className="w-3.5 h-3.5 text-emerald-400 dark:text-lime-soft" /> Our Mission & Vision
                </Link>
              </li>
              <li className="text-slate-400">Designed for Privacy & Minimization</li>
              <li className="text-slate-400">User Data Ownership & Admin-Assisted Deletion</li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-400">
          <p>© {new Date().getFullYear()} CoachPath Inc. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <Link href="/privacy" className="hover:text-slate-300">
              Privacy Policy
            </Link>
            <Link href="/privacy" className="hover:text-slate-300">
              Terms of Service
            </Link>
            <Link href="/about" className="hover:text-slate-300">
              Contact
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
