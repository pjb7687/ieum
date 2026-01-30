<script>
    import { enhance } from '$app/forms';
    import { goto } from '$app/navigation';
    
    import { A, List, Li, Card, Button, Heading, Indicator, Label, Input, Dropzone, Checkbox, Select, Alert, Navbar } from 'flowbite-svelte';
    import { onMount } from 'svelte';

    import { createForm } from 'felte';
    import { validator } from '@felte/validator-yup';
    import * as yup from 'yup';

    import RegistrationForm from '$lib/components/RegistrationForm.svelte';
    import 'academicons';

    let { data, form } = $props();

    let event = data.event;
    let abstract = data.abstract;

    const schema = yup.object({
        title: yup.string().required('Title is required.'),
    });

    let me = data.user;
    let error_message = $state('');
    const { form: felteForm, data: formData, errors, isSubmitting } = createForm({
        initialValues: {
            is_oral: true,
        },
        onSubmit: async (data) => {
            const fd = new FormData();
            fd.append('title', data.title);
            fd.append('is_oral', data.is_oral);
            fd.append('file_name', abstract_file.file_name);
            fd.append('file_content', abstract_file.file_content);

            const response = await fetch('?/abstract',
                {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json',
                    },
                    body: fd
                }
            );
            if (!response.ok || response.status !== 200) {
                const rtn = await response.json();
                throw rtn.error;
            }
            location.reload();
        },
        extend: validator({ schema }),
        onError: (errors) => {
            // scroll to top
            error_message = errors.message;
            return errors;
        }
    });

    let abstract_file = $state({
        file_name: '',
        file_content: '',
    });

    const set_file = (file) => {
        let ext = file.name.split('.').pop();
        if (ext !== 'docx' && ext !== 'odt') {
            error_message = 'Invalid file format. Please upload a DOCX or ODT file.';
            return;
        }
        if (file.size > 1048576) {
            error_message = 'File size exceeds the limit of 1 MB.';
            return;
        }

        // read the file as a base64 string
        const reader = new FileReader();
        reader.onload = (event) => {
            error_message = '';
            abstract_file.file_name = file.name;
            abstract_file.file_content = event.target.result;
            abstract_file = abstract_file;
        };
        reader.readAsDataURL(file);
    };

    const unset_file = () => {
        abstract_file.file_name = '';
        abstract_file.file_content = null;
        abstract_file = abstract_file;
    };

    const dropHandle = (event) => {
        unset_file();
        event.preventDefault();
        if (event.dataTransfer.items) {
        [...event.dataTransfer.items].forEach((item, i) => {
            if (item.kind === 'file') {
                const file = item.getAsFile();
                set_file(file);
                return;
            }
        });
        } else {
            [...event.dataTransfer.files].forEach((file, i) => {
                set_file(file);
                return;
            });
        }
    };

    const handleChange = (event) => {
        const files = event.target.files;
        if (files.length > 0) {
            set_file(files[0]);
        }
    };
</script>

<Heading tag="h1" class="text-2xl font-bold mb-3">Abstract Submittion</Heading>
{#if data.abstract_submitted}
<p class="mb-10 font-light">Thank you for submitting your abstract. You can preview your submission below. If you need to make any changes, please contact the event organizers.</p>
<Card size="xl" class="text-black mb-10">
    <div class="text-center">
        <h3 class="text-lg font-bold">{abstract.title}</h3>
        <p class="text-sm text-gray-600 mb-6">Presented by {me.first_name} {#if me.middle_initial}{me.middle_initial}{/if} {me.last_name}</p>
    </div>
    <hr class="mb-5 border-gray-200" />
    {@html abstract.body}
    <hr class="mb-5 border-gray-200" />
</Card>
<div class="flex flex-col md:flex-row justify-center gap-4">
    <Button href={abstract.link} color="primary" size="lg" data-sveltekit-reload>Download Submission</Button>
    <Button href="/event/{event.id}" color="alternative" size="lg" data-sveltekit-reload>Go Back</Button>
</div>
{:else}
<p class="mb-5 font-light">Please fill the following form to submit an abstract.</p>
<form use:felteForm method="post" class="space-y-5">
    <div class="mb-6">
        <Label for="title" class="block mb-2">Abstract Title*</Label>
        <Input id="title" name="title" type="text" bind:value={$formData.title} />
        {#if $errors.title}
            <Alert type="error" color="red" class="mb-6 mt-3">
            <p class="text-sm">{$errors.title}</p>
            </Alert>
        {/if}
    </div>
    <div class="mb-6">
        <Label for="abstract" class="block mb-3">Abstract File*</Label>
        <p class="mb-2 text-sm">Please use one of the following templates:</p>
        <List list="disc" class="mb-5">
            <Li class="mb-2 font-bold text-sm"><A href="/abstract/abstract_template.docx">Download an abstract template in docx format</A></Li>
            <Li class="font-bold text-sm"><A href="/abstract/abstract_template.odt">Download an abstract template in odt format</A></Li>
        </List>
        <Dropzone id="dropzone"
        on:drop={dropHandle}
        on:dragover={(event) => {
            event.preventDefault();
        }}
        on:change={handleChange}>
        <svg aria-hidden="true" class="mb-3 w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
        {#if abstract_file.file_name !== ''}
            <p>{abstract_file.file_name}</p>
        {:else}
            <p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">DOCX or ODT (MAX. 1 MB)</p>
        {/if}
        </Dropzone>
        {#if $errors.file}
            <Alert type="error" color="red" class="mb-6 mt-3">
                <p class="text-sm">{$errors.file}</p>
            </Alert>
        {/if}
    </div>
    {#if error_message}
        <Alert color="red" class="mb-4 error">{error_message}</Alert>
    {/if}
    <Checkbox id="is_oral" name="is_oral" bind:checked={$formData.is_oral} class="mb-6">I would like to be considered for an oral presentation</Checkbox>
    <div class="flex flex-col md:flex-row justify-center gap-4">
        <Button type="submit" color="primary" size="lg" disabled={$isSubmitting}>Submit Abstract</Button>
        <Button href="/event/{event.id}" color="alternative" size="lg" data-sveltekit-reload>Go Back</Button>
    </div>
</form>
{/if}