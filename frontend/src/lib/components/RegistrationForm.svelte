<script>
  import { Heading, Input, ButtonGroup, InputAddon, Button, Textarea, Select, Label, Alert } from 'flowbite-svelte';
  import * as m from '$lib/paraglide/messages.js';
  import InstitutionLookup from '$lib/components/InstitutionLookup.svelte';

  // Props to accept form data and errors from parent
  export let data = {
    first_name: '',
    middle_initial: '',
    korean_name: '',
    last_name: '',
    nationality: undefined,
    institute: '',
    department: '',
    job_title: '',
    disability: '',
    dietary: '',
    email: '',
    password: '',
    confirm_password: '',
    orcid: '',
  };
  export let errors = {};
  export let config = {};
  export let institutions = [];

  function link_orcid() {
    let data = {
      provider: 'orcid',
      process: 'connect',
      callback_url: config.action?`/${config.action}?next=${config.next}`:config.next,
      csrfmiddlewaretoken: config.csrf_token,
    };
    // create a form element
    let form = document.createElement('form');
    form.setAttribute('method', 'POST');
    form.setAttribute('action', '/_allauth/browser/v1/auth/provider/redirect');
    form.style.display = 'hidden';
    // append the form to the body
    document.body.appendChild(form);
    // add the data to the form
    for (let key in data) {
      let input = document.createElement('input');
      input.setAttribute('type', 'hidden');
      input.setAttribute('name', key);
      input.setAttribute('value', data[key]);
      form.appendChild(input);
    }
    // submit the form
    form.submit();
  }

  function unlink_orcid() {
    fetch('/_allauth/browser/v1/account/providers', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': config.csrf_token,
      },
      body: JSON.stringify({
        provider: 'orcid',
        account: data.orcid,
      }),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to unlink ORCID');
      }
      data.orcid = '';
    })
    .catch(error => {
      console.error(error);
    });
  }
</script>
  
{#if !config.hide_login_info}
<!-- Login Information -->
<Heading tag="h2" customSize="text-lg font-bold" class="mb-6">{m.form_personalInfo()}</Heading>
<div class="mb-6">
  <Label for="email" class="block mb-2 text-dark">{m.form_email()}*</Label>
  <Input type="email" id="email" name="email" bind:value={data.email} disabled={config.hide_password} />
  {#if errors.email}
    <Alert type="error" color="red" class="mb-6 mt-3">
      <p class="text-sm">{errors.email}</p>
    </Alert>
  {/if}
</div>
{#if config.hide_password}
<div class="mb-6">
  <Label for="orcid" class="block mb-2 text-dark">{m.form_orcid()}</Label>
  <ButtonGroup class="w-full">
    <Input id="orcid" name="orcid" bind:value={data.orcid} disabled />
      {#if data.orcid}
      <Button onclick={unlink_orcid} class="w-40" style="background-color: #A6CE39; color: white;">
        {m.form_unlinkOrcid()}
      </Button>
      {:else}
      <Button onclick={link_orcid} class="w-40" style="background-color: #A6CE39; color: white;">
        {m.form_linkOrcid()}
      </Button>
      {/if}
  </ButtonGroup>
  {#if errors.orcid}
    <Alert type="error" color="red" class="mb-6 mt-3">
      <p class="text-sm">{errors.orcid}</p>
    </Alert>
  {/if}
</div>
{/if}
{#if !config.hide_password}
<div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
  <div class="mb-6">
    <Label for="password" class="block mb-2">{m.form_password()}*</Label>
    <Input id="password" name="password" type="password" bind:value={data.password} />
    {#if errors.password}
      <Alert type="error" color="red" class="mb-6 mt-3">
        <p class="text-sm">{errors.password}</p>
      </Alert>
    {/if}
  </div>
  <div class="mb-6">
    <Label for="confirm_password" class="block mb-2">{m.form_confirmPassword()}*</Label>
    <Input id="confirm_password" name="confirm_password" type="password" bind:value={data.confirm_password} />
    {#if errors.confirm_password}
      <Alert type="error" color="red" class="mb-6 mt-3">
        <p class="text-sm">{errors.confirm_password}</p>
      </Alert>
    {/if}
  </div>
</div>
{/if}
{/if}

<div class="mb-6">
  <Label for="nationality" class="block mb-2">{m.form_nationality()}*</Label>
  <Select id="nationality" name="nationality" bind:value={data.nationality} items={
    [
      { value: "1", name: m.form_nationalityKorean() },
      { value: "2", name: m.form_nationalityNonKorean() },
      { value: "3", name: m.form_nationalityPreferNot() },
    ]
  } />
  {#if errors.nationality}
    <Alert type="error" color="red" class="mb-6 mt-3">
      <p class="text-sm">{errors.nationality}</p>
    </Alert>
  {/if}
</div>

<div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
  <div class="mb-6">
    <Label for="first_name" class="block mb-2">{m.form_firstName()}*</Label>
    <Input id="first_name" name="first_name" bind:value={data.first_name} />
    {#if errors.first_name}
      <Alert type="error" color="red" class="mb-6 mt-3">
        <p class="text-sm">{errors.first_name}</p>
      </Alert>
    {/if}
  </div>
  <div class="mb-6">
    <Label for="middle_initial" class="block mb-2">{m.form_middleInitial()}</Label>
    <Input id="middle_initial" name="middle_initial" maxlength="1" bind:value={data.middle_initial} />
  </div>
  <div class="mb-6">
    <Label for="last_name" class="block mb-2">{m.form_lastName()}*</Label>
    <Input id="last_name" name="last_name" bind:value={data.last_name} />
    {#if errors.last_name}
      <Alert type="error" color="red" class="mb-6 mt-3">
        <p class="text-sm">{errors.last_name}</p>
      </Alert>
    {/if}
  </div>
</div>

{#if data.nationality === 1 || data.nationality === "1"}
<div class="mb-6">
  <Label for="korean_name" class="block mb-2">{m.form_koreanName()}</Label>
  <Input id="korean_name" name="korean_name" bind:value={data.korean_name} />
  {#if errors.korean_name}
    <Alert type="error" color="red" class="mb-6 mt-3">
      <p class="text-sm">{errors.korean_name}</p>
    </Alert>
  {/if}
</div>
{/if}

<!-- Additional Information -->
<hr class="my-8 border-gray-200" />
<Heading tag="h2" customSize="text-lg font-bold" class="mb-6">{m.form_additionalInfo()}</Heading>
<div class="mb-6">
  <InstitutionLookup bind:value={data.institute} error={errors.institute} required={true} bind:institutions />
</div>

<div class="mb-6">
  <Label for="department" class="block mb-2">{m.form_department()}</Label>
  <Input id="department" name="department" bind:value={data.department} />
</div>

<div class="mb-6">
  <Label for="job_title" class="block mb-2">{m.form_jobTitle()}</Label>
  <Input id="job_title" name="job_title" bind:value={data.job_title} />
</div>

<div class="mb-6">
  <Label for="disability" class="block mb-2">{m.form_disability()}</Label>
  <Textarea id="disability" name="disability" bind:value={data.disability} />
</div>

<div class="mb-6">
  <Label for="dietary" class="block mb-2">{m.form_dietary()}</Label>
  <Textarea id="dietary" name="dietary" bind:value={data.dietary} />
</div>