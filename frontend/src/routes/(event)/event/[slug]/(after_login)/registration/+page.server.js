import { get } from '$lib/fetch';
import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, params, cookies }) {
    let rtn = await parent();

    // If user is not registered, redirect to event detail page
    if (!rtn.registered) {
        throw redirect(303, `/event/${params.slug}`);
    }

    // Fetch current user's registration
    const response_attendee = await get(`api/event/${params.slug}/registration`, cookies);
    if (response_attendee.ok && response_attendee.status === 200) {
        rtn.attendee = response_attendee.data;
    }

    // Fetch abstract if user has submitted one
    if (rtn.event.accepts_abstract) {
        try {
            const response_abstract = await get(`api/event/${params.slug}/abstract`, cookies);
            if (response_abstract.ok && response_abstract.status === 200) {
                rtn.my_abstract = response_abstract.data;
            }
        } catch (e) {
            // Abstract might not exist, which is fine
            rtn.my_abstract = null;
        }
    }

    return rtn;
}
