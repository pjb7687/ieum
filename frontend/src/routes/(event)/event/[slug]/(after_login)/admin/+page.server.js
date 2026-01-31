import { get, post } from '$lib/fetch';
import { error } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ parent, params, cookies, request }) {
    let rtn = await parent();

    const get_data_or_404 = async (item) => {
        const response = await get(`api/${item}`, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            throw error(404, "Not Found");
        }
    }

    const get_data_or_404_event = async (item) => {
        return get_data_or_404(`event/${params.slug}/${item}`);
    }

    rtn.event = await get_data_or_404(`admin/event/${params.slug}`);

    // Superusers (staff) get access to full user list, event admins use attendees
    if (rtn.user?.is_staff) {
        rtn.users = await get_data_or_404('users');
    }

    rtn.attendees = await get_data_or_404_event('attendees');
    rtn.questions = await get_data_or_404_event('questions');
    rtn.speakers = await get_data_or_404_event('speakers');
    rtn.reviewers = await get_data_or_404_event('reviewers');
    rtn.abstracts = await get_data_or_404_event('abstracts');
    rtn.organizers = await get_data_or_404_event('organizers');
    rtn.eventadmins = await get_data_or_404_event('eventadmins');
    rtn.email_templates = await get_data_or_404_event('email_templates');
    rtn.onsite_attendees = await get_data_or_404_event('onsite');

    return rtn;
}

/** @type {import('./$types').Actions} */
export const actions = {
    toggle_published: async ({ cookies, params, request }) => {
        const response = await post(`api/event/${params.slug}/toggle_published`, {}, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    update_event: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/update`, formdata, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },  
    update_email_templates: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/emailtemplates`, {
            email_template_registration_subject: formdata.get('email_template_registration_subject'),
            email_template_registration_body: formdata.get('email_template_registration_body'),
            email_template_abstract_submission_subject: formdata.get('email_template_abstract_submission_subject'),
            email_template_abstract_submission_body: formdata.get('email_template_abstract_submission_body'),
            email_template_certificate_subject: formdata.get('email_template_certificate_subject'),
            email_template_certificate_body: formdata.get('email_template_certificate_body'),
        }, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    update_questions: async ({ cookies, params, request }) => {
        let formdata = await request.formData();

        // convert formdata to json
        let questions = [];
        for (let i = 0; i < formdata.getAll('question_id[]').length; i++) {
            let question = {
                type: formdata.getAll('question_type[]')[i],
                question: formdata.getAll('question_question[]')[i],
            };
            if (question.type === 'checkbox' || question.type === 'select') {
                question.options = formdata.getAll('question_options[]')[i].split('\n');
            }
            questions.push({
                id: parseInt(formdata.getAll('question_id[]')[i]),
                question: question,
            });
        }

        const response = await post(`api/event/${params.slug}/questions`, { questions }, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    add_speaker: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/speaker/add`, {
            name: formdata.get('name'),
            email: formdata.get('email'),
            affiliation: formdata.get('affiliation'),
            is_domestic: formdata.get('is_domestic') === 'true',
            type: formdata.get('type'),
        }, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    update_speaker: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/speaker/${formdata.get('id')}/update`, {
            name: formdata.get('name'),
            email: formdata.get('email'),
            affiliation: formdata.get('affiliation'),
            is_domestic: formdata.get('is_domestic') === 'true',
            type: formdata.get('type'),
        }, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    remove_speaker: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/speaker/${formdata.get('id')}/delete`, {
            id: parseInt(formdata.get('id'))
        }, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    update_attendee: async ({ cookies, params, request }) => {
        let formdata = await request.formData();

        const response = await post(`api/event/${params.slug}/attendee/${parseInt(formdata.get('id'))}/update`, { 
            first_name: formdata.get('first_name'),
            middle_initial: formdata.get('middle_initial'),
            last_name: formdata.get('last_name'),
            nationality: formdata.get('nationality'),
            institute: formdata.get('institute'),
            department: formdata.get('department'),
            job_title: formdata.get('job_title'),
            disability: formdata.get('disability'),
            dietary: formdata.get('dietary'),
        }, cookies);

        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    update_answers: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        let answers = [];
        for (let i = 0; i < formdata.getAll('answer_reference_id[]').length; i++) {
            answers.push({
                reference_id: parseInt(formdata.getAll('answer_reference_id[]')[i]),
                question: formdata.getAll('answer_question[]')[i],
                answer: formdata.getAll('answer_answer[]')[i],
            });
        }
        const response = await post(`api/event/${params.slug}/attendee/${formdata.get('attendee_id')}/answers`, {
            answers: answers,
        }, cookies);

        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    deregister_attendee: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/attendee/${formdata.get('id')}/deregister`, {}, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    send_emails: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/send_emails`, {
            to: formdata.get('to'),
            subject: formdata.get('subject'),
            body: formdata.get('body'),
        }, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    add_reviewer: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/reviewer/add`, {
            id: parseInt(formdata.get('id')),
        }, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    delete_reviewer: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/reviewer/${formdata.get('id')}/delete`, {}, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    get_abstract: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await get(`api/event/${params.slug}/abstract/${formdata.get('id')}`, cookies);
        if (response.ok && response.status === 200) {
            return JSON.stringify(response.data);
        } else {
            error(response.status, response.data);
        }
        return;
    },
    update_abstract: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/abstract/${formdata.get('id')}/update`, {
            title: formdata.get('title'),
            is_oral: formdata.get('type') === 'oral',
            is_accepted: formdata.get('is_accepted') === 'true',
        }, cookies);
        if (response.ok && response.status === 200) {
            return JSON.stringify(response.data);
        } else {
            error(response.status, response.data);
        }
        return;
    },
    delete_abstract: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/abstract/${formdata.get('id')}/delete`, {}, cookies);
        if (response.ok && response.status === 200) {
            return JSON.stringify(response.data);
        } else {
            error(response.status, response.data);
        }
        return;
    },
    add_eventadmin: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/eventadmin/add`, {
            id: parseInt(formdata.get('id')),
        }, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    delete_eventadmin: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/eventadmin/${formdata.get('id')}/delete`, {}, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    add_organizer: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/organizer/add`, {
            id: parseInt(formdata.get('id')),
        }, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    delete_organizer: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/organizer/${formdata.get('id')}/delete`, {}, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    update_onsite_attendee: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/onsite/${formdata.get('id')}/update`, {
            name: formdata.get('name'),
            email: formdata.get('email'),
            institute: formdata.get('institute'),
            job_title: formdata.get('job_title'),
        }, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    remove_onsite_attendee: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/onsite/${formdata.get('id')}/delete`, {}, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    },
    send_certificate: async ({ cookies, params, request }) => {
        let formdata = await request.formData();
        const response = await post(`api/event/${params.slug}/send_certificate`, {
            email: formdata.get('email'),
            pdf_base64: formdata.get('pdf_base64'),
            attendee_name: formdata.get('attendee_name'),
        }, cookies);
        if (response.ok && response.status === 200) {
            return response.data;
        } else {
            error(response.status, response.data);
        }
        return;
    }
};