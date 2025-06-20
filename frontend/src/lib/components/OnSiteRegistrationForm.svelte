<script>
  import { Input, Label, Alert } from 'flowbite-svelte';

  // Props to accept form data and errors from parent
  export let data = {
    first_name: '',
    middle_initial: '',
    last_name: '',
    institute: '',
    job_title: '',
  };
  export let errors = {};
</script>
  
<div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
  <div class="mb-6">
    <Label for="first_name" class="block mb-2">First Name*</Label>
    <Input id="first_name" name="first_name" bind:value={data.first_name} />
    {#if errors.first_name}
      <Alert type="error" color="red" class="mb-6 mt-3">
        <p class="text-sm">{errors.first_name}</p>
      </Alert>
    {/if}
  </div>
  <div class="mb-6">
    <Label for="middle_initial" class="block mb-2">Middle Initial</Label>
    <Input id="middle_initial" name="middle_initial" maxlength="1" bind:value={data.middle_initial} />
    {#if errors.middle_initial}
      <Alert type="error" color="red" class="mb-6 mt-3">
        <p class="text-sm">{errors.middle_initial}</p>
      </Alert>
    {/if}
  </div>
  <div class="mb-6">
    <Label for="last_name" class="block mb-2">Last Name*</Label>
    <Input id="last_name" name="last_name" bind:value={data.last_name} />
    {#if errors.last_name}
      <Alert type="error" color="red" class="mb-6 mt-3">
        <p class="text-sm">{errors.last_name}</p>
      </Alert>
    {/if}
  </div>
</div>

<div class="mb-6">
  <Label for="institute" class="block mb-2">Institute*</Label>
  <Input id="institute" name="institute" bind:value={data.institute} />
  {#if errors.institute}
    <Alert type="error" color="red" class="mb-6 mt-3">
      <p class="text-sm">{errors.institute}</p>
    </Alert>
  {/if}
</div>

<div class="mb-6">
  <Label for="job_title" class="block mb-2">Job Title*</Label>
  <Input id="job_title" name="job_title" bind:value={data.job_title} />
  {#if errors.job_title}
    <Alert type="error" color="red" class="mb-6 mt-3">
      <p class="text-sm">{errors.job_title}</p>
    </Alert>
  {/if}
</div>