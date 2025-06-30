<script>
    import { enhance } from '$app/forms';
    import { goto } from '$app/navigation';
    
    import { A, Card, Button, Heading, Indicator, Label, Input, Checkbox, Select, Alert, Navbar, Textarea } from 'flowbite-svelte';
    import { onMount } from 'svelte';

    import { createForm } from 'felte';
    import { validator } from '@felte/validator-yup';
    import * as yup from 'yup';

    import RegistrationForm from '$lib/components/RegistrationForm.svelte';
    import 'academicons';

    let { data, form } = $props();

    let event = data.event;
    let deadline = event.registration_deadline ? new Date(event.registration_deadline) : new Date(event.start_date);
    let now = new Date();
    
    let form_config = { 
        hide_login_info: true,
    };
    
    const koreanRegex = /[\u3131-\u3163\uac00-\ud7a3]/;
    const rejectKorean = (value) => {
        if (!value) return true;
        return !koreanRegex.test(value);
    };

    const schema = yup.object({
        first_name: yup.string().required('First name is required.').test('no-korean', 'Korean characters are not allowed.', rejectKorean),
        last_name: yup.string().required('Last name is required.').test('no-korean', 'Korean characters are not allowed.', rejectKorean),
        middle_initial: yup.string().max(1).test('no-korean', 'Korean characters are not allowed.', rejectKorean),
        nationality: yup.number().required().test('no-korean', 'Korean characters are not allowed.', rejectKorean),
        job_title: yup.string().test('no-korean', 'Korean characters are not allowed.', rejectKorean),
        department: yup.string().test('no-korean', 'Korean characters are not allowed.', rejectKorean),
        institute: yup.string().required('Institute is required.').test('no-korean', 'Korean characters are not allowed.', rejectKorean),
        disability: yup.string().test('no-korean', 'Korean characters are not allowed.', rejectKorean),
        dietary: yup.string().test('no-korean', 'Korean characters are not allowed.', rejectKorean),
    });

    let me = data.user;
    let error_message = $state('');
    const { form: felteForm, data: formData, errors, isSubmitting } = createForm({
        initialValues: {
            first_name: me?me.first_name:'',
            middle_initial: me?me.middle_initial:'',
            last_name: me?me.last_name:'',
            nationality: me?me.nationality:1,
            institute: me?me.institute:'',
            department: me?me.department:'',
            job_title: me?me.job_title:'',
            disability: me?me.disability:'',
            dietary: me?me.dietary:'',
        },
        onSubmit: async (data) => {
            const response = await fetch('?/register',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'application/json',
                    },
                    body: new URLSearchParams(data),
                }
            );
            if (!response.ok || response.status !== 200) {
                const rtn = await response.json();
                throw rtn.error;
            }
            goto(`/event/${event.id}`);
        },
        extend: validator({ schema }),
        onError: (errors) => {
            // scroll to top
            error_message = errors.message;
            return errors;
        }
    });
</script>

{#snippet process_spaces(text)}
    {@html text.replace(/\n/g, '<br>').replace(/ /g, '&nbsp;')}
{/snippet}

<Heading tag="h1" customSize="text-2xl font-bold" class="mb-3">Event Registration</Heading>
<p class="mb-10 font-light">
    You are registering for the event <b>{event.name}</b> on {event.start_date} to {event.end_date}. Please fill the following form to register for the event. Your information was automatically filled based on your account information.<br><br>
    Once this form is submitted, you <b>cannot</b> change the information you provided to the event. If you need to update your information, please contact the event organizers.
</p>
{#if deadline && deadline > now}
    <Alert color="red">
        Registration for this event has been closed.
    </Alert>
    <p class="text-center mt-10">
        <Button color="alternative" href={event.link_info} size="lg" data-sveltekit-reload>Return to Event Page</Button>
    </p>
{:else}
<form use:felteForm method="post" class="space-y-5">
    <RegistrationForm data={$formData} errors={$errors} config={form_config} />
    {#if data.questions.length > 0}
        <Heading tag="h2" customSize="text-lg font-bold" class="pt-3">Event Specific Information</Heading>
        <div>
            {#each data.questions as question}
            <div class="mb-3">
                <Label for={question.id} class="block mb-5">{@render process_spaces(question.question.question)}</Label>
                {#if question.question.type === 'select'}
                <Select id={question.id} name={question.id} class="mb-6" required>
                    {#each question.question.options as option, oidx}
                    <option value={option}>{option}</option>
                    {/each}
                </Select>
                {:else if question.question.type === 'checkbox'}
                {#each question.question.options as option, oidx}
                    <div class="flex">
                        <Checkbox id={`${question.id}_${oidx}`} name={`${question.id}_${oidx}`} class="mb-5" checked>{option}</Checkbox>
                    </div>
                {/each}
                {:else if question.question.type === 'text'}
                <div class="mb-6">
                    <Input type="text" id={question.id} name={question.id} />
                </div>
                {:else if question.question.type === 'textarea'}
                <div class="mb-6">
                    <Textarea type="text" id={question.id} name={question.id} />
                </div>
                {/if}
            </div>
            {/each}
        </div>
    {/if}
    {#if error_message}
        <Alert color="red" class="mb-4 error">{error_message}</Alert>
    {/if}
    <div class="flex flex-col md:flex-row justify-center gap-4">
        <Button type="submit" color="blue" size="lg" disabled={$isSubmitting}>Register</Button>
        <Button color="alternative" href={event.link_info} size="lg" data-sveltekit-reload>Return to Event Page</Button>
    </div>
</form>
{/if}