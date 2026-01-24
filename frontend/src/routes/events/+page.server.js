import { get } from '$lib/fetch';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, cookies }) {
    let rtn = await parent();

    // Events are already loaded in root layout
    return rtn;
}
