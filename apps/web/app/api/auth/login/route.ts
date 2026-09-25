import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  let email = '';
  let password = '';
  try {
    const body = await request.json();
    email = body.email;
    password = body.password;

    // In a real app, this would call the backend API
    // For demo mode, we accept any email/password
    if (process.env.NEXT_PUBLIC_DEMO_MODE === 'true') {
      const token = 'demo-jwt-token-' + Date.now();
      
      const response = NextResponse.json({
        access_token: token,
        token_type: 'bearer',
        user: {
          id: 'demo-user-id',
          email,
          full_name: 'Demo User',
          role: 'admin',
          is_active: true,
        }
      });

      // Set cookie
      response.cookies.set('auth_token', token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24, // 24 hours
        path: '/',
      });

      return response;
    }

    // Real backend call
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username: email,
        password,
      }),
    });

    if (!response.ok) {
      return NextResponse.json(
        { detail: 'Invalid credentials' },
        { status: 401 }
      );
    }

    const data = await response.json();
    
    const nextResponse = NextResponse.json(data);
    
    // Set cookie
    nextResponse.cookies.set('auth_token', data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24, // 24 hours
      path: '/',
    });

    return nextResponse;
  } catch (error) {
    console.error('Login error:', error);
    // If backend is unreachable but demo credentials were provided, allow login
    if (email === 'admin@ecdat.demo' && password === 'demo123') {
      const token = 'demo-jwt-fallback-' + Date.now();
      const fallbackResponse = NextResponse.json({
        access_token: token,
        token_type: 'bearer',
        user: {
          id: 'demo-admin-id',
          email,
          full_name: 'Security Administrator',
          role: 'ADMIN',
          is_active: true,
        },
      });
      fallbackResponse.cookies.set('auth_token', token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24,
        path: '/',
      });
      return fallbackResponse;
    }
    return NextResponse.json(
      { detail: 'Authentication service temporarily unavailable' },
      { status: 503 }
    );
  }
}