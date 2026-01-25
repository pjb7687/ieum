<script>
    let { data } = $props();

    import { Card, Button, Alert, Spinner } from 'flowbite-svelte';
    import * as m from '$lib/paraglide/messages.js';

    let verifying = $state(false);
    let success = $state(false);
    let errorMessage = $state('');

    const verifyEmail = async () => {
        verifying = true;
        errorMessage = '';

        const response = await fetch('?/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
            },
            body: new URLSearchParams({
                key: data.key
            }),
        });

        if (!response.ok || response.status !== 200) {
            verifying = false;
            const rtn = await response.json();
            errorMessage = rtn.error?.message || 'An error occurred during verification.';
        } else {
            success = true;
            // Redirect will happen automatically from server action
        }
    };
</script>

<div class="container mx-auto max-w-2xl my-10 px-3 sm:px-7">
    <Card size="xl" padding="xl">
        <div class="text-center mb-6">
            {#if success}
                <svg class="mx-auto mb-4 text-green-600 w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            {:else if verifying}
                <div class="flex justify-center mb-4">
                    <Spinner size="12" color="blue" />
                </div>
            {:else}
                <svg class="mx-auto mb-4 text-blue-600 w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
            {/if}

            <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-3">
                {m.verifyEmail_title()}
            </h1>

            <p class="text-base text-gray-600 dark:text-gray-400">
                {#if success}
                    {m.verifyEmail_successMessage()}
                {:else if verifying}
                    {m.verifyEmail_verifying()}
                {:else}
                    {m.verifyEmail_description()}
                {/if}
            </p>
        </div>

        {#if errorMessage}
            <Alert color="red" class="mb-6" dismissable>
                <p>{errorMessage}</p>
            </Alert>
        {/if}

        {#if !verifying && !success}
            <div class="flex justify-center">
                <Button onclick={verifyEmail} color="primary" size="lg" class="w-full sm:w-auto">
                    {m.verifyEmail_submit()}
                </Button>
            </div>
        {/if}
    </Card>
</div>
