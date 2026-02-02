import { get } from '$lib/fetch';
import { error } from '@sveltejs/kit';

/** @type {import('./$types').LayoutServerLoad} */
export async function load({ parent, params, cookies }) {
    let rtn = await parent();

    const response_event = await get(`api/event/${params.slug}`, cookies);
    if (response_event.ok && response_event.status === 200) {
        let event = response_event.data;
        rtn.event = event;
    } else {
        throw error(response_event.status);
    }

    if (rtn.user) {
        const response_registered = await get(`api/event/${params.slug}/registered`, cookies); // true if registered, false if not
        if (response_registered.ok && response_registered.status === 200) {
            rtn.registered = response_registered.data.registered;
            rtn.payment_status = response_registered.data.payment_status;
        }
    }
    
    return rtn;
}