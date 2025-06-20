/** @type {import('./$types').PageLoad} */
export function load({ params }) {
    return {
        onsiteid: params.onsiteid
    };
}