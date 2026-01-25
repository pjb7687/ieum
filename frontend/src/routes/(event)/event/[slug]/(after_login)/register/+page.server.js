import { get, post } from '$lib/fetch';
import { error, fail, redirect } from '@sveltejs/kit';

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

    return rtn;
}

/** @type {import('./$types').Actions} */
export const actions = {
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