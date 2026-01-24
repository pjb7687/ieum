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

    return rtn;
}
