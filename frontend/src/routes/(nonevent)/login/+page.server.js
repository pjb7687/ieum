import { get, post } from '$lib/fetch';
import { error, fail, redirect } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, params, cookies, request }) {
    let rtn = await parent();
    if (rtn.user) {
        return redirect(303, '/');
    }

    const url = new URL(request.url);
    rtn.sociallogin_error = url.searchParams.get('error_process') || '';

    return rtn;
}

/** @type {import('./$types').Actions} */
export const actions = {
	login: async ({ cookies, request }) => {
        let formdata = await request.formData()
        const response = await post('_allauth/browser/v1/auth/login', formdata, cookies);

		if (!response.ok || response.status !== 200) {
            if (response.status === 401) {
                return fail(response.status, { error: true, message: 'Email not verified. Please check your mailbox.' });
            }
            return fail(response.status, { error: true, message: 'Login Failed. Check your credentials.' });
        }
        cookies.set('sessionid', response.sessionid, {
            path: '/',
            httpOnly: true,
            sameSite: 'lax',
            secure: process.env.NODE_ENV === 'production',
        });
        return;
	},
};
