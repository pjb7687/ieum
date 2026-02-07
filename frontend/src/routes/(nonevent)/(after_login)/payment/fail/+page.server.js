/** @type {import('./$types').PageServerLoad} */
export async function load({ url }) {
    // Get error parameters from URL
    const code = url.searchParams.get('code');
    const message = url.searchParams.get('message');
    const orderId = url.searchParams.get('orderId');

    return {
        code,
        message: message ? decodeURIComponent(message) : null,
        orderId,
    };
}
