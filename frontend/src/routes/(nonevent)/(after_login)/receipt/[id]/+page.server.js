import { get } from '$lib/fetch';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, params, cookies }) {
    const data = await parent();

    const response = await get(`api/me/payment/${params.id}`, cookies);
    if (response.ok) {
        data.payment = response.data;
    } else {
        data.payment = null;
    }

    return data;
}
