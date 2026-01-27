import { get, post } from '$lib/fetch';
import { error, redirect } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, params, cookies }) {
    let rtn = await parent();
    if (rtn.user) {
        if (rtn.registered) {
            return redirect(303, `/event/${params.slug}`);
        }
        const response_questions = await get(`api/event/${params.slug}/questions`, cookies); // list of custom questions
        if (response_questions.ok && response_questions.status === 200) {
            rtn.questions = response_questions.data;
        } else {
            error(500, "Internal Server Error");
        }
    } else {
        return redirect(303, `/login?next=${encodeURIComponent(`/event/${params.slug}/register`)}`);
    }

    // Load all institutions for the lookup component
    const institutionsResponse = await get('api/institutions', cookies);
    if (institutionsResponse.ok) {
        rtn.institutions = institutionsResponse.data;
    } else {
        rtn.institutions = [];
    }

    return rtn;
}

/** @type {import('./$types').Actions} */
export const actions = {
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
    },
    register: async ({ cookies, params, request }) => {
        let formdata = await request.formData()
        const response = await post(`api/event/${params.slug}/register`, formdata, cookies);

        if (!response.ok || response.status !== 200) {
            if (response.status === 400) {
                throw error(response.status, { error: true, message: response.data.message });
            }
            throw error(response.status, { error: true, message: 'Failed due to server error. It this persists, please contact the admininistrator.' });
        }
        return;
    },
};