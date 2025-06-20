<script>
    import { goto } from '$app/navigation';
    
    import { A, Card, Button, Heading, Indicator, Label, Input, Checkbox, Select, Alert, Navbar, Textarea } from 'flowbite-svelte';
    import { onMount } from 'svelte';

    import { createForm } from 'felte';
    import { validator } from '@felte/validator-yup';
    import * as yup from 'yup';

    import OnSiteRegistrationForm from '$lib/components/OnSiteRegistrationForm.svelte';

    let { data, form } = $props();

    let event = data.event;
    
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
        institute: yup.string().required('Institute is required.').test('no-korean', 'Korean characters are not allowed.', rejectKorean),
        job_title: yup.string().required('Job title is required.').test('no-korean', 'Korean characters are not allowed.', rejectKorean),
    });

    let error_message = $state('');
    const { form: felteForm, data: formData, errors, isSubmitting } = createForm({
        onSubmit: async (data) => {
            const response = await fetch('?/onsiteregister',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'application/json',
                    },
                    body: new URLSearchParams(data),
                }
            );
            const rtn = await response.json();
            if (!response.ok || response.status !== 200) {
                throw rtn.error;
            }
            // rtn should be 303 see other
            if (rtn.status !== 303) {
                throw new Error('Unexpected response status: ' + rtn.status);
            }
            goto(rtn.location);
        },
        extend: validator({ schema }),
        onError: (errors) => {
            // scroll to top
            error_message = errors.message;
            return errors;
        }
    });
</script>

<Heading tag="h1" customSize="text-2xl font-bold" class="mb-3">On-site Registration</Heading>
<p class="mb-10 font-light">Please fill the below form to register on-site.</p>
<form use:felteForm method="post" class="space-y-5">
    <OnSiteRegistrationForm errors={$errors} />
    {#if error_message}
        <Alert color="red" class="mb-4 error">{error_message}</Alert>
    {/if}
    <div class="flex flex-col md:flex-row justify-center gap-4">
        <Button type="submit" color="blue" size="lg">Register</Button>
    </div>
</form>
