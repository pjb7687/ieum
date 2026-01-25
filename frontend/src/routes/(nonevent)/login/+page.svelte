<script>
    import { A, Card, Button, Heading, Indicator, Label, Input, Checkbox, Select, Alert, Modal } from 'flowbite-svelte';
    import { onMount } from 'svelte';
    import * as m from '$lib/paraglide/messages.js';

    import 'academicons';

    let { data, form } = $props();

    let successModal = $state(false);

    // Show modal when verification email is sent successfully
    $effect(() => {
        if (form?.success) {
            successModal = true;
        }
    });

    function fUp(s){
        return s[0].toUpperCase() + s.slice(1);
    }

    const login_orcid = () => {
        const next = data.next || '/';
        const callback_url = `/login${next !== '/' ? `?next=${encodeURIComponent(next)}` : ''}`;

        let formdata = {
            provider: 'orcid',
            process: 'login',
            callback_url: callback_url,
            csrfmiddlewaretoken: data.csrf_token,
        };
        // create a form element
        let form = document.createElement('form');
        form.setAttribute('method', 'POST');
        form.setAttribute('action', '/_allauth/browser/v1/auth/provider/redirect');
        form.style.display = 'hidden';
        // append the form to the body
        document.body.appendChild(form);
        // add the data to the form
        for (let key in formdata) {
            let input = document.createElement('input');
            input.setAttribute('type', 'hidden');
            input.setAttribute('name', key);
            input.setAttribute('value', formdata[key]);
            form.appendChild(input);
        }
        // submit the form
        form.submit();
    };

    const resendVerification = (email, verificationKey) => {
        // create a form element dynamically to submit the resend action
        let resendForm = document.createElement('form');
        resendForm.setAttribute('method', 'POST');
        resendForm.setAttribute('action', '?/resendVerification');
        resendForm.style.display = 'none';

        // add email input
        let emailInput = document.createElement('input');
        emailInput.setAttribute('type', 'hidden');
        emailInput.setAttribute('name', 'email');
        emailInput.setAttribute('value', email);
        resendForm.appendChild(emailInput);

        // add verification key input
        let keyInput = document.createElement('input');
        keyInput.setAttribute('type', 'hidden');
        keyInput.setAttribute('name', 'verificationKey');
        keyInput.setAttribute('value', verificationKey);
        resendForm.appendChild(keyInput);

        // append to body and submit
        document.body.appendChild(resendForm);
        resendForm.submit();
    };
</script>

<div class="container mx-auto max-w-4xl my-10 px-3 sm:px-7">
    <Card size="none" padding="none" class="grid md:grid-cols-2">
        <div class="p-8 flex flex-col space-y-8 border-l border-b">
            <h3 class="text-xl font-medium text-gray-900 dark:text-white">{m.login_createAccountTitle()}</h3>
            <p class="text-sm !mt-2">{m.login_createAccountDescription()}</p>
            <Button class="w-full" href="/registration?next={encodeURIComponent(data.next || '/')}">{m.login_createAccountButton()}</Button>
        </div>
        <div class="border-l border-b p-8">
            <h3 class="text-xl font-medium text-gray-900 dark:text-white">{m.login_title()}</h3>
            <p class="text-sm !mt-2">{m.login_description()}</p>
            <form method="POST" action="?/login" class="space-y-4 mt-6">
                <input type="hidden" name="next" value={data.next || '/'} />
                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700">{m.form_email()}*</label>
                    <Input id="email" name="username" type="email" required class="mt-1" />
                </div>
                <div>
                    <label for="password" class="block text-sm font-medium text-gray-700">{m.form_password()}*</label>
                    <Input id="password" name="password" type="password" required class="mt-1" />
                </div>
                {#if form?.error}
                <Alert color="red" class="mb-4" dismissable>
                    <p>{form.message}</p>
                    {#if form?.needsVerification}
                        <p class="text-sm mt-2">
                            {m.login_emailNotDelivered()} <button type="button" class="underline" onclick={() => resendVerification(form.email, form.verificationKey)}>{m.login_resendVerificationLink()}</button>
                        </p>
                    {/if}
                </Alert>
                {/if}
                {#if data.sociallogin_error}
                <Alert color="red" class="mb-4" dismissable>{m.login_orcidNotLinked()}</Alert>
                {/if}
                <Button type="submit" color="primary" class="w-full">{m.login_submit()}</Button>
                <Button onclick={login_orcid}
                    color="none" class="w-full py-0" style="color: #555;">{m.login_orcidButton()}<i class="ai ai-orcid ai-2x ml-1" style="color: #A6CE39;"></i></Button>
                <p class="text-sm font-bold text-gray-600 text-center mb-0">
                    <a href="/forgot-password?next={encodeURIComponent(data.next || '/')}" class="text-sm text-blue-500">{m.login_forgotPassword()}</a><br>
                </p>
            </form>
        </div>
    </Card>
</div>

<Modal bind:open={successModal} size="sm" autoclose outsideclose>
    <div class="text-center">
        <svg class="mx-auto mb-4 text-green-600 w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <h3 class="mb-5 text-lg font-normal text-gray-500">
            {form?.message || m.login_verificationEmailSent()}
        </h3>
        <Button color="green" onclick={() => successModal = false}>{m.common_ok()}</Button>
    </div>
</Modal>
