import { get } from '$lib/fetch';
import { error } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, params, cookies }) {
    let rtn = await parent();

    // Fetch speakers if available
    try {
        const response_speakers = await get(`api/event/${params.slug}/speakers`, cookies);
        if (response_speakers.ok && response_speakers.status === 200) {
            rtn.speakers = response_speakers.data;
        }
    } catch (e) {
        // Speakers are optional, so we don't fail if this errors
        rtn.speakers = [];
    }

    // Check if user is an event admin
    // Default to false for all users (including non-logged-in users)
    rtn.is_event_admin = false;

    if (rtn.user) {
        // Check if user is staff (superuser)
        if (rtn.user.is_staff) {
            rtn.is_event_admin = true;
        } else {
            // Check if user is an admin for this specific event
            try {
                const response_admin = await get(`api/admin/event/${params.slug}`, cookies);
                if (response_admin.ok && response_admin.status === 200) {
                    rtn.is_event_admin = true;
                }
            } catch (e) {
                // User is not an event admin
                rtn.is_event_admin = false;
            }
        }
    }

    return rtn;
}
