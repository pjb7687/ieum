<script>
    import { TableSearch, TableHead, TableHeadCell, TableBody, TableBodyRow, TableBodyCell, Checkbox, Button } from 'flowbite-svelte';
    import { Modal, Heading, Textarea, Select, Label, Card, Input } from 'flowbite-svelte';
    import { Alert } from 'flowbite-svelte';
    import { enhance } from '$app/forms';
    import { UserAddSolid, UserEditSolid, UserRemoveSolid, TextSizeOutline } from 'flowbite-svelte-icons';

    import OnSiteRegistrationForm from './OnSiteRegistrationForm.svelte';

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

    const afterSuccessfulDeregistration = () => {
        return async ({ result, action, update }) => {
            if (result.type === 'success') {
                await update({ reset: false });
            }
            remove_attendee_modal = false;
        };
    };
</script>

<Heading tag="h2" customSize="text-xl font-bold" class="mb-3">On-site Attendees</Heading>
<p class="font-light mb-6">Below is the list of on-site attendees for this event.</p>
<div class="flex justify-end sm:flex-row flex-col">
    <div class="flex items-center gap-2">
        <Button color="primary" size="sm" onclick={exportAttendeesAsCSV}>Export All Data as CSV</Button>
    </div>
</div>
<p class="mt-5 mb-3 text-sm text-right">{data.onsite_attendees.length} people registered to this event.</p>
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
        <TableHeadCell>Institute</TableHeadCell>
        <TableHeadCell>Job Title</TableHeadCell>
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
                <TableBodyCell>{row.institute}</TableBodyCell>
                <TableBodyCell>{row.job_title}</TableBodyCell>
                <TableBodyCell>
                    <div class="flex justify-center gap-2">
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
                <TableBodyCell colspan="6" class="text-center">No records</TableBodyCell>
            </TableBodyRow>
        {/if}
    </TableBody>
</TableSearch>

<Modal id="attendee_modal" size="xl" title="Attendee Details" bind:open={attendee_modal} outsideclose>
    <form method="post" action="?/update_onsite_attendee" use:enhance={afterSuccessfulSubmit}>
        <input type="hidden" name="id" value={data.onsite_attendees[selected_idx].id} />
        <OnSiteRegistrationForm data={data.onsite_attendees[selected_idx]} />
        <div class="flex justify-center mt-6">
            <Button color="primary" type="submit">Update Attendee Information</Button>
        </div>
    </form>
</Modal>

<Modal id="remove_attendee_modal" size="sm" title="Are you sure?" bind:open={remove_attendee_modal} outsideclose>
    <form method="post" action="?/remove_onsite_attendee" use:enhance={afterSuccessfulDeregistration}>
        <input type="hidden" name="id" value={data.onsite_attendees[selected_idx].id} />
        <p class="font-light mb-6">Are you sure you want to remove this attendee?</p>
        <div class="flex justify-center gap-2">
            <Button color="red" type="submit">Remove</Button>
            <Button color="dark" onclick={() => remove_attendee_modal = false}>Cancel</Button>
        </div>
    </form>
</Modal>