import { get } from '$lib/fetch';
import { json } from '@sveltejs/kit';

/** @type {import('./$types').RequestHandler} */
export async function GET({ url, cookies }) {
    // Forward all query parameters to the backend
    const params = url.searchParams;

    const response = await get(`api/events?${params.toString()}`, cookies);

    if (response.ok && response.status === 200) {
        return json(response.data);
    }

    return json({ events: [], total: 0, offset: 0, limit: 20 }, { status: response.status || 500 });
}
