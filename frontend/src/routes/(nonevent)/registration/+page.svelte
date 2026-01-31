<script>
    let { data: page_data } = $props();

    import RegistrationForm from '$lib/components/RegistrationForm.svelte';

    import { goto } from '$app/navigation';
    import { createForm } from 'felte';
    import { validator } from '@felte/validator-yup';
    import * as yup from 'yup';
    import { Alert, Input, Textarea, Select, Button, Label, InputAddon, ButtonGroup, Heading, Card } from 'flowbite-svelte';
    import { UserCircleSolid } from 'flowbite-svelte-icons';
    import * as m from '$lib/paraglide/messages.js';
    import { onlyLatinChars } from '$lib/utils.js';

    const schema = yup.object({
        email: yup.string().email().required(m.validation_emailRequired()),
        password: yup.string().required(m.validation_passwordRequired()).min(8, m.validation_passwordMinLength()),
        confirm_password: yup.string().required(m.validation_confirmPasswordRequired()).oneOf([yup.ref('password'), null], m.validation_passwordsMismatch()),
        first_name: yup.string().required(m.validation_firstNameRequired()).test('latin-only', m.eventRegister_validationNoKorean(), onlyLatinChars),
        last_name: yup.string().required(m.validation_lastNameRequired()).test('latin-only', m.eventRegister_validationNoKorean(), onlyLatinChars),
        middle_initial: yup.string().max(1).test('latin-only', m.eventRegister_validationNoKorean(), onlyLatinChars),
        korean_name: yup.string(),
        nationality: yup.string().required(m.validation_nationalityRequired()),
        job_title: yup.string().required(m.validation_jobTitleRequired()),
        department: yup.string(),
        institute: yup.mixed().transform((value, originalValue) => {
            // If it's already a number, return it
            if (typeof originalValue === 'number') return originalValue;
            // If it's an empty string, return undefined to trigger required validation
            if (originalValue === '' || originalValue === null || originalValue === undefined) return undefined;
            // Otherwise convert to number
            const num = Number(originalValue);
            return isNaN(num) ? undefined : num;
        }).required(m.validation_instituteRequired()),
        disability: yup.string(),
        dietary: yup.string(),
    });

    let form_config = $derived({
        next: page_data.next,
        show_english_name: true,
        show_korean_name: true,
        allow_korean_institute: true,
    });

    const { form: felteForm, data, errors, isSubmitting } = createForm({
        initialValues: {
            email: '',
            password: '',
            confirm_password: '',
            first_name: '',
            last_name: '',
            middle_initial: '',
            korean_name: '',
            nationality: '1',
            job_title: '',
            department: '',
            institute: '',
            disability: '',
            dietary: '',
        },
        onSubmit: async (data) => {
            delete data.confirm_password;
            data.username = data.email;
            const response = await fetch('?/register',
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
        },
        extend: validator({ schema }),
        onError: (errors) => {
            if (errors.redirect) {
                goto(`/verify-email?next=${page_data.next}`);
            } else {
                window.scrollTo(0, 0);
            }
            return errors;
        }
    });
</script>

<!-- Page Header Card -->
<div class="relative rounded-lg shadow-sm py-16 px-8 mb-8 overflow-hidden" style="background-image: url('/bg-events.webp'); background-size: cover; background-position: center;">
    <div class="absolute inset-0 bg-slate-900 opacity-60"></div>
    <div class="relative z-10">
        <h1 class="text-3xl font-bold text-white">{m.registration_title()}</h1>
        <p class="text-slate-200 mt-2">{m.registration_description()}</p>
    </div>
</div>

<!-- Form Card -->
<div class="bg-white border border-gray-200 rounded-lg shadow-sm p-8">
    <form use:felteForm method="post">
        <RegistrationForm data={$data} errors={$errors} config={form_config} />
        <div class="flex flex-col md:flex-row justify-center gap-4 mt-8">
            <Button type="submit" size="lg" color="primary" disabled={$isSubmitting}>
                {m.registration_submit()}
            </Button>
        </div>
    </form>
</div>