import { get } from '$lib/fetch';
import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, params, cookies }) {
    const data = await parent();

    // Redirect to login if not authenticated
    if (!data.user) {
        throw redirect(302, `/login?redirect=/receipt/${params.id}`);
    }

    const response = await get(`api/me/payment/${params.id}`, cookies);
    if (response.ok) {
        data.payment = response.data;
    } else {
        data.payment = null;
    }

    return data;
}
