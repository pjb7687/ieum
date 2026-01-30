import { error, redirect } from '@sveltejs/kit';
import { post } from '$lib/fetch';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, params }) {
    const data = await parent();
    data.key = params.slug;
    return data;
}

/** @type {import('./$types').Actions} */
export const actions = {
    verify: async ({ request, cookies }) => {
        let formdata = await request.formData()
        const response = await post('_allauth/browser/v1/auth/email/verify', formdata, cookies);
        // 200: Email verified, 400: Input error, 401: Success but login required, 409: Already verified
        if (response.status === 200 || response.status === 401) {
            // Redirect to login page after successful verification
            throw redirect(303, '/login');
        } else if (response.status === 400) {
            throw error(response.status, 'Oops! It seems to be an invalid or expired verification link.');
        } else if (response.status === 409) {
            throw error(response.status, 'Oops! This email address was already verified.');
        } else {
            throw error(response.status, 'Server error. If this persists, please contact the administrator.');
        }
    }
};