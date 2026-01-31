import { post } from '$lib/fetch';
import { redirect } from '@sveltejs/kit';
import { sanitizeRedirectUrl } from '$lib/utils.js';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, request, cookies }) {
    const url = new URL(request.url);
    const next = sanitizeRedirectUrl(url.searchParams.get('next'));

    const data = await parent();
    if (!data.user) {
        return redirect(303, next);
    }

    // Call backend logout endpoint
    try {
        await post('/_allauth/browser/v1/auth/session', {}, cookies);
    } catch (error) {
        console.error('Logout error:', error);
    }

    // Delete the session cookie
    cookies.delete('sessionid', {
        path: '/',
        httpOnly: true,
        sameSite: 'lax',
        secure: process.env.NODE_ENV === 'production'
    });

    return redirect(303, next);
}