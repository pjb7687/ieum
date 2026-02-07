import { get } from '$lib/fetch';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, cookies }) {
    const data = await parent();

    const response = await get('api/me/registration-history', cookies);
    if (response.ok) {
        data.registrations = response.data;
    } else {
        data.registrations = [];
    }

    return data;
}
