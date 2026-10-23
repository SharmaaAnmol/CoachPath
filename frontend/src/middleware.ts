import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * CoachPath Edge Authentication Middleware.
 * Protects authenticated application routes from unauthenticated access.
 * Redirects authenticated users away from public auth pages (/login, /signup).
 */

const PROTECTED_PREFIXES = [
  '/dashboard',
  '/onboarding',
  '/career-profile',
  '/profile',
  '/skills',
  '/assessments',
  '/roadmap',
  '/jobs',
  '/resume',
  '/applications',
  '/recruiters',
  '/interviews',
  '/career-readiness',
  '/readiness',
  '/settings',
];

const AUTH_PAGES = ['/login', '/signup'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const accessToken = request.cookies.get('access_token')?.value;
  const refreshToken = request.cookies.get('refresh_token')?.value;
  const hasAuthSession = Boolean(accessToken || refreshToken);

  const isProtected = PROTECTED_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
  );
  const isAuthPage = AUTH_PAGES.some(
    (page) => pathname === page || pathname.startsWith(`${page}/`)
  );

  // 1. Unauthenticated user accessing protected route without session -> redirect to /login
  if (isProtected && !hasAuthSession) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Note: We intentionally do NOT force edge-redirecting /login or /signup to /dashboard here.
  // When an auth token expires or becomes invalid, client-side AuthProvider handles verification.
  // Edge-redirecting based purely on cookie presence causes an infinite redirect loop with AppLayout.
  // /login and /signup pages perform safe client-side redirection once useAuth() confirms a valid session.

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - images, svg, icons
     */
    '/((?!_next/static|_next/image|favicon.ico|images|icons|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
