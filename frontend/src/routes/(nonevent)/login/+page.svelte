<script>
    import { A, Card, Button, Heading, Indicator, Label, Input, Checkbox, Select, Alert } from 'flowbite-svelte';
    import { onMount } from 'svelte';
    import * as m from '$lib/paraglide/messages.js';

    import 'academicons';

    let { data, form } = $props();

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
                <Alert color="red" class="mb-4" dismissable>{form.message}</Alert>
                {/if}
                {#if data.sociallogin_error}
                <Alert color="red" class="mb-4" dismissable>{m.login_orcidNotLinked()}</Alert>
                {/if}
                <Button type="submit" color="primary" class="w-full">{m.login_submit()}</Button>
                <Button on:click={login_orcid}
                    color="none" class="w-full py-0" style="color: #555;">{m.login_orcidButton()}<i class="ai ai-orcid ai-2x ml-1" style="color: #A6CE39;"></i></Button>
                <p class="text-sm font-bold text-gray-600 text-center mb-0">
                    <a href="/forgot-password?next={encodeURIComponent(data.next || '/')}" class="text-sm text-blue-500">{m.login_forgotPassword()}</a><br>
                </p>
            </form>
        </div>
    </Card>
</div>
