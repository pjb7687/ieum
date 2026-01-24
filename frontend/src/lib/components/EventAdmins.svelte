<script>
    import { Heading, TableSearch, TableHead, TableHeadCell, TableBody, TableBodyRow, TableBodyCell, Checkbox, Card} from 'flowbite-svelte';
    import { Button, Modal, Label, Input, Select, Textarea, Alert } from 'flowbite-svelte';
    import { Tabs, TabItem } from 'flowbite-svelte';
    import { UserEditSolid, UserRemoveSolid } from 'flowbite-svelte-icons';
    import { enhance } from '$app/forms';
    import { error } from '@sveltejs/kit';
    import * as m from '$lib/paraglide/messages.js';

    let { data } = $props();

    let searchTermEventAdmin = $state('');
    let filteredEventAdmins = $state([]);
    $effect(() => {
        filteredEventAdmins = data.eventadmins.filter((item) => item.name.toLowerCase().includes(searchTermEventAdmin.toLowerCase()))
    });

    let eventadmin_modal = $state(false);
    let delete_eventadmin_modal = $state(false);
    let selected_eventadmin = $state(null);

    const addEventAdminModal = () => {
        selected_eventadmin = null;
        eventadmin_modal = true;
    };
    const deleteEventAdminModal = (id) => {
        selected_eventadmin = data.eventadmins.find((item) => item.id === id);
        delete_eventadmin_modal = true;
    };

    let add_eventadmin_error = $state('');
    const afterAddEventAdmin = () => {
        return async ({ result, action, update }) => {
            if (result.type === "success") {
                await update({ reset: false });
                eventadmin_modal = false;
                add_eventadmin_error = '';
            } else {
                add_eventadmin_error = result.error.message;
            }
        }
    };

    let delete_eventadmin_error = $state('');
    const afterDeleteEventAdmin = () => {
        return async ({ result, action, update }) => {
            if (result.type === "success") {
                await update({ reset: false });
                delete_eventadmin_modal = false;
                delete_eventadmin_error = '';
            } else {
                delete_eventadmin_error = result.error.message;
            }
        }
    };
</script>

<Heading tag="h2" customSize="text-xl font-bold" class="mb-3">{m.eventAdmins_title()}</Heading>
<p class="font-light mb-6">{m.eventAdmins_description()}</p>
<div class="flex justify-end gap-2">
    <Button color="primary" size="sm" onclick={addEventAdminModal}>{m.eventAdmins_addAdmin()}</Button>
</div>
<TableSearch placeholder={m.eventAdmins_searchPlaceholder()} hoverable={true} bind:inputValue={searchTermEventAdmin}>
    <TableHead>
        <TableHeadCell>{m.eventAdmins_name()}</TableHeadCell>
        <TableHeadCell>{m.eventAdmins_email()}</TableHeadCell>
        <TableHeadCell>{m.eventAdmins_institute()}</TableHeadCell>
        <TableHeadCell class="w-1">{m.eventAdmins_actions()}</TableHeadCell>
    </TableHead>
    <TableBody tableBodyClass="divide-y">
        {#each filteredEventAdmins as row}
            <TableBodyRow>
                <TableBodyCell>{row.name}</TableBodyCell>
                <TableBodyCell>{row.email}</TableBodyCell>
                <TableBodyCell>{row.institute}</TableBodyCell>
                <TableBodyCell>
                    <div class="flex justify-center gap-2">
                        <Button color="none" size="none" onclick={() => deleteEventAdminModal(row.id)}>
                            <UserRemoveSolid class="w-5 h-5" />
                        </Button>
                    </div>
                </TableBodyCell>
            </TableBodyRow>
        {/each}
        {#if filteredEventAdmins.length === 0}
            <TableBodyRow>
                <TableBodyCell colspan="4" class="text-center">{m.eventAdmins_noRecords()}</TableBodyCell>
            </TableBodyRow>
        {/if}
    </TableBody>
</TableSearch>

<Modal bind:open={eventadmin_modal} title={m.eventAdmins_addAdminTitle()} size="lg">
    <form method="POST" action="?/add_eventadmin" use:enhance={afterAddEventAdmin}>
        <div class="mb-6">
            <Label for="id" class="block mb-2">{m.eventAdmins_admin()}</Label>
            <Select id="id" name="id" items={
                data.users.map(a => ({ value: a.id, name: `${a.name}, ${a.institute} (${a.email})` }))
            } onchange={
                (e) => {
                    const id = parseInt(e.target.value);
                    const user = data.users.find(a => a.id === id);
                    document.getElementById('name').value = user.name;
                    document.getElementById('email').value = user.email;
                    document.getElementById('affiliation').value = user.institute;
                }
            } />
        </div>
        {#if add_eventadmin_error}
            <Alert color="red" class="mb-6">{add_eventadmin_error}</Alert>
        {/if}
        <div class="flex justify-center">
            <Button color="primary" type="submit">{m.eventAdmins_add()}</Button>
        </div>
    </form>
</Modal>

<Modal bind:open={delete_eventadmin_modal} title={m.eventAdmins_deleteAdmin()} size="sm">
    <form method="POST" action="?/delete_eventadmin" use:enhance={afterDeleteEventAdmin}>
        <input type="hidden" name="id" value={selected_eventadmin?selected_eventadmin.id:''} />
        <p class="mb-6">{m.eventAdmins_deleteConfirm()}</p>
        {#if delete_eventadmin_error}
            <Alert color="red" class="mb-6">{delete_eventadmin_error}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="red" type="submit">{m.eventAdmins_delete()}</Button>
            <Button color="dark" type="button" onclick={() => delete_eventadmin_modal = false}>{m.eventAdmins_cancel()}</Button>
        </div>
    </form>
</Modal>
