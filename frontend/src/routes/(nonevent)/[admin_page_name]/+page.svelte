<script>
    import { TableSearch, TableHead, TableHeadCell, TableBody, TableBodyRow, TableBodyCell} from 'flowbite-svelte';
    import { Modal, Heading, Button, Alert } from 'flowbite-svelte';
    import { CogSolid, TrashBinSolid } from 'flowbite-svelte-icons';
    import { enhance } from '$app/forms';
    import * as m from '$lib/paraglide/messages.js';

    import EventAdminForm from '$lib/components/EventAdminForm.svelte';

    let { data } = $props();

    let selected_event = $state(null);
    let delete_error = $state('');
    let delete_modal = $state(false);

    let search_term = $state('');
    let filtered_events = $state([]);
    $effect(() => {
        filtered_events = data.admin.events.filter((item) => item.name.toLowerCase().indexOf(search_term.toLowerCase()) !== -1);
    });

    const afterDelete = () => {
        return async ({ result, action, update }) => {
            if (result.type === "success") {
                await update();
                delete_modal = false;
                delete_error = '';
            } else {
                delete_error = result.error.message;
            }
        }
    };
    const deleteEvent = (event) => {
        selected_event = event;
        delete_modal = true;
    };
    
    let create_modal = $state(false);
    let create_error = $state('');
    const afterCreate = () => {
        return async ({ result, action, update }) => {
            if (result.type === "success") {
                await update();
                create_modal = false;
                create_error = '';
            } else {
                create_error = result.error.message;
            }
        }
    };
</script>

<!-- Page Header Card -->
<div class="relative rounded-lg shadow-sm py-16 px-8 mb-8 overflow-hidden" style="background-image: url('/bg-events.webp'); background-size: cover; background-position: center;">
    <div class="absolute inset-0 bg-slate-900 opacity-60"></div>
    <div class="relative z-10">
        <h1 class="text-3xl font-bold text-white">{m.admin_manageEvents_title()}</h1>
        <p class="text-slate-200 mt-2">{m.admin_manageEvents_description()}</p>
    </div>
</div>

<!-- Content Card -->
<div class="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
    <div class="flex justify-end mb-6">
        <Button color="primary" onclick={() => create_modal = true}>{m.admin_createEvent()}</Button>
    </div>

    <TableSearch placeholder={m.admin_searchEvents()} bind:inputValue={search_term} hoverable={true}>
        <TableHead>
            <TableHeadCell>{m.admin_tableId()}</TableHeadCell>
            <TableHeadCell>{m.admin_tableName()}</TableHeadCell>
            <TableHeadCell>{m.admin_tableVenue()}</TableHeadCell>
            <TableHeadCell class="w-1">{m.admin_tableActions()}</TableHeadCell>
        </TableHead>
        <TableBody>
            {#each filtered_events as event}
                <TableBodyRow>
                    <TableBodyCell>{event.id}</TableBodyCell>
                    <TableBodyCell>
                        <a href={`/event/${event.id}`}>{event.name}</a>
                    </TableBodyCell>
                    <TableBodyCell>{event.venue}</TableBodyCell>
                    <TableBodyCell>
                        <div class="flex justify-center gap-2">
                            <Button color="none" size="none" href={`/event/${event.id}/admin`}>
                                <CogSolid class="w-5 h-5" />
                            </Button>
                            <Button color="none" size="none" onclick={() => deleteEvent(event)}>
                                <TrashBinSolid class="w-5 h-5" />
                            </Button>
                        </div>
                    </TableBodyCell>
                </TableBodyRow>
            {/each}
            {#if filtered_events.length === 0}
                <TableBodyRow>
                    <TableBodyCell colspan="4" class="text-center">{m.admin_noEventsFound()}</TableBodyCell>
                </TableBodyRow>
            {/if}
        </TableBody>
    </TableSearch>
</div>

<Modal id="delete_modal" size="sm" title={m.admin_removeEventTitle()} bind:open={delete_modal} outsideclose>
    <form method="post" action="?/delete_event" use:enhance={afterDelete}>
        <input type="hidden" name="id" value={selected_event?selected_event.id:''} />
        <p class="mb-6">{m.admin_removeEventConfirm()}</p>
        {#if delete_error}
            <Alert color="red" class="mb-6">{delete_error}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="red" type="submit">{m.admin_remove()}</Button>
            <Button color="dark" type="button" onclick={() => delete_modal = false}>{m.common_cancel()}</Button>
        </div>
    </form>
</Modal>

<Modal id="create_modal" size="xl" title={m.admin_createEventTitle()} bind:open={create_modal} outsideclose>
    <form method="post" action="?/create_event" use:enhance={afterCreate}>
        <EventAdminForm />
        {#if create_error}
            <Alert color="red" class="mb-6">{create_error}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="primary" type="submit">{m.admin_create()}</Button>
            <Button color="alternative" type="button" onclick={() => create_modal = false}>{m.common_cancel()}</Button>
        </div>
    </form>
</Modal>