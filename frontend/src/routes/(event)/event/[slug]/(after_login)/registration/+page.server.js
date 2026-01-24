import { get } from '$lib/fetch';
import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, params, cookies }) {
    let rtn = await parent();

    // If user is not registered, redirect to event detail page
    if (!rtn.registered) {
        throw redirect(303, `/event/${params.slug}`);
    }

    // Fetch attendee details
    const response_attendees = await get(`api/event/${params.slug}/attendees`, cookies);
    if (response_attendees.ok && response_attendees.status === 200) {
        const attendees = response_attendees.data;
        // Find the current user's attendee record
        const myAttendee = attendees.find(a => a.user.id === rtn.user.id);
        if (myAttendee) {
            rtn.attendee = myAttendee;
        }
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
