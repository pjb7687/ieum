import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').LayoutServerLoad} */
export async function load({ parent, request }) {
    let data = await parent();
    if (!data.user) {
        const url = new URL(request.url);
        redirect(303, `/login?next=${encodeURIComponent(url.pathname)}`);
    }
    return data;
}
