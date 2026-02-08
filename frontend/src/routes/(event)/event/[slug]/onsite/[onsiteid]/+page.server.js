import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, params }) {
    const data = await parent();
    const event = data.event;

    const today = new Date().toISOString().split('T')[0];
    if (today < event.start_date || today > event.end_date) {
        throw redirect(303, `/event/${params.slug}`);
    }

    return {
        onsiteid: params.onsiteid
    };
}
