import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies }) {
    // Always redirect to events list
    return redirect(301, '/events');
}