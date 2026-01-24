<script>
    import { TableSearch, TableHead, TableHeadCell, TableBody, TableBodyRow, TableBodyCell, Checkbox, Button } from 'flowbite-svelte';
    import { Modal, Heading, Textarea, Select, Label, Card, Input } from 'flowbite-svelte';
    import { Alert } from 'flowbite-svelte';
    import { enhance } from '$app/forms';
    import { UserAddSolid, UserEditSolid, UserRemoveSolid, TextSizeOutline, TagOutline, AwardOutline } from 'flowbite-svelte-icons';
    import * as m from '$lib/paraglide/messages.js';

    import OnSiteRegistrationForm from './OnSiteRegistrationForm.svelte';
    import jsPDF from 'jspdf';

    let { data } = $props();

    function sortAttendeesById(a, b) {
        return a.id - b.id;
    }
    data.onsite_attendees.sort(sortAttendeesById);

    const exportAttendeesAsCSV = () => {
        const csv = [
            [   "ID",
                "First Name",
                "Middle Initial",
                "Last Name",
                "Institute",
                "Job Title"
            ],
            ...data.onsite_attendees.map(row => [
                row.id,
                row.first_name,
                row.middle_initial,
                row.last_name,
                row.institute,
                row.job_title
            ])
        ].map(row => row.map(item => `"${item}"`).join(',')).join('\n');

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        // Get current timestamp in YYYY-MM-DD_HH-MM-SS format
        const timestamp = new Date().toISOString().replace(/T/, '_').replace(/\..+/, '').replace(/:/g, '-');
        a.href = url;
        a.download = `onsite_attendees_${timestamp}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    let searchTermAttendee = $state('');
    let filteredAttendees = $state([]);
    let selectedAttendees = $state([]);
    $effect(() => {
        filteredAttendees = data.onsite_attendees.filter((item) => item.name.toLowerCase().includes(searchTermAttendee.toLowerCase()))
    });

    let attendee_modal = $state(false);
    let remove_attendee_modal = $state(false);

    let selected_idx = $state(null);
    const showAttenteeModal = (id) => {
        selected_idx = data.onsite_attendees.findIndex(item => item.id === id);
        attendee_modal = true;
    };

    const showRemoveAttenteeModal = (id) => {
        selected_idx = data.onsite_attendees.findIndex(item => item.id === id);
        remove_attendee_modal = true;
    };

    let message_update = $state({});
    const afterSuccessfulSubmit = () => {
        return async ({ result, action, update }) => {
            if (result.type === 'success') {
                await update({ reset: false });
                message_update = { type: 'success', message: m.onsiteAttendees_successMessage() };
            } else {
                message_update = { type: 'error', message: m.onsiteAttendees_errorMessage() };
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

    let nametag_modal = $state(false);
    let selected_nametag = $state({});
    const showNametagModal = async (id) => {
        const doc = new jsPDF({
            orientation: "portrait",
            unit: "mm",
            format: [90, 100]
        });
        let p = data.onsite_attendees.find(a => a.id === id);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(30);
        let splitName = doc.splitTextToSize(p.name, 80);
        doc.text(splitName, 45, 45 - (splitName.length - 1) * 12, 'center');
        doc.setFontSize(20);
        let splitInstitute = doc.splitTextToSize(p.institute, 80);
        doc.text(splitInstitute, 45, 55, 'center');
        doc.setFontSize(23);
        doc.setLineWidth(1);
        doc.line(5, 82, 85, 82);
        doc.text(`Participant`, 45, 93, 'center');
        selected_nametag = doc.output('bloburi');
        nametag_modal = true;
    };

    let cert_modal = $state(false);
    let selected_cert = $state({});
    const showCertificateModal = async (id) => {
        const doc = new jsPDF({
            orientation: "portrait",
            unit: "mm",
            format: [210, 297]
        });
        let p = data.onsite_attendees.find(a => a.id === id);
        let curr_y = 45;
        const add_line = (text, font_weight, font_size, y) => {
            doc.setFont("helvetica", font_weight?font_weight:'normal');
            doc.setFontSize(font_size?font_size:15);
            let splitText = doc.splitTextToSize(text, 150);
            if (y) {
                splitText.forEach((line, index) => {
                    doc.text(line, 105, y, 'center');
                });
            } else {
                splitText.forEach((line, index) => {
                    doc.text(line, 105, curr_y + (index * 10), 'center');
                });
                curr_y += (splitText.length * 12);
            }
        };
        add_line(`Issue date: ${new Date().toLocaleDateString()}`, 'italic', 10, 10);
        add_line(`Certificate of Attendance`, 'bold', 30);
        curr_y += 15;
        add_line(`This is to certify that below person`);
        add_line(p.name, 'bold');
        add_line(p.institute, 'bold');
        add_line(`has attended`);
        add_line(data.event.name, 'bold');
        add_line(`on`);
        add_line(data.event.start_date, 'bold');
        add_line(`to`);
        add_line(data.event.end_date, 'bold');
        add_line(`held at`);
        add_line(data.event.venue, 'bold');
        add_line(`as a participant.`);
        curr_y += 20;
        add_line(data.event.organizers, 'bold');
        add_line('This certificate was machine generated and is valid without a signature.', 'italic', 10, 287);

        selected_cert = doc.output('bloburi');
        cert_modal = true;
    };
</script>

<Heading tag="h2" customSize="text-xl font-bold" class="mb-3">{m.onsiteAttendees_title()}</Heading>
<p class="font-light mb-6">{m.onsiteAttendees_description()}</p>
<div class="flex justify-end sm:flex-row flex-col">
    <div class="flex items-center gap-2">
        <Button color="primary" size="sm" onclick={exportAttendeesAsCSV}>{m.onsiteAttendees_exportCSV()}</Button>
    </div>
</div>
<p class="mt-5 mb-3 text-sm text-right">{data.onsite_attendees.length} {m.onsiteAttendees_peopleRegistered()}</p>
<TableSearch placeholder={m.onsiteAttendees_searchPlaceholder()} hoverable={true} bind:inputValue={searchTermAttendee}>
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
        <TableHeadCell>{m.onsiteAttendees_id()}</TableHeadCell>
        <TableHeadCell>{m.onsiteAttendees_name()}</TableHeadCell>
        <TableHeadCell>{m.onsiteAttendees_institute()}</TableHeadCell>
        <TableHeadCell>{m.onsiteAttendees_jobTitle()}</TableHeadCell>
        <TableHeadCell class="w-1">{m.onsiteAttendees_actions()}</TableHeadCell>
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
                <TableBodyCell>{row.institute}</TableBodyCell>
                <TableBodyCell>{row.job_title}</TableBodyCell>
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
                <TableBodyCell colspan="6" class="text-center">{m.onsiteAttendees_noRecords()}</TableBodyCell>
            </TableBodyRow>
        {/if}
    </TableBody>
</TableSearch>

<Modal id="attendee_modal" size="xl" title={m.onsiteAttendees_detailsTitle()} bind:open={attendee_modal} outsideclose>
    <form method="post" action="?/update_onsite_attendee" use:enhance={afterSuccessfulSubmit}>
        <input type="hidden" name="id" value={data.onsite_attendees[selected_idx].id} />
        <OnSiteRegistrationForm data={data.onsite_attendees[selected_idx]} />
        {#if message_update.type === 'success'}
            <Alert type="success" color="green">{message_update.message}</Alert>
        {:else if message_update.type === 'error'}
            <Alert type="error" color="red">{message_update.message}</Alert>
        {/if}
        <div class="flex justify-center mt-6">
            <Button color="primary" type="submit">{m.onsiteAttendees_updateAttendee()}</Button>
        </div>
    </form>
</Modal>

<Modal id="remove_attendee_modal" size="sm" title={m.onsiteAttendees_removeTitle()} bind:open={remove_attendee_modal} outsideclose>
    <form method="post" action="?/remove_onsite_attendee" use:enhance={afterSuccessfulDeregistration}>
        <input type="hidden" name="id" value={data.onsite_attendees[selected_idx].id} />
        <p class="font-light mb-6">{m.onsiteAttendees_removeConfirm()}</p>
        <div class="flex justify-center gap-2">
            <Button color="red" type="submit">{m.onsiteAttendees_remove()}</Button>
            <Button color="dark" onclick={() => remove_attendee_modal = false}>{m.onsiteAttendees_cancel()}</Button>
        </div>
    </form>
</Modal>

<Modal id="nametag_modal" size="lg" title={m.onsiteAttendees_nametag()} bind:open={nametag_modal} outsideclose>
    <iframe id="nametag" class="w-full h-[500px]" src={selected_nametag} title="Nametag">
        Your browser does not support iframes.
    </iframe>
    <div class="flex justify-center mt-6 gap-2">
        <Button color="primary" onclick={() => {
            const iframe = document.getElementById('nametag');
            if (iframe) {
                iframe.contentWindow.print();
            }
        }}>{m.onsiteAttendees_print()}</Button>
        <Button color="dark" onclick={() => nametag_modal = false}>{m.onsiteAttendees_close()}</Button>
    </div>
</Modal>

<Modal id="cert_modal" size="lg" title={m.onsiteAttendees_certificate()} bind:open={cert_modal} outsideclose>
    <iframe id="cert" class="w-full h-[500px]" src={selected_cert} title="Certificate">
        Your browser does not support iframes.
    </iframe>
    <div class="flex justify-center mt-6 gap-2">
        <Button color="primary" onclick={() => {
            const iframe = document.getElementById('cert');
            if (iframe) {
                iframe.contentWindow.print();
            }
        }}>{m.onsiteAttendees_print()}</Button>
        <Button color="dark" onclick={() => cert_modal = false}>{m.onsiteAttendees_close()}</Button>
    </div>
</Modal>
