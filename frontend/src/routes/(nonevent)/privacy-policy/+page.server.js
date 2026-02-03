import { get } from '$lib/fetch';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies }) {
    const response = await get('api/privacy-policy', cookies);

    if (response.ok && response.status === 200) {
        return {
            privacyPolicy: response.data
        };
    }

    return {
        privacyPolicy: {
            content_en: '',
            content_ko: '',
            updated_at: ''
        }
    };
}
