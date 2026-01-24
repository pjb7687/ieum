<script>
    import { enhance } from '$app/forms';
    import { goto, invalidateAll } from '$app/navigation';

    import { A, Card, Button, Heading, Indicator, Label, Input, Checkbox, Select, Alert } from 'flowbite-svelte';
    import { onMount } from 'svelte';

    import 'academicons';

    let { data, form } = $props();

    function fUp(s){
        return s[0].toUpperCase() + s.slice(1);
    }

    let isLoggingIn = $state(false);
    const handleLogin = () => {
      if (isLoggingIn) return;
      isLoggingIn = true;
      return async ({ result, update }) => {
        if (result.type === 'success') {
            // Redirect to homepage after login
            goto('/', { invalidateAll: true });
        } else {
            isLoggingIn = false;
            await update();
        }
      };
    };

    const login_orcid = () => {
        let formdata = {
            provider: 'orcid',
            process: 'login',
            callback_url: '/login',
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
            <h3 class="text-xl font-medium text-gray-900 dark:text-white">Create a registration account</h3>
            <p class="text-sm !mt-2">New with us? Create an account to proceed.</p>
            <Button class="w-full" href="/registration?next=/login">Create an account</Button>
        </div>
        <div class="border-l border-b p-8">
            <h3 class="text-xl font-medium text-gray-900 dark:text-white">Sign in to your account</h3>
            <p class="text-sm !mt-2">Please log in to access your account.</p>
            <form method="POST" action="?/login" use:enhance={handleLogin} class="space-y-4 mt-6">
                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700">Email*</label>
                    <Input id="email" name="username" type="email" required class="mt-1" />
                </div>
                <div>
                    <label for="password" class="block text-sm font-medium text-gray-700">Password*</label>
                    <Input id="password" name="password" type="password" required class="mt-1" />
                </div>
                {#if form?.error}
                <Alert color="red" class="mb-4" dismissable>{form.message}</Alert>
                {/if}
                {#if data.sociallogin_error}
                <Alert color="red" class="mb-4" dismissable>ORCID is not linked to any account. Please link ORCID after login.</Alert>
                {/if}
                <Button type="submit" color="primary" class="w-full" disabled={isLoggingIn}>Login</Button>
                <Button on:click={login_orcid}
                    color="none" class="w-full py-0" style="color: #555;" disabled={isLoggingIn}>Or, click here to login via<i class="ai ai-orcid ai-2x ml-1" style="color: #A6CE39;"></i></Button>
                <p class="text-sm font-bold text-gray-600 text-center mb-0">
                    <a href="/forgot-password?next=/login" class="text-sm text-blue-500">Forgot your password?</a><br>
                </p>
            </form>
        </div>
    </Card>
</div>
