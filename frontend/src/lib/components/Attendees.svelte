<script>
    import { TableSearch, TableHead, TableHeadCell, TableBody, TableBodyRow, TableBodyCell, Checkbox, Button } from 'flowbite-svelte';
    import { Modal, Heading, Textarea, Select, Label, Card, Input } from 'flowbite-svelte';
    import { Alert } from 'flowbite-svelte';
    import { enhance } from '$app/forms';
    import { UserAddSolid, UserEditSolid, UserRemoveSolid, TextSizeOutline, TagOutline } from 'flowbite-svelte-icons';
    import { jsPDF } from "jspdf";

    import RegistrationForm from './RegistrationForm.svelte';

    let { data } = $props();

    function sortAttendeesById(a, b) {
        return a.id - b.id;
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
                name: item.name,
                first_name: item.first_name,
                middle_initial: item.middle_initial,
                last_name: item.last_name,
                email: item.user.email,
                nationality: item.nationality,
                institute: item.institute,
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
        const csv = [
            [   "ID",
                "First Name",
                "Middle Initial",
                "Last Name",
                "Email",
                "Nationality",
                "Institute",
                "Department",
                "Job Title",
                "Disability",
                "Dietary",
                ...custom_headers_attendees.map(q => q.replace(/\n/, ' ').replace(/\s+/g, ' '))],
            ...table_data_attendees.map(row => [
                row.id,
                row.first_name,
                row.middle_initial,
                row.last_name,
                row.email,
                stringify_nationality(row.nationality),
                row.institute,
                row.department,
                row.job_title,
                row.disability,
                row.dietary,
                ...row.custom_answers.map(answer => answer ? answer.answer.replace(/^- /, '').replace(/\n- /g, '; ') : "")
            ])
        ].map(row => row.map(item => `"${item}"`).join(',')).join('\n');
        
        const blob = new Blob([csv], { type: 'text/csv' });
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
    let filteredAttendees = $state([]);
    let selectedAttendees = $state([]);
    $effect(() => {
        filteredAttendees = table_data_attendees.filter((item) => item.name.toLowerCase().includes(searchTermAttendee.toLowerCase()))
    });

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
            message_custom_answer_changes = { type: 'error', message: 'Please select a reference question for each answer.' };
            cancel();
            return;
        }
        if (formData.getAll('answer_question[]').length !== custom_answers.length) {
            message_custom_answer_changes = { type: 'error', message: 'Please enter a question for each answer.' };
            cancel();
            return;
        }
        if (formData.getAll('answer_answer[]').length !== custom_answers.length) {
            message_custom_answer_changes = { type: 'error', message: 'Please enter an answer for each question.' };
            cancel();
            return;
        }
        return async ({ result, action, update }) => {
            if (result.type === 'success') {
                await update({ reset: false });
                message_custom_answer_changes = { type: 'success', message: 'Successfully updated custom answers.' };
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
                message_default_answer_changes = { type: 'success', message: 'Successfully updated attendee information.' };
            } else {
                message_default_answer_changes = { type: 'error', message: 'Failed to update attendee information.' };
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
        if (value === 1) {
            return 'Korean';
        } else if (value === 2) {
            return 'Non-Korean';
        }
        return 'Not Specified';
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
                message_send_email = { type: 'error', message: 'Failed to send emails.' };
            }
        };
    };

    let nametag_modal = $state(false);
    let selected_nametag = $state({});
    let role = $state('Participant'); // Default role for nametag
    const showNametagModal = async (id) => {
        const doc = new jsPDF({
            orientation: "portrait",
            unit: "mm",
            format: [90, 100]
        });
        let p = table_data_attendees.find(a => a.id === id);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(10);
        doc.text(`${p.id}`, 45, 10, 'center');
        doc.setFontSize(30);
        let splitName = doc.splitTextToSize(p.name, 80);
        doc.text(splitName, 45, 45 - (splitName.length - 1) * 12, 'center');
        doc.setFontSize(20);
        let splitInstitute = doc.splitTextToSize(p.institute, 80);
        doc.text(splitInstitute, 45, 55, 'center');
        doc.setFontSize(23);
        doc.setLineWidth(1);
        doc.line(5, 82, 85, 82);
        doc.text(role, 45, 93, 'center');
        selected_nametag = doc.output('bloburi');
        nametag_modal = true;
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

<Heading tag="h2" customSize="text-xl font-bold" class="mb-3">Attendees</Heading>
<p class="font-light mb-6">Below is the list of attendees for this event.</p>
<div class="flex justify-end sm:flex-row flex-col">
    <div class="flex items-center gap-2">
        <Button color="primary" size="sm" onclick={showSendEmailModal} disabled={selectedAttendees.length === 0}>Send Emails to Selected Attendees</Button>
        <Button color="primary" size="sm" onclick={() => expand_attendees = !expand_attendees}>{expand_attendees ?  "Collapse" : "Expand"} Headers</Button>
        <Button color="primary" size="sm" onclick={exportAttendeesAsCSV}>Export All Data as CSV</Button>
    </div>
</div>
<p class="mt-5 mb-3 text-sm text-right">{table_data_attendees.length} people registered to this event.</p>
<Input type="text" placeholder="Role" bind:value={role} class="mb-6" /><br>
<TableSearch placeholder="Search by First Name" hoverable={true} bind:inputValue={searchTermAttendee}>
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
        <TableHeadCell>ID</TableHeadCell>
        <TableHeadCell>Name</TableHeadCell>
        <TableHeadCell>Email</TableHeadCell>
        <TableHeadCell>Nationality</TableHeadCell>
        <TableHeadCell>Institute</TableHeadCell>
        {#if expand_attendees}
            <TableHeadCell>Department</TableHeadCell>
            <TableHeadCell>Job Title</TableHeadCell>
            <TableHeadCell>Disability</TableHeadCell>
            <TableHeadCell>Dietary</TableHeadCell>
            {#each custom_headers_attendees as header}
                <TableHeadCell>{@render process_spaces(header)}</TableHeadCell>
            {/each}
        {/if}
        <TableHeadCell class="w-1">Actions</TableHeadCell>
    </TableHead>
    <TableBody tableBodyClass="divide-y">
        {#each filteredAttendees as row}
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
                    expand_attendees ? custom_headers_attendees.length + 10 : 6
                } class="text-center">No records</TableBodyCell>
            </TableBodyRow>
        {/if}
    </TableBody>
</TableSearch>


<Modal id="attendee_modal" size="xl" title="Attendee Details" bind:open={attendee_modal} outsideclose>
    <form method="post" action="?/update_attendee" use:enhance={afterSuccessfulSubmitDefaultAnswerChanges}>
        <input type="hidden" name="id" value={table_data_attendees[selected_idx].id} />
        <Heading tag="h2" customSize="text-lg font-bold" class="pt-3 mb-6">Basic Information</Heading>
        <RegistrationForm data={table_data_attendees[selected_idx]} config={form_config} />
        {#if message_default_answer_changes.type === 'success'}
            <Alert type="success" color="green">{message_default_answer_changes.message}</Alert>
        {:else if message_default_answer_changes.type === 'error'}
            <Alert type="error" color="red">{message_default_answer_changes.message}</Alert>
        {/if}
        <div class="flex justify-center mt-6">
            <Button color="primary" type="submit">Update Attendee Information</Button>
        </div>
    </form>
    <Heading tag="h2" customSize="text-lg font-bold" class="pt-3 mb-6">Answers to the Event Specific Questions</Heading>
    <form method="post" action="?/update_answers" use:enhance={afterSuccessfulSubmitCustomAnswerChanges}>
        <div class="flex justify-center gap-2 mb-6">
            <Button color="primary" onclick={resetCustomAnswerChanges}>Reset Changes</Button>
            <Button type="submit" color="primary">Apply Changes</Button>
        </div>
        <input type="hidden" name="attendee_id" value={table_data_attendees[selected_idx].id} />
        {#if custom_answers.length > 0}
            {#each custom_answers as answer, idx}
                <Card size="none" class="mb-6">
                    <div class="mb-6">
                        <Label for={`answer_reference_id_${idx}`} class="block mb-2">Reference Question</Label>
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
                        <Label for={`answer_question_${idx}`} class="block mb-2">Question</Label>
                        <Textarea class="mb-2" id={`answer_question_${idx}`} name="answer_question[]" bind:value={answer.question} readonly={answer.reference.question !== ""} />
                    </div>
                    <div class="mb-6">
                        <Label for={`answer_answer_${idx}`} class="block mb-2">Answer</Label>
                        <Textarea id={`answer_answer_${idx}`} name="answer_answer[]" bind:value={answer.answer} />
                    </div>
                    <div class="flex justify-center gap-2">
                        <Button color="red" onclick={
                            () => custom_answers = custom_answers.filter((a, i) => i !== idx)
                        }>Delete Answer</Button>
                    </div>
                </Card>
            {/each}
        {:else}
            <p class="text-center mb-6">This attendee has not answered any event specific questions.</p>
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
            <Button color="primary" onclick={resetCustomAnswerChanges}>Reset Changes</Button>
            <Button type="submit" color="primary">Apply Changes</Button>
        </div>
    </form>
</Modal>

<Modal id="remove_attendee_modal" size="sm" title="Are you sure?" bind:open={remove_attendee_modal} outsideclose>
    <form method="post" action="?/deregister_attendee" use:enhance={afterSuccessfulDeregistration}>
        <input type="hidden" name="id" value={table_data_attendees[selected_idx].id} />
        <p class="font-light mb-6">Are you sure you want to deregister this attendee?</p>
        <div class="flex justify-center gap-2">
            <Button color="red" type="submit">Deresigister</Button>
            <Button color="dark" onclick={() => remove_attendee_modal = false}>Cancel</Button>
        </div>
    </form>
</Modal>

<Modal id="send_email_modal" size="lg" title="Send Emails" bind:open={send_email_modal} outsideclose>
    <form method="post" action="?/send_emails" use:enhance={afterSuccessfulSendEmails}>
        <div class="mb-6">
            <Label for="to" class="block mb-2 text-black">To</Label>
            <Input id="to" name="to" type="text" value={selectedAttendees.map(id => table_data_attendees.find(a => a.id === id).email).join("; ")} readonly />
        </div>
        <div class="mb-6">
            <Label for="subject" class="block mb-2">Subject</Label>
            <Input id="subject" name="subject" type="text" />
        </div>
        <div class="mb-6">
            <Label for="body" class="block mb-2">Message</Label>
            <Textarea id="body" name="body" rows="10" />
        </div>
        {#if message_send_email.type === 'error'}
            <Alert type="error" color="red" class="mb-6">{message_send_email.message}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="primary" type="submit">Send Emails</Button>
        </div>
    </form>
</Modal>

<Modal id="nametag_modal" size="lg" title="Nametag" bind:open={nametag_modal} outsideclose>
    <iframe id="nametag" class="w-full h-[500px]" src={selected_nametag} title="Nametag">
        Your browser does not support iframes.
    </iframe>
    <div class="flex justify-center mt-6 gap-2">
        <Button color="primary" onclick={() => {
            const iframe = document.getElementById('nametag');
            if (iframe) {
                iframe.contentWindow.print();
            }
        }}>Print</Button>
        <Button color="dark" onclick={() => nametag_modal = false}>Close</Button>
    </div>
</Modal>