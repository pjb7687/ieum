<script>
    import { enhance } from '$app/forms';
    import { goto } from '$app/navigation';
    
    import { A, List, Li, Card, Button, Heading, Indicator, Label, Input, Dropzone, Checkbox, Select, Alert, Navbar } from 'flowbite-svelte';
    import { onMount } from 'svelte';

    import { createForm } from 'felte';
    import { validator } from '@felte/validator-yup';
    import * as yup from 'yup';

    let { data, form } = $props();

    const schema = yup.object({
        password: yup.string().required('Password is required.').min(8, 'Password must be at least 8 characters.'),
        confirm_password: yup.string().required('Passwords do not match.').oneOf([yup.ref('password'), null], 'Passwords do not match.'),
    });

    let me = data.user;
    let error_message = $state('');
    let success_message = $state('');
    let submitted = $state(false);
    const { form: felteForm, data: formData, errors, isSubmitting } = createForm({
        onSubmit: async (data) => {
            const response = await fetch('?/password',
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
            } else {
                submitted = true;
                success_message = 'Password has been reset. Please login with your new password.';
            }
        },
        extend: validator({ schema }),
        onError: (errors) => {
            // scroll to top
            error_message = errors.message;
            return errors;
        }
    });
</script>

<Heading tag="h1" class="text-2xl font-bold mb-3">Reset Password</Heading>
<p class="mb-5 font-light">Please enter your new password.</p>
<form use:felteForm method="post" class="space-y-5">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div class="mb-6">
          <Label for="password" class="block mb-2">Password <span class="text-red-500">*</span></Label>
          <Input id="password" name="password" type="password" bind:value={$formData.password} />
          {#if $errors.password}
            <Alert type="error" color="red" class="mb-6 mt-3">
              <p class="text-sm">{$errors.password}</p>
            </Alert>
          {/if}
        </div>
        <div class="mb-6">
          <Label for="confirm_password" class="block mb-2">Confirm Password <span class="text-red-500">*</span></Label>
          <Input id="confirm_password" name="confirm_password" type="password" bind:value={$formData.confirm_password} />
          {#if $errors.confirm_password}
            <Alert type="error" color="red" class="mb-6 mt-3">
              <p class="text-sm">{$errors.confirm_password}</p>
            </Alert>
          {/if}
        </div>
        <Input type="hidden" name="key" value={data.key} />
    </div>
    {#if error_message}
    <Alert type="error" color="red" class="mb-6 mt-3">
      <p class="text-sm">{error_message}</p>
    </Alert>
    {/if}
    {#if success_message}
        <Alert type="success" color="green" class="mb-6 mt-3">
            <p class="text-sm">{success_message}</p>
        </Alert>
    {/if}
    <div class="flex flex-col md:flex-row justify-center gap-4">
        <Button type="submit" color="primary" size="lg" disabled={$isSubmitting || submitted}>Reset Password</Button>
    </div>
</form>