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

        // Check if user has submitted an abstract (only for internal abstract management)
        if (rtn.event.accepts_abstract && rtn.event.abstract_submission_type !== 'external') {
            const response_abstract = await get(`api/event/${params.slug}/abstract`, cookies);
            if (response_abstract.ok && response_abstract.status === 200) {
                rtn.abstract_submitted = true;
            } else {
                rtn.abstract_submitted = false;
            }
        } else {
            rtn.abstract_submitted = false;
        }
    }

    return rtn;
}