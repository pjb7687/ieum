import { get } from '$lib/fetch';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies }) {
    const response = await get('api/terms-of-service', cookies);

    if (response.ok && response.status === 200) {
        return {
            termsOfService: response.data
        };
    }

    return {
        termsOfService: {
            content_en: '',
            content_ko: '',
            updated_at: ''
        }
    };
}
