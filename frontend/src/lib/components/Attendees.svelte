<script>
    import { TableSearch, TableHead, TableHeadCell, TableBody, TableBodyRow, TableBodyCell, Checkbox, Button } from 'flowbite-svelte';
    import { Modal, Heading, Textarea, Select, Label, Card, Input } from 'flowbite-svelte';
    import { Alert } from 'flowbite-svelte';
    import { enhance } from '$app/forms';
    import { UserEditSolid, UserRemoveSolid, TagOutline, AwardOutline } from 'flowbite-svelte-icons';
    import * as m from '$lib/paraglide/messages.js';
    import { languageTag } from '$lib/paraglide/runtime.js';
    import { generateNametagPDF, generateCertificatePDF, loadKoreanFonts } from '$lib/pdfUtils.js';

    import RegistrationForm from './RegistrationForm.svelte';
    import TablePagination from '$lib/components/TablePagination.svelte';

    let { data } = $props();

    // Preload fonts on component mount
    $effect(() => {
        loadKoreanFonts();
    });

    function sortAttendeesById(a, b) {
        return a.id - b.id;
    }

    function getDisplayName(item) {
        // Display name based on UI language
        const currentLang = languageTag();
        if (currentLang === 'ko') {
            // If UI is Korean, prefer Korean name
            return item.korean_name || item.name;
        }
        // If UI is English or default, show English name
        return item.name;
    }

    function getDisplayInstitute(item) {
        // Display institute based on UI language
        const currentLang = languageTag();
        if (currentLang === 'ko' && item.institute_ko) {
            return item.institute_ko;
        }
        return item.institute;
    }

    function transformToTableFormat(attendees) {
        // Extract all unique questions object
        attendees.sort(sortAttendeesById);
        let unique_questions = new Set();
        data.questions.forEach(item => {
            unique_questions.add(item.question.question);
        });
        attendees.forEach(item => {
            item.custom_answers.forEach(answerObj => {
                unique_questions.add(answerObj.question);
            });
        });
        const custom_headers = [...unique_questions];

        // Create table_data rows
        const table_data = attendees.map((item, idx) => {
            // Create a row with empty strings for each question
            const row = {
                id: item.id,
                name: getDisplayName(item),
                first_name: item.first_name,
                middle_initial: item.middle_initial,
                last_name: item.last_name,
                korean_name: item.korean_name,
                email: item.user.email,
                nationality: item.nationality.toString(),
                institute: getDisplayInstitute(item),
                institute_en: item.institute,
                institute_ko: item.institute_ko,
                department: item.department,
                job_title: item.job_title,
                disability: item.disability,
                dietary: item.dietary,
                custom_answers: []
            }

            // Fill in the answers for each question
            custom_headers.forEach(question => {
                const answerObj = item.custom_answers.find(answer => answer.question === question);
                if (answerObj) {
                    row.custom_answers.push(answerObj);
                } else {
                    let empty_answer = {
                        id: undefined,
                        reference: data.questions.find(q => q.question.question === question),
                        question: question,
                        answer: ''
                    }
                    row.custom_answers.push(empty_answer);
                }
            });

            return row;
        });

        return {
            custom_headers,
            table_data
        };
    }

    const exportAttendeesAsCSV = () => {
        const currentLang = languageTag();
        const isKorean = currentLang === 'ko';

        // Build headers based on UI language
        const headers = [
            m.attendees_id(),
            ...(isKorean ? [m.attendees_koreanName()] : [m.attendees_firstName(), m.attendees_middleInitial(), m.attendees_lastName()]),
            m.attendees_email(),
            m.attendees_nationality(),
            m.attendees_institute(),
            m.attendees_department(),
            m.attendees_jobTitle(),
            m.attendees_disability(),
            m.attendees_dietary(),
            ...custom_headers_attendees.map(q => q.replace(/\n/, ' ').replace(/\s+/g, ' '))
        ];

        // Build data rows based on UI language
        const dataRows = table_data_attendees.map(row => [
            row.id,
            ...(isKorean ? [row.korean_name || row.name] : [row.first_name, row.middle_initial, row.last_name]),
            row.email,
            stringify_nationality(row.nationality),
            row.institute,
            row.department,
            row.job_title,
            row.disability,
            row.dietary,
            ...row.custom_answers.map(answer => answer ? answer.answer.replace(/^- /, '').replace(/\n- /g, '; ') : "")
        ]);

        const csv = [headers, ...dataRows].map(row => row.join('\t')).join('\r\n');

        // Convert to UTF-16 LE with BOM for Excel compatibility
        const BOM = '\uFEFF';
        const csvWithBOM = BOM + csv;

        // Encode to UTF-16 LE
        const buffer = new ArrayBuffer(csvWithBOM.length * 2);
        const view = new Uint16Array(buffer);
        for (let i = 0; i < csvWithBOM.length; i++) {
            view[i] = csvWithBOM.charCodeAt(i);
        }

        const blob = new Blob([buffer], { type: 'text/csv;charset=utf-16le;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        // Get current timestamp in YYYY-MM-DD_HH-MM-SS format
        const timestamp = new Date().toISOString().replace(/T/, '_').replace(/\..+/, '').replace(/:/g, '-');
        a.href = url;
        a.download = `attendees_${timestamp}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    let searchTermAttendee = $state('');
    let selectedAttendees = $state([]);
    let currentPage = $state(1);
    const itemsPerPage = 10;

    let filteredAttendees = $derived(
        table_data_attendees.filter((item) => item.name.toLowerCase().includes(searchTermAttendee.toLowerCase()))
    );

    // Reset to page 1 when search changes
    $effect(() => {
        searchTermAttendee;
        currentPage = 1;
    });

    let totalPages = $derived(Math.ceil(filteredAttendees.length / itemsPerPage));
    let paginatedAttendees = $derived(
        filteredAttendees.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
    );

    function handlePageChange(page) {
        currentPage = page;
    }

    let attendee_modal = $state(false);
    let remove_attendee_modal = $state(false);

    let selected_idx = $state(null);
    const showAttenteeModal = (id) => {
        selected_idx = table_data_attendees.findIndex(item => item.id === id);
        resetCustomAnswerChanges();
        message_custom_answer_changes = {};
        message_default_answer_changes = {};
        attendee_modal = true;
    };

    const showRemoveAttenteeModal = (id) => {
        selected_idx = table_data_attendees.findIndex(item => item.id === id);
        remove_attendee_modal = true;
    };

    let expand_attendees = $state(false);


    let custom_answers = $state([]);
    const addNewCustomAnswer = () => {
        custom_answers = [...custom_answers, {
            id: undefined,
            reference: {
                id: undefined,
                question: ''
            },
            question: '',
            answer: ''
        }];
    };

    const resetCustomAnswerChanges = () => {
        if (selected_idx === null) {
            return;
        }
        custom_answers = table_data_attendees[selected_idx].custom_answers.map(a => {
            return a?{
                id: a.id,
                reference: a.reference,
                question: a.question,
                answer: a.answer
            }:{
                id: -1,
                reference: null,
                question: '',
                answer: ''
            };
        });
    };

    let message_custom_answer_changes = $state({});
    const afterSuccessfulSubmitCustomAnswerChanges = ({ formData, cancel }) => {
        if (formData.getAll('answer_reference_id[]').length !== custom_answers.length) {
            message_custom_answer_changes = { type: 'error', message: m.attendees_errorSelectReference() };
            cancel();
            return;
        }
        if (formData.getAll('answer_question[]').length !== custom_answers.length) {
            message_custom_answer_changes = { type: 'error', message: m.attendees_errorEnterQuestion() };
            cancel();
            return;
        }
        if (formData.getAll('answer_answer[]').length !== custom_answers.length) {
            message_custom_answer_changes = { type: 'error', message: m.attendees_errorEnterAnswer() };
            cancel();
            return;
        }
        return async ({ result, action, update }) => {
            if (result.type === 'success') {
                await update({ reset: false });
                message_custom_answer_changes = { type: 'success', message: m.attendees_successCustomAnswers() };
            } else {
                message_custom_answer_changes = { type: 'error', message: result.error.message };
            }
            // scroll attendee_modal to bottom
            const modalContent = document.querySelector('#attendee_modal [role="document"]');
            if (modalContent) {
                modalContent.scrollTo({ top: modalContent.scrollHeight, behavior: 'smooth' });
            }
        };
    };

    let message_default_answer_changes = $state({});
    const afterSuccessfulSubmitDefaultAnswerChanges = () => {
        return async ({ result, action, update }) => {
            if (result.type === 'success') {
                await update({ reset: false });
                message_default_answer_changes = { type: 'success', message: m.attendees_successUpdate() };
            } else {
                message_default_answer_changes = { type: 'error', message: m.attendees_errorUpdate() };
            }
        };
    };

    const afterSuccessfulDeregistration = () => {
        return async ({ result, action, update }) => {
            if (result.type === 'success') {
                await update({ reset: false });
            }
            remove_attendee_modal = false;
        };
    };

    let form_config = {
        hide_login_info: true,
    };

    const stringify_nationality = (value) => {
        if (value === '1') {
            return m.nationality_korean();
        } else if (value === '2') {
            return m.nationality_nonKorean();
        }
        return m.nationality_notSpecified();
    };

    let send_email_modal = $state(false);
    const showSendEmailModal = () => {
        send_email_modal = true;
    };

    let message_send_email = $state({});
    const afterSuccessfulSendEmails = () => {
        return async ({ result, action, update }) => {
            if (result.type === 'success') {
                await update({ reset: false });
                send_email_modal = false;
                message_send_email = {}
            } else {
                message_send_email = { type: 'error', message: m.attendees_sendEmailError() };
            }
        };
    };

    let nametag_modal = $state(false);
    let selected_nametag = $state('');
    let selected_nametag_id = $state(null);
    let selected_role = $state('Participant');

    const generateNametag = async (id, role) => {
        const p = table_data_attendees.find(a => a.id === id);
        selected_nametag = await generateNametagPDF({
            name: p.name,
            institute: p.institute,
            role,
            id: p.id
        });
    };

    const showNametagModal = async (id) => {
        selected_nametag_id = id;
        selected_role = 'Participant';
        await generateNametag(id, selected_role);
        nametag_modal = true;
    };

    const onRoleChange = async (e) => {
        await generateNametag(selected_nametag_id, e.target.value);
    };

    let cert_modal = $state(false);
    let selected_cert = $state('');
    let cert_email = $state('');
    let cert_sending = $state(false);
    let cert_message = $state({});
    let selected_cert_attendee_id = $state(null);

    // Bulk certificate sending
    let bulk_cert_sending = $state(false);
    let bulk_cert_message = $state({});

    const sendCertificatesToSelected = async () => {
        if (selectedAttendees.length === 0 || bulk_cert_sending) return;
        bulk_cert_sending = true;
        bulk_cert_message = {};
        try {
            for (const id of selectedAttendees) {
                const p = table_data_attendees.find(a => a.id === id);
                if (!p.email) continue;
                const pdfDataUri = await generateCertificatePDF({
                    attendee: { name: p.name, institute: p.institute },
                    event: data.event,
                    messages: {
                        certIssueDate: m.attendees_certIssueDate,
                        certTitle: m.attendees_certTitle,
                        certName: m.attendees_certName,
                        certInstitute: m.attendees_certInstitute,
                        certHasAttended: m.attendees_certHasAttended,
                        certOn: m.attendees_certOn,
                        certHeldAt: m.attendees_certHeldAt,
                        certAsParticipant: m.attendees_certAsParticipant,
                        certFooter: m.attendees_certFooter
                    },
                    outputFormat: 'datauristring'
                });
                const base64Pdf = pdfDataUri.split(',')[1];
                const formData = new FormData();
                formData.append('email', p.email);
                formData.append('pdf_base64', base64Pdf);
                formData.append('attendee_id', id);
                formData.append('attendee_type', 'attendee');
                await fetch('?/send_certificate', {
                    method: 'POST',
                    body: formData
                });
            }
            bulk_cert_message = { type: 'success', message: m.attendees_sendCertificatesComplete() };
        } catch (error) {
            bulk_cert_message = { type: 'error', message: m.attendees_sendCertificateError() };
        } finally {
            bulk_cert_sending = false;
        }
    };

    const showCertificateModal = async (id) => {
        const p = table_data_attendees.find(a => a.id === id);
        selected_cert_attendee_id = id;
        cert_email = p.email;
        cert_message = {};
        selected_cert = await generateCertificatePDF({
            attendee: { name: p.name, institute: p.institute },
            event: data.event,
            messages: {
                certIssueDate: m.attendees_certIssueDate,
                certTitle: m.attendees_certTitle,
                certName: m.attendees_certName,
                certInstitute: m.attendees_certInstitute,
                certHasAttended: m.attendees_certHasAttended,
                certOn: m.attendees_certOn,
                certHeldAt: m.attendees_certHeldAt,
                certAsParticipant: m.attendees_certAsParticipant,
                certFooter: m.attendees_certFooter
            }
        });
        cert_modal = true;
    };

    const sendCertificate = async () => {
        if (!cert_email || cert_sending) return;
        cert_sending = true;
        cert_message = {};
        try {
            const p = table_data_attendees.find(a => a.id === selected_cert_attendee_id);
            const pdfDataUri = await generateCertificatePDF({
                attendee: { name: p.name, institute: p.institute },
                event: data.event,
                messages: {
                    certIssueDate: m.attendees_certIssueDate,
                    certTitle: m.attendees_certTitle,
                    certName: m.attendees_certName,
                    certInstitute: m.attendees_certInstitute,
                    certHasAttended: m.attendees_certHasAttended,
                    certOn: m.attendees_certOn,
                    certHeldAt: m.attendees_certHeldAt,
                    certAsParticipant: m.attendees_certAsParticipant,
                    certFooter: m.attendees_certFooter
                },
                outputFormat: 'datauristring'
            });
            // Extract base64 from data URI (format: data:application/pdf;filename=generated.pdf;base64,...)
            const base64Pdf = pdfDataUri.split(',')[1];
            const formData = new FormData();
            formData.append('email', cert_email);
            formData.append('pdf_base64', base64Pdf);
            formData.append('attendee_id', selected_cert_attendee_id);
            formData.append('attendee_type', 'attendee');
            const response = await fetch('?/send_certificate', {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                cert_message = { type: 'success', message: m.attendees_sendCertificateSuccess() };
            } else {
                cert_message = { type: 'error', message: m.attendees_sendCertificateError() };
            }
        } catch (error) {
            cert_message = { type: 'error', message: m.attendees_sendCertificateError() };
        } finally {
            cert_sending = false;
        }
    };

    let custom_headers_attendees = $state([]);
    let table_data_attendees = $state([]);
    $effect.pre(() => {
        let df = transformToTableFormat(data.attendees);
        custom_headers_attendees = df.custom_headers;
        table_data_attendees = df.table_data;
    });
</script>

{#snippet process_spaces(text)}
    {@html text.replace(/\n/g, '<br>').replace(/ /g, '&nbsp;')}
{/snippet}

<Heading tag="h2" class="text-xl font-bold mb-3">{m.attendees_title()}</Heading>
<p class="font-light mb-6">{m.attendees_description()}</p>
<div class="flex justify-end sm:flex-row flex-col">
    <div class="flex items-center gap-2 flex-wrap">
        <Button color="primary" size="sm" onclick={showSendEmailModal} disabled={selectedAttendees.length === 0}>{m.attendees_sendEmailToSelected()}</Button>
        <Button color="primary" size="sm" onclick={sendCertificatesToSelected} disabled={selectedAttendees.length === 0 || bulk_cert_sending}>
            {bulk_cert_sending ? m.attendees_sendingCertificates() : m.attendees_sendCertificatesToSelected()}
        </Button>
        <Button color="primary" size="sm" onclick={() => expand_attendees = !expand_attendees}>{expand_attendees ? m.attendees_collapseHeaders() : m.attendees_expandHeaders()}</Button>
        <Button color="primary" size="sm" onclick={exportAttendeesAsCSV}>{m.attendees_exportCSV()}</Button>
    </div>
</div>
{#if bulk_cert_message.type === 'success'}
    <Alert type="success" color="green" class="mt-3">{bulk_cert_message.message}</Alert>
{:else if bulk_cert_message.type === 'error'}
    <Alert type="error" color="red" class="mt-3">{bulk_cert_message.message}</Alert>
{/if}
<p class="mt-5 mb-3 text-sm text-right">{table_data_attendees.length} {m.attendees_peopleRegistered()}</p>
<TableSearch placeholder={m.attendees_searchPlaceholder()} hoverable={true} bind:inputValue={searchTermAttendee}>
    <TableHead>
        <TableHeadCell class="w-1">
            <Checkbox
                checked={selectedAttendees.length > 0 && selectedAttendees.length === data.attendees.length}
                intermediate={
                    selectedAttendees.length > 0 && (selectedAttendees.length < data.attendees.length)
                }
                onclick={(e) => {
                    if (e.target.checked) {
                        selectedAttendees = filteredAttendees.map(a => a.id);
                    } else {
                        selectedAttendees = [];
                    }
                }}
            />
        </TableHeadCell>
        <TableHeadCell>{m.attendees_id()}</TableHeadCell>
        <TableHeadCell>{m.attendees_name()}</TableHeadCell>
        <TableHeadCell>{m.attendees_email()}</TableHeadCell>
        <TableHeadCell>{m.attendees_nationality()}</TableHeadCell>
        <TableHeadCell>{m.attendees_institute()}</TableHeadCell>
        {#if expand_attendees}
            <TableHeadCell>{m.attendees_koreanName()}</TableHeadCell>
            <TableHeadCell>{m.attendees_department()}</TableHeadCell>
            <TableHeadCell>{m.attendees_jobTitle()}</TableHeadCell>
            <TableHeadCell>{m.attendees_disability()}</TableHeadCell>
            <TableHeadCell>{m.attendees_dietary()}</TableHeadCell>
            {#each custom_headers_attendees as header}
                <TableHeadCell>{@render process_spaces(header)}</TableHeadCell>
            {/each}
        {/if}
        <TableHeadCell class="w-1">{m.attendees_actions()}</TableHeadCell>
    </TableHead>
    <TableBody tableBodyClass="divide-y">
        {#each paginatedAttendees as row}
            <TableBodyRow>
                <TableBodyCell><Checkbox checked={selectedAttendees.includes(row.id)} onclick={(e) => {
                    if (e.target.checked) {
                        selectedAttendees = [...selectedAttendees, row.id];
                    } else {
                        selectedAttendees = selectedAttendees.filter(a => a !== row.id);
                    }
                }} /></TableBodyCell>
                <TableBodyCell>{row.id}</TableBodyCell>
                <TableBodyCell>{row.name}</TableBodyCell>
                <TableBodyCell>{row.email}</TableBodyCell>
                <TableBodyCell>{stringify_nationality(row.nationality)}</TableBodyCell>
                <TableBodyCell>{row.institute}</TableBodyCell>
                {#if expand_attendees}
                    <TableBodyCell>{row.korean_name}</TableBodyCell>
                    <TableBodyCell>{row.department}</TableBodyCell>
                    <TableBodyCell>{row.job_title}</TableBodyCell>
                    <TableBodyCell>{row.disability}</TableBodyCell>
                    <TableBodyCell>{row.dietary}</TableBodyCell>
                    {#each row.custom_answers as a}
                        <TableBodyCell>{@render process_spaces(a?a.answer:"")}</TableBodyCell>
                    {/each}
                {/if}
                <TableBodyCell>
                    <div class="flex justify-center gap-2">
                        <Button color="none" size="none" onclick={() => showNametagModal(row.id)}>
                            <TagOutline class="w-5 h-5" />
                        </Button>
                        <Button color="none" size="none" onclick={() => showCertificateModal(row.id)}>
                            <AwardOutline class="w-5 h-5" />
                        </Button>
                        <Button color="none" size="none" onclick={() => showAttenteeModal(row.id)}>
                            <UserEditSolid class="w-5 h-5" />
                        </Button>
                        <Button color="none" size="none" onclick={() => showRemoveAttenteeModal(row.id)}>
                            <UserRemoveSolid class="w-5 h-5" />
                        </Button>
                    </div>
                </TableBodyCell>
            </TableBodyRow>
        {/each}
        {#if filteredAttendees.length === 0}
            <TableBodyRow>
                <TableBodyCell colspan={
                    expand_attendees ? custom_headers_attendees.length + 11 : 6
                } class="text-center">{m.attendees_noRecords()}</TableBodyCell>
            </TableBodyRow>
        {/if}
    </TableBody>
</TableSearch>

<TablePagination {currentPage} {totalPages} onPageChange={handlePageChange} />

<Modal id="attendee_modal" size="xl" title={m.attendees_detailsTitle()} bind:open={attendee_modal} outsideclose>
    <form method="post" action="?/update_attendee" use:enhance={afterSuccessfulSubmitDefaultAnswerChanges}>
        <input type="hidden" name="id" value={table_data_attendees[selected_idx].id} />
        <Heading tag="h2" class="text-lg font-bold pt-3 mb-6">{m.attendees_basicInformation()}</Heading>
        <RegistrationForm data={table_data_attendees[selected_idx]} config={form_config} />
        {#if message_default_answer_changes.type === 'success'}
            <Alert type="success" color="green">{message_default_answer_changes.message}</Alert>
        {:else if message_default_answer_changes.type === 'error'}
            <Alert type="error" color="red">{message_default_answer_changes.message}</Alert>
        {/if}
        <div class="flex justify-center mt-6">
            <Button color="primary" type="submit">{m.attendees_updateAttendee()}</Button>
        </div>
    </form>
    <Heading tag="h2" class="text-lg font-bold pt-3 mb-6">{m.attendees_answersTitle()}</Heading>
    <form method="post" action="?/update_answers" use:enhance={afterSuccessfulSubmitCustomAnswerChanges}>
        <div class="flex justify-center gap-2 mb-6">
            <Button color="primary" onclick={resetCustomAnswerChanges}>{m.attendees_resetChanges()}</Button>
            <Button type="submit" color="primary">{m.attendees_applyChanges()}</Button>
        </div>
        <input type="hidden" name="attendee_id" value={table_data_attendees[selected_idx].id} />
        {#if custom_answers.length > 0}
            {#each custom_answers as answer, idx}
                <Card size="xl" class="mb-6">
                    <div class="mb-6">
                        <Label for={`answer_reference_id_${idx}`} class="block mb-2">{m.attendees_referenceQuestion()}</Label>
                        <Select id={`answer_reference_id_${idx}`} name="answer_reference_id[]" items={data.questions.map(q => ({
                            value: q.id,
                            name: q.question.question
                        }))} onchange={(e) => {
                            const q_id = parseInt(e.target.value);
                            const q = data.questions.find(q => q.id === q_id);
                            custom_answers[idx].reference = q;
                            custom_answers[idx].question = q.question.question;
                        }} value={answer.reference.id} />
                    </div>
                    <div class="mb-6">
                        <Label for={`answer_question_${idx}`} class="block mb-2">{m.attendees_question()}</Label>
                        <Textarea class="mb-2 w-full" id={`answer_question_${idx}`} name="answer_question[]" bind:value={answer.question} readonly={answer.reference.question !== ""} />
                    </div>
                    <div class="mb-6">
                        <Label for={`answer_answer_${idx}`} class="block mb-2">{m.attendees_answer()}</Label>
                        <Textarea id={`answer_answer_${idx}`} name="answer_answer[]" bind:value={answer.answer} class="w-full" />
                    </div>
                    <div class="flex justify-center gap-2">
                        <Button color="red" onclick={
                            () => custom_answers = custom_answers.filter((a, i) => i !== idx)
                        }>{m.attendees_deleteAnswer()}</Button>
                    </div>
                </Card>
            {/each}
        {:else}
            <p class="text-center mb-6">{m.attendees_noAnswers()}</p>
        {/if}
        <div class="flex justify-center gap-2 mb-6">
            <Button color="dark" onclick={addNewCustomAnswer}>+</Button>
        </div>
        <div class="mb-6">
            {#if message_custom_answer_changes.type === 'success'}
                <Alert type="success" color="green">{message_custom_answer_changes.message}</Alert>
            {:else if message_custom_answer_changes.type === 'error'}
                <Alert type="error" color="red">{message_custom_answer_changes.message}</Alert>
            {/if}
        </div>
        <div class="flex justify-center gap-2">
            <Button color="primary" onclick={resetCustomAnswerChanges}>{m.attendees_resetChanges()}</Button>
            <Button type="submit" color="primary">{m.attendees_applyChanges()}</Button>
        </div>
    </form>
</Modal>

<Modal id="remove_attendee_modal" size="sm" title={m.attendees_removeTitle()} bind:open={remove_attendee_modal} outsideclose>
    <form method="post" action="?/deregister_attendee" use:enhance={afterSuccessfulDeregistration}>
        <input type="hidden" name="id" value={table_data_attendees[selected_idx].id} />
        <p class="font-light mb-6">{m.attendees_removeConfirm()}</p>
        <div class="flex justify-center gap-2">
            <Button color="red" type="submit">{m.attendees_deregister()}</Button>
            <Button color="dark" onclick={() => remove_attendee_modal = false}>{m.attendees_cancel()}</Button>
        </div>
    </form>
</Modal>

<Modal id="send_email_modal" size="lg" title={m.attendees_sendEmails()} bind:open={send_email_modal} outsideclose>
    <form method="post" action="?/send_emails" use:enhance={afterSuccessfulSendEmails}>
        <div class="mb-6">
            <Label for="to" class="block mb-2 text-black">{m.attendees_to()}</Label>
            <Input id="to" name="to" type="text" value={selectedAttendees.map(id => table_data_attendees.find(a => a.id === id).email).join("; ")} readonly />
        </div>
        <div class="mb-6">
            <Label for="subject" class="block mb-2">{m.attendees_subject()}</Label>
            <Input id="subject" name="subject" type="text" />
        </div>
        <div class="mb-6">
            <Label for="body" class="block mb-2">{m.attendees_message()}</Label>
            <Textarea id="body" name="body" rows="10" class="w-full" />
        </div>
        {#if message_send_email.type === 'error'}
            <Alert type="error" color="red" class="mb-6">{message_send_email.message}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="primary" type="submit">{m.attendees_sendEmails()}</Button>
        </div>
    </form>
</Modal>

<Modal id="nametag_modal" size="lg" title={m.attendees_nametag()} bind:open={nametag_modal} outsideclose>
    <div class="mb-4 flex gap-2 items-center">
        <Label for="role" class="whitespace-nowrap">Role:</Label>
        <Select id="role" bind:value={selected_role} onchange={onRoleChange} items={[
            { value: 'Participant', name: 'Participant' },
            { value: 'Speaker', name: 'Speaker' },
            { value: 'Organizer', name: 'Organizer' },
            { value: 'Staff', name: 'Staff' },
            { value: 'Volunteer', name: 'Volunteer' }
        ]} class="flex-1" />
    </div>
    <iframe id="nametag" class="w-full h-[500px]" src={selected_nametag} title={m.attendees_nametag()}>
        {m.attendees_iframeNotSupported()}
    </iframe>
    <div class="flex justify-center mt-6 gap-2">
        <Button color="primary" onclick={() => {
            const iframe = document.getElementById('nametag');
            if (iframe) {
                iframe.contentWindow.print();
            }
        }}>{m.attendees_print()}</Button>
        <Button color="dark" onclick={() => nametag_modal = false}>{m.attendees_close()}</Button>
    </div>
</Modal>

<Modal id="cert_modal" size="lg" title={m.attendees_certificate()} bind:open={cert_modal} outsideclose>
    <div class="mb-4 flex gap-2 items-center">
        <Input type="email" bind:value={cert_email} placeholder={m.attendees_emailPlaceholder()} class="flex-1" />
        <Button color="primary" onclick={sendCertificate} disabled={cert_sending || !cert_email}>
            {cert_sending ? '...' : m.attendees_sendCertificate()}
        </Button>
    </div>
    {#if cert_message.type === 'success'}
        <Alert type="success" color="green" class="mb-4">{cert_message.message}</Alert>
    {:else if cert_message.type === 'error'}
        <Alert type="error" color="red" class="mb-4">{cert_message.message}</Alert>
    {/if}
    <iframe id="cert" class="w-full h-[500px]" src={selected_cert} title={m.attendees_certificate()}>
        {m.attendees_iframeNotSupported()}
    </iframe>
    <div class="flex justify-center mt-6 gap-2">
        <Button color="primary" onclick={() => {
            const iframe = document.getElementById('cert');
            if (iframe) {
                iframe.contentWindow.print();
            }
        }}>{m.attendees_print()}</Button>
        <Button color="dark" onclick={() => cert_modal = false}>{m.attendees_close()}</Button>
    </div>
</Modal>
