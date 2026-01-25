import { get } from '$lib/fetch';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, cookies, url }) {
    let rtn = await parent();

    // Load first 20 events
    const offset = parseInt(url.searchParams.get('offset') || '0');
    const limit = 20;
    const year = url.searchParams.get('year') || 'all';
    const search = url.searchParams.get('search') || '';
    const showOnlyOpen = url.searchParams.get('showOnlyOpen') === 'true';

    const queryParams = new URLSearchParams({
        offset: offset.toString(),
        limit: limit.toString(),
    });

    if (year !== 'all') queryParams.append('year', year);
    if (search) queryParams.append('search', search);
    if (showOnlyOpen) queryParams.append('showOnlyOpen', 'true');

    const response_events = await get(`api/events?${queryParams.toString()}`);
    if (response_events.ok && response_events.status === 200) {
        rtn.eventsData = response_events.data;
    } else {
        rtn.eventsData = { events: [], total: 0, offset: 0, limit: 20 };
    }

    return rtn;
}
