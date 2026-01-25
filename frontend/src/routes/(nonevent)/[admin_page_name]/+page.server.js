import { get, post } from '$lib/fetch';
import { error, redirect } from '@sveltejs/kit';

const ADMIN_PAGE_NAME = process.env.ADMIN_PAGE_NAME || '/admin';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, params, cookies }) {
    let data = await parent();
    let admin_page_name = params.admin_page_name;
    if (admin_page_name !== ADMIN_PAGE_NAME) {
        throw error(404, 'Not Found');
    }
    
    const get_data_or_404 = async (item) => {
        const response = await get(`api/admin/${item}`, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            throw error(404, "Not Found");
        }
    };

    data.admin = {
        events: await get_data_or_404('events'),
        users: await get_data_or_404('users')
    };

    return data;
}

/** @type {import('./$types').PageServerActions} */
export const actions = {
    'create_event': async ({ cookies, request }) => {
        let formdata = await request.formData();
        const response = await post('api/admin/event/add', formdata, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            throw error(response.status, response.data);
        }
    },
    'delete_event': async ({ cookies, request }) => {
        let formdata = await request.formData();
        let id = formdata.get('id');
        const response = await post(`api/admin/event/${id}/delete`, {}, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            throw error(response.status, response.data);
        }
    },
    'toggle_user_active': async ({ cookies, request }) => {
        let formdata = await request.formData();
        let user_id = formdata.get('user_id');
        const response = await post(`api/admin/user/${user_id}/toggle-active`, {}, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            throw error(response.status, response.data);
        }
    },
    'toggle_user_verified': async ({ cookies, request }) => {
        let formdata = await request.formData();
        let user_id = formdata.get('user_id');
        const response = await post(`api/admin/user/${user_id}/toggle-verified`, {}, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            throw error(response.status, response.data);
        }
    }
};