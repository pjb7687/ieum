import { get, post } from '$lib/fetch';
import { error } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, request, cookies }) {
    const data = await parent();
    const url = new URL(request.url);
    const next = url.searchParams.get('next') || '/';
    data.next = next;

    // Load all institutions for the lookup component
    const institutionsResponse = await get('api/institutions', cookies);
    if (institutionsResponse.ok) {
        data.institutions = institutionsResponse.data;
    } else {
        data.institutions = [];
    }

    return data;
}

/** @type {import('./$types').Actions} */
export const actions = {
    update: async ({ cookies, request }) => {
        let formdata = await request.formData()

        // Convert FormData to JSON object
        const data = {};
        for (const [key, value] of formdata.entries()) {
            data[key] = value;
        }

        const response = await post('api/me', data, cookies);

        if (!response.ok || response.status !== 200) {
            throw error(response.status, { message: 'Server error. If this persists, please contact the administrator.' });
        }
    },
    create_institution: async ({ cookies, request }) => {
        let formdata = await request.formData();
        const data = {
            name_en: formdata.get('name_en'),
            name_ko: formdata.get('name_ko') || ''
        };
        const response = await post('api/institutions', data, cookies);
        if (response.ok && response.status === 200) {
            return { success: true, institution: response.data };
        } else {
            throw error(response.status, response.data);
        }
    }
};