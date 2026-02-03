<script>
    import { Heading, TableSearch, TableHead, TableHeadCell, TableBody, TableBodyRow, TableBodyCell, Card } from 'flowbite-svelte';
    import { Button, Modal, Label, Select, Alert } from 'flowbite-svelte';
    import { UserRemoveSolid, ChevronUpOutline, ChevronDownOutline } from 'flowbite-svelte-icons';
    import { enhance } from '$app/forms';
    import { invalidateAll } from '$app/navigation';
    import * as m from '$lib/paraglide/messages.js';
    import { getDisplayInstitute, getDisplayName } from '$lib/utils.js';
    import MultiUserSelector from '$lib/components/MultiUserSelector.svelte';
    import TablePagination from '$lib/components/TablePagination.svelte';

    let { data } = $props();

    // Staff users get full user list, event admins get attendees only
    // Filter out attendees whose user has been deleted (they can't be organizers without an account)
    const userList = $derived(data.users ? data.users.map(u => ({ id: u.id, ...u })) : data.attendees.filter(a => a.user).map(a => ({ ...a, id: a.user.id })));

    // Filter out users who are already organizers
    const existingOrganizerIds = $derived(data.organizers.map(o => o.id));
    const availableUsers = $derived(userList.filter(u => !existingOrganizerIds.includes(u.id)));

    let searchTermOrganizer = $state('');
    let currentPage = $state(1);
    const itemsPerPage = 10;

    let filteredOrganizers = $derived(
        data.organizers.filter((item) => {
            const searchLower = searchTermOrganizer.toLowerCase();
            return item.name.toLowerCase().includes(searchLower) ||
                   (item.korean_name && item.korean_name.toLowerCase().includes(searchLower));
        })
    );

    // Reset to page 1 when search changes
    $effect(() => {
        searchTermOrganizer;
        currentPage = 1;
    });

    let totalPages = $derived(Math.ceil(filteredOrganizers.length / itemsPerPage));
    let paginatedOrganizers = $derived(
        filteredOrganizers.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
    );

    function handlePageChange(page) {
        currentPage = page;
    }

    let organizer_modal = $state(false);
    let delete_organizer_modal = $state(false);
    let selected_organizer = $state(null);
    let selectedOrganizerIds = $state([]);
    let reordering = $state(false);

    const addOrganizerModal = () => {
        selectedOrganizerIds = [];
        organizer_modal = true;
    };
    const deleteOrganizerModal = (id) => {
        selected_organizer = data.organizers.find((item) => item.id === id);
        delete_organizer_modal = true;
    };

    // Reorder functions
    async function moveOrganizer(index, direction) {
        if (reordering) return;

        const newIndex = index + direction;
        if (newIndex < 0 || newIndex >= data.organizers.length) return;

        reordering = true;

        // Create new order
        const newOrder = [...data.organizers.map(o => o.id)];
        [newOrder[index], newOrder[newIndex]] = [newOrder[newIndex], newOrder[index]];

        try {
            const response = await fetch(`/api/event/${data.event.id}/organizers/reorder`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ order: newOrder })
            });

            if (response.ok) {
                await invalidateAll();
            }
        } catch (error) {
            console.error('Failed to reorder organizers:', error);
        } finally {
            reordering = false;
        }
    }

    let add_organizer_error = $state('');
    const afterAddOrganizer = () => {
        return async ({ result, action, update }) => {
            if (result.type === "success") {
                await update({ reset: false });
                organizer_modal = false;
                add_organizer_error = '';
                selectedOrganizerIds = [];
            } else {
                add_organizer_error = m.userSelection_error();
            }
        }
    };

    let delete_organizer_error = $state('');
    const afterDeleteOrganizer = () => {
        return async ({ result, action, update }) => {
            if (result.type === "success") {
                await update({ reset: false });
                delete_organizer_modal = false;
                delete_organizer_error = '';
            } else {
                delete_organizer_error = m.userSelection_error();
            }
        }
    };
</script>

<Heading tag="h2" class="text-xl font-bold mb-3">{m.organizers_title()}</Heading>
<p class="font-light mb-6">{m.organizers_description()}</p>
<div class="flex justify-end gap-2 mb-4">
    <Button color="primary" size="sm" onclick={addOrganizerModal}>{m.organizers_addOrganizer()}</Button>
</div>
<TableSearch placeholder={m.organizers_searchPlaceholder()} hoverable={true} bind:inputValue={searchTermOrganizer}>
    <TableHead>
        <TableHeadCell class="w-1">{m.organizers_order()}</TableHeadCell>
        <TableHeadCell>{m.organizers_name()}</TableHeadCell>
        <TableHeadCell>{m.organizers_email()}</TableHeadCell>
        <TableHeadCell>{m.organizers_institute()}</TableHeadCell>
        <TableHeadCell class="w-1">{m.organizers_actions()}</TableHeadCell>
    </TableHead>
    <TableBody tableBodyClass="divide-y">
        {#each paginatedOrganizers as row, localIndex}
            {@const globalIndex = (currentPage - 1) * itemsPerPage + localIndex}
            <TableBodyRow>
                <TableBodyCell>
                    <div class="flex flex-col gap-0.5">
                        <button
                            onclick={() => moveOrganizer(globalIndex, -1)}
                            disabled={globalIndex === 0 || reordering || searchTermOrganizer}
                            class="p-0.5 rounded hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                            <ChevronUpOutline class="w-4 h-4" />
                        </button>
                        <button
                            onclick={() => moveOrganizer(globalIndex, 1)}
                            disabled={globalIndex === data.organizers.length - 1 || reordering || searchTermOrganizer}
                            class="p-0.5 rounded hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                            <ChevronDownOutline class="w-4 h-4" />
                        </button>
                    </div>
                </TableBodyCell>
                <TableBodyCell>{getDisplayName(row)}</TableBodyCell>
                <TableBodyCell>{row.email}</TableBodyCell>
                <TableBodyCell>{getDisplayInstitute(row)}</TableBodyCell>
                <TableBodyCell>
                    <div class="flex justify-center gap-2">
                        <Button color="none" size="none" onclick={() => deleteOrganizerModal(row.id)}>
                            <UserRemoveSolid class="w-5 h-5" />
                        </Button>
                    </div>
                </TableBodyCell>
            </TableBodyRow>
        {/each}
        {#if filteredOrganizers.length === 0}
            <TableBodyRow>
                <TableBodyCell colspan="5" class="text-center">{m.organizers_noRecords()}</TableBodyCell>
            </TableBodyRow>
        {/if}
    </TableBody>
</TableSearch>

<TablePagination {currentPage} {totalPages} onPageChange={handlePageChange} />

<Modal bind:open={organizer_modal} title={m.organizers_addOrganizerTitle()} size="lg">
    <form method="POST" action="?/add_organizer" use:enhance={afterAddOrganizer}>
        <MultiUserSelector
            users={availableUsers}
            bind:selectedIds={selectedOrganizerIds}
        />
        <input type="hidden" name="ids" value={JSON.stringify(selectedOrganizerIds)} />
        {#if add_organizer_error}
            <Alert color="red" class="mb-6">{add_organizer_error}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="alternative" type="button" onclick={() => organizer_modal = false}>{m.common_cancel()}</Button>
            <Button color="primary" type="submit" disabled={selectedOrganizerIds.length === 0}>{m.organizers_add()}</Button>
        </div>
    </form>
</Modal>

<Modal bind:open={delete_organizer_modal} title={m.organizers_deleteOrganizer()} size="sm">
    <form method="POST" action="?/delete_organizer" use:enhance={afterDeleteOrganizer}>
        <input type="hidden" name="id" value={selected_organizer?selected_organizer.id:''} />
        <p class="mb-6">{m.organizers_deleteConfirm()}</p>
        {#if delete_organizer_error}
            <Alert color="red" class="mb-6">{delete_organizer_error}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="red" type="submit">{m.organizers_delete()}</Button>
            <Button color="dark" type="button" onclick={() => delete_organizer_modal = false}>{m.organizers_cancel()}</Button>
        </div>
    </form>
</Modal>
