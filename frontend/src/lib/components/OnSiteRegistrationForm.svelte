<script>
  import { Input, Label, Alert } from 'flowbite-svelte';
  import * as m from '$lib/paraglide/messages.js';

  // Props to accept form data and errors from parent
  export let data = {
    name: '',
    email: '',
    institute: '',
    job_title: '',
  };
  export let errors = {};
</script>

<div class="mb-6">
  <Label for="name" class="block mb-2">{m.onsiteRegistration_name()}</Label>
  <Input id="name" name="name" bind:value={data.name} />
  {#if errors.name}
    <Alert type="error" color="red" class="mb-6 mt-3">
      <p class="text-sm">{errors.name}</p>
    </Alert>
  {/if}
</div>

<div class="mb-6">
  <Label for="email" class="block mb-2">{m.onsiteRegistration_email()}</Label>
  <Input id="email" name="email" type="email" bind:value={data.email} />
  {#if errors.email}
    <Alert type="error" color="red" class="mb-6 mt-3">
      <p class="text-sm">{errors.email}</p>
    </Alert>
  {/if}
</div>

<div class="mb-6">
  <Label for="institute" class="block mb-2">{m.onsiteRegistration_institute()}</Label>
  <Input id="institute" name="institute" bind:value={data.institute} />
  {#if errors.institute}
    <Alert type="error" color="red" class="mb-6 mt-3">
      <p class="text-sm">{errors.institute}</p>
    </Alert>
  {/if}
</div>

<div class="mb-6">
  <Label for="job_title" class="block mb-2">{m.onsiteRegistration_jobTitle()}</Label>
  <Input id="job_title" name="job_title" bind:value={data.job_title} />
  {#if errors.job_title}
    <Alert type="error" color="red" class="mb-6 mt-3">
      <p class="text-sm">{errors.job_title}</p>
    </Alert>
  {/if}
</div>