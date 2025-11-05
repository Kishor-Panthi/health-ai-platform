import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Get user from cookie (stored by zustand persist)
  const userStorage = request.cookies.get("user-storage");
  const hasUser = userStorage?.value && userStorage.value !== "null";

  // Protected routes that require authentication
  const isProtectedRoute = pathname.startsWith("/dashboard");

  // Auth routes that should redirect to dashboard if already logged in
  const isAuthRoute = ["/login", "/register", "/forgot-password"].includes(pathname);

  // Redirect to login if accessing protected route without auth
  if (isProtectedRoute && !hasUser) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect to dashboard if accessing auth routes while logged in
  if (isAuthRoute && hasUser) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
