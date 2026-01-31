<script>
    let { data: page_data } = $props();

    import { onMount } from 'svelte';
    import { createForm } from 'felte';
    import { validator } from '@felte/validator-yup';
    import * as yup from 'yup';
    import { Alert, Input, Textarea, Select, Button, Label, InputAddon, ButtonGroup, Heading, Card, Modal } from 'flowbite-svelte';
    import { UserCircleSolid } from 'flowbite-svelte-icons';
    import { goto } from '$app/navigation';
    import * as m from '$lib/paraglide/messages.js';

    import RegistrationForm from '$lib/components/RegistrationForm.svelte';

    let success = $state(false);
    let showResetPasswordModal = $state(false);
    let resetPasswordSuccess = $state(false);
    let resetPasswordError = $state('');
    let resetPasswordLoading = $state(false);

    async function handleResetPassword() {
        resetPasswordLoading = true;
        resetPasswordError = '';
        try {
            const response = await fetch('?/reset_password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json',
                },
                body: new URLSearchParams({ email: me.email }),
            });
            if (!response.ok || response.status !== 200) {
                const rtn = await response.json();
                throw new Error(rtn.error?.message || 'Failed to send reset email');
            }
            resetPasswordSuccess = true;
            showResetPasswordModal = false;
        } catch (err) {
            resetPasswordError = err.message || 'An error occurred';
        } finally {
            resetPasswordLoading = false;
        }
    }

    const schema = yup.object({
        email: yup.string().email().required(),
        first_name: yup.string().required('First name is required.'),
        last_name: yup.string().required('Last name is required.'),
        middle_initial: yup.string().max(1),
        korean_name: yup.string(),
        nationality: yup.string().required(),
        job_title: yup.string().required(m.validation_jobTitleRequired()),
        department: yup.string(),
        institute: yup.number().required('Institute is required.'),
        orcid: yup.string(),
        google: yup.string(),
        disability: yup.string(),
        dietary: yup.string(),
    });

    let form_config = {
        next: page_data.next,
        action: 'profile',
        hide_password: true,
        csrf_token: page_data.csrf_token,
    }

    let me = page_data.user;

    const { form: felteForm, data, errors, isSubmitting } = createForm({
        initialValues: {
            email: me.email,
            first_name: me.first_name,
            middle_initial: me.middle_initial,
            korean_name: me.korean_name || '',
            last_name: me.last_name,
            nationality: me.nationality ? me.nationality.toString() : undefined,
            institute: me.institute,
            department: me.department,
            job_title: me.job_title,
            disability: me.disability,
            dietary: me.dietary,
            orcid: me.orcid,
            google: me.google || '',
        },
        onSubmit: async (data) => {
            success = false;
            data.username = data.email;
            const response = await fetch('?/update',
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
            success = true;
        },
        extend: validator({ schema }),
        onError: (errors) => {
            return errors;
        }
    });
</script>

<!-- Page Header Card -->
<div class="relative rounded-lg shadow-sm py-16 px-8 mb-8 overflow-hidden" style="background-image: url('/bg-events.webp'); background-size: cover; background-position: center;">
    <div class="absolute inset-0 bg-slate-900 opacity-60"></div>
    <div class="relative z-10">
        <h1 class="text-3xl font-bold text-white">{m.profile_title()}</h1>
        <p class="text-slate-200 mt-2">{m.profile_description()}</p>
    </div>
</div>

<!-- Form Card -->
<div class="bg-white border border-gray-200 rounded-lg shadow-sm p-8">
    <form use:felteForm method="post">
        <RegistrationForm data={$data} errors={$errors} config={form_config} institution_resolved={page_data.user?.institution_resolved} />
        {#if success}
        <Alert color="blue" class="mb-4" dismissable>{m.profile_updateSuccess()}</Alert>
        {/if}
        {#if resetPasswordSuccess}
        <Alert color="green" class="mb-4" dismissable>{m.profile_resetPasswordSuccess()}</Alert>
        {/if}
        <div class="flex flex-col md:flex-row justify-center gap-4 mt-8">
            <Button type="submit" size="lg" color="primary" disabled={$isSubmitting}>{m.profile_updateInfo()}</Button>
            <Button type="button" onclick={() => showResetPasswordModal = true} size="lg" color="light">{m.profile_resetPassword()}</Button>
            <Button onclick={() => goto(page_data.next)} size="lg" color="alternative">{m.common_goBack()}</Button>
        </div>
    </form>
</div>

<!-- Reset Password Confirmation Modal -->
<Modal bind:open={showResetPasswordModal} size="sm" autoclose={false} class="w-full">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">{m.profile_resetPasswordConfirmTitle()}</h3>
    <p class="text-gray-600 mb-6">{m.profile_resetPasswordConfirmMessage()}</p>
    {#if resetPasswordError}
    <Alert color="red" class="mb-4">{resetPasswordError}</Alert>
    {/if}
    <div class="flex justify-end gap-3">
        <Button color="alternative" onclick={() => showResetPasswordModal = false}>{m.profile_resetPasswordCancel()}</Button>
        <Button color="primary" onclick={handleResetPassword} disabled={resetPasswordLoading}>{m.profile_resetPasswordConfirm()}</Button>
    </div>
</Modal>