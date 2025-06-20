import { get, post } from '$lib/fetch';
import { error, fail, redirect } from '@sveltejs/kit';

/** @type {import('./$types').Actions} */
export const actions = {
    onsiteregister: async ({ cookies, params, request }) => {
        let formdata = await request.formData()
        const response = await post(`api/event/${params.slug}/onsite`, formdata, cookies);

        if (!response.ok || response.status !== 200) {
            if (response.status === 400) {
                throw error(response.status, { error: true, message: response.data.message });
            }
            throw error(response.status, { error: true, message: 'Failed due to server error. It this persists, please contact the admininistrator.' });
        }
        let rtn = await response.data;
        return redirect(303, `/event/${params.slug}/onsite/${rtn.id}`);
    },
};