<script>
    import { enhance } from '$app/forms';
    import { goto } from '$app/navigation';

    import { A, Card, Button, Heading, Indicator, Label, Input, Checkbox, Select, Alert, Navbar, Textarea } from 'flowbite-svelte';
    import { onMount } from 'svelte';

    import { createForm } from 'felte';
    import { validator } from '@felte/validator-yup';
    import * as yup from 'yup';

    import RegistrationForm from '$lib/components/RegistrationForm.svelte';
    import * as m from '$lib/paraglide/messages.js';
    import 'academicons';

    let { data, form } = $props();

    let event = data.event;
    let deadline = event.registration_deadline ? new Date(event.registration_deadline) : new Date(event.start_date);
    let now = new Date();

    // Determine which languages are included in the event
    const hasEnglish = event.main_languages && event.main_languages.includes('en');
    const hasKorean = event.main_languages && event.main_languages.includes('ko');

    let form_config = {
        hide_login_info: true,
        show_english_name: hasEnglish,
        show_korean_name: hasKorean,
        allow_korean_institute: hasKorean,
    };

    const koreanRegex = /[\u3131-\u3163\uac00-\ud7a3]/;
    const rejectKorean = (value) => {
        if (!value) return true;
        return !koreanRegex.test(value);
    };

    // Build dynamic validation schema based on event languages
    const schemaFields = {
        nationality: yup.string().required(),
        // All personal info fields allow all languages (set by institution modal or user input)
        job_title: yup.string().required(m.validation_jobTitleRequired()),
        department: yup.string(),
        institute: yup.number().required(m.validation_instituteRequired()),
        disability: yup.string(),
        dietary: yup.string(),
    };

    // Add English name fields if event includes English
    if (hasEnglish) {
        schemaFields.first_name = yup.string().required(m.validation_firstNameRequired()).test('no-korean', m.eventRegister_validationNoKorean(), rejectKorean);
        schemaFields.last_name = yup.string().required(m.validation_lastNameRequired()).test('no-korean', m.eventRegister_validationNoKorean(), rejectKorean);
        schemaFields.middle_initial = yup.string().max(1).test('no-korean', m.eventRegister_validationNoKorean(), rejectKorean);
    }

    // Add Korean name field if event includes Korean
    if (hasKorean) {
        schemaFields.korean_name = yup.string();
        // If only Korean (not English), make Korean name required
        if (!hasEnglish) {
            schemaFields.korean_name = yup.string().required(m.validation_koreanNameRequired());
        }
    }

    const schema = yup.object(schemaFields);

    let me = data.user;
    let error_message = $state('');
    const { form: felteForm, data: formData, errors, isSubmitting } = createForm({
        initialValues: {
            first_name: me?me.first_name:'',
            middle_initial: me?me.middle_initial:'',
            korean_name: me?(me.korean_name || ''):'',
            last_name: me?me.last_name:'',
            nationality: me?(me.nationality ? me.nationality.toString() : '1'):'1',
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

<div class="container mx-auto my-10 px-3 sm:px-7">
    <!-- Page Header Card -->
    <div class="relative rounded-lg shadow-sm py-16 px-8 mb-8 overflow-hidden" style="background-image: url('/bg-events.webp'); background-size: cover; background-position: center;">
        <div class="absolute inset-0 bg-slate-900 opacity-60"></div>
        <div class="relative z-10">
            <h1 class="text-3xl font-bold text-white">{m.eventRegister_title()}</h1>
            <p class="text-slate-200 mt-2">
                <a href="/events" class="hover:underline">{m.eventDetail_breadcrumbEvents()}</a>
                <span class="mx-2">/</span>
                <a href="/event/{event.id}" class="hover:underline">{event.name}</a>
                <span class="mx-2">/</span>
                <span class="text-white font-medium">{m.eventRegister_title()}</span>
            </p>
        </div>
    </div>

    {#if deadline && deadline < now}
        <!-- Registration Closed -->
        <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-8">
            <Alert color="red">
                {m.eventRegister_closed()}
            </Alert>
            <p class="text-center mt-6">
                <Button color="alternative" href="/event/{event.id}" size="lg">{m.eventRegister_returnToEvent()}</Button>
            </p>
        </div>
    {:else}
        <!-- Registration Form -->
        <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-8">
            <div class="mb-8">
                <p class="text-gray-700 mb-2">
                    {m.eventRegister_description()}
                </p>
                <ul class="list-disc ml-8 mb-4 text-gray-700 space-y-1">
                    <li>
                        <span class="font-medium">{m.eventRegister_eventName()}</span> {event.name}
                    </li>
                    <li>
                        <span class="font-medium">{m.eventRegister_eventDates()}</span> {event.start_date} {m.eventRegister_to()} {event.end_date}
                    </li>
                </ul>
                <p class="text-gray-700 mb-4">
                    {m.eventRegister_instructions()}
                </p>
                <Alert color="yellow" class="mb-0">
                    {m.eventRegister_warning()}
                </Alert>
            </div>

            <form use:felteForm method="post" class="space-y-6">
                <RegistrationForm data={$formData} errors={$errors} config={form_config} institution_resolved={data.user?.institution_resolved} />

                {#if data.questions.length > 0}
                    <div class="pt-6 border-t border-gray-200">
                        <h2 class="text-xl font-bold text-gray-900 mb-6">{m.eventRegister_eventSpecificInfo()}</h2>
                        <div class="space-y-6">
                            {#each data.questions as question}
                                <div>
                                    <Label for={question.id} class="block mb-2">{@render process_spaces(question.question.question)}</Label>
                                    {#if question.question.type === 'select'}
                                        <Select id={question.id} name={question.id} required>
                                            {#each question.question.options as option, oidx}
                                                <option value={option}>{option}</option>
                                            {/each}
                                        </Select>
                                    {:else if question.question.type === 'checkbox'}
                                        <div class="space-y-2">
                                            {#each question.question.options as option, oidx}
                                                <Checkbox id={`${question.id}_${oidx}`} name={`${question.id}_${oidx}`} checked>{option}</Checkbox>
                                            {/each}
                                        </div>
                                    {:else if question.question.type === 'text'}
                                        <Input type="text" id={question.id} name={question.id} />
                                    {:else if question.question.type === 'textarea'}
                                        <Textarea id={question.id} name={question.id} rows={4} />
                                    {/if}
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}

                {#if error_message}
                    <Alert color="red" class="error">{error_message}</Alert>
                {/if}

                <div class="flex flex-col md:flex-row justify-center gap-4 pt-4">
                    <Button type="submit" color="primary" size="lg" disabled={$isSubmitting}>{m.eventRegister_submit()}</Button>
                    <Button color="alternative" href="/event/{event.id}" size="lg">{m.eventRegister_returnToEvent()}</Button>
                </div>
            </form>
        </div>
    {/if}
</div>