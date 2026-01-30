<script>
    import { Heading, TableSearch, TableHead, TableHeadCell, TableBody, TableBodyRow, TableBodyCell, Checkbox, Card} from 'flowbite-svelte';
    import { Button, Modal, Label, Input, Select, Textarea, Alert } from 'flowbite-svelte';
    import { Tabs, TabItem } from 'flowbite-svelte';
    import { UserEditSolid, UserRemoveSolid, DownloadSolid, EditSolid, TrashBinSolid } from 'flowbite-svelte-icons';
    import { enhance } from '$app/forms';
    import { error } from '@sveltejs/kit';
    import * as m from '$lib/paraglide/messages.js';
    import { getDisplayInstitute, getDisplayName } from '$lib/utils.js';

    let { data } = $props();

    let searchTermReviewer = $state('');
    let filteredReviewers = $state([]);
    let selectedReviewers = $state([]);
    $effect(() => {
        filteredReviewers = data.reviewers.filter((item) => {
            const searchLower = searchTermReviewer.toLowerCase();
            return item.name.toLowerCase().includes(searchLower) ||
                   (item.korean_name && item.korean_name.toLowerCase().includes(searchLower));
        });
    });

    let reviewer_modal = $state(false);
    let delete_reviewer_modal = $state(false);
    let selected_reviewer = $state(null);

    const addReviewerModal = () => {
        selected_reviewer = null;
        reviewer_modal = true;
    };
    const deleteReviewerModal = (id) => {
        selected_reviewer = data.reviewers.find((item) => item.id === id);
        delete_reviewer_modal = true;
    };

    let add_reviwer_error = $state('');
    const afterAddReviewer = () => {
        return async ({ result, action, update }) => {
            if (result.type === "success") {
                await update({ reset: false });
                reviewer_modal = false;
                add_reviwer_error = '';
            } else {
                add_reviwer_error = result.error.message;
            }
        }
    };

    let delete_reviewer_error = $state('');
    const afterDeleteReviewer = () => {
        return async ({ result, action, update }) => {
            if (result.type === "success") {
                await update({ reset: false });
                delete_reviewer_modal = false;
                delete_reviewer_error = '';
            } else {
                delete_reviewer_error = result.error.message;
            }
        }
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
                message_send_email = { type: 'error', message: m.abstracts_sendEmailError() };
            }
        };
    };

    let abstract_modal = $state(false);
    let abstract_delete_modal = $state(false);
    let selected_abstract = $state(null);
    let update_abstract_error = $state('');
    const showAbstractEditModal = async (id) => {
        // fetch full abstract details
        const body = new FormData();
        body.append('id', id);
        const response = await fetch(`?/get_abstract`, {
            method: 'POST',
            body
        });
        if (response.ok) {
            const result = await response.json();
            selected_abstract = JSON.parse(JSON.parse(result.data)[0]);
            abstract_modal = true;
        } else {
            update_abstract_error = m.abstracts_fetchError();
        }
    };
    const showAbstractDeleteModal = (id) => {
        selected_abstract = data.abstracts.find((item) => item.id === id);
        abstract_delete_modal = true;
    };
    const afterUpdateAbstract = () => {
        return async ({ result, action, update }) => {
            if (result.type === "success") {
                await update({ reset: false });
                abstract_modal = false;
                update_abstract_error = '';
            } else {
                update_abstract_error = result.error.message;
            }
        }
    };

    let delete_abstract_error = $state('');
    const afterDeleteAbstract = () => {
        return async ({ result, action, update }) => {
            if (result.type === "success") {
                await update({ reset: false });
                abstract_delete_modal = false;
                delete_abstract_error = '';
            } else {
                delete_abstract_error = result.error.message;
            }
        }
    };
</script>

<Heading tag="h2" class="text-xl font-bold mb-3">{m.abstracts_title()}</Heading>
<p class="font-light mb-6">{m.abstracts_description()}</p>

<Heading tag="h3" class="text-lg font-bold mb-3">{m.abstracts_reviewersTitle()}</Heading>
<div class="flex justify-end gap-2">
    <Button color="primary" size="sm" disabled={selectedReviewers.length === 0} onclick={showSendEmailModal}>{m.abstracts_sendEmailToSelected()}</Button>
    <Button color="primary" size="sm" onclick={addReviewerModal}>{m.abstracts_addReviewer()}</Button>
</div>
<TableSearch placeholder={m.abstracts_searchReviewerPlaceholder()} hoverable={true} bind:inputValue={searchTermReviewer}>
    <TableHead>
        <TableHeadCell class="w-1"><Checkbox
            checked={selectedReviewers.length > 0 && selectedReviewers.length === data.reviewers.length}
            intermediate={
                selectedReviewers.length > 0 && (selectedReviewers.length < data.reviewers.length)
            }
            onclick={(e) => {
                if (e.target.checked) {
                    selectedReviewers = filteredReviewers.map(a => a.id);
                } else {
                    selectedReviewers = [];
                }
            }}
        /></TableHeadCell>
        <TableHeadCell>{m.abstracts_name()}</TableHeadCell>
        <TableHeadCell>{m.abstracts_email()}</TableHeadCell>
        <TableHeadCell>{m.abstracts_institute()}</TableHeadCell>
        <TableHeadCell class="w-1">{m.abstracts_actions()}</TableHeadCell>
    </TableHead>
    <TableBody tableBodyClass="divide-y">
        {#each filteredReviewers as row}
            <TableBodyRow>
                <TableBodyCell><Checkbox checked={selectedReviewers.includes(row.id)} onclick={(e) => {
                    if (e.target.checked) {
                        selectedReviewers = [...selectedReviewers, row.id];
                    } else {
                        selectedReviewers = selectedReviewers.filter(a => a !== row.id);
                    }
                }} /></TableBodyCell>
                <TableBodyCell>{getDisplayName(row)}</TableBodyCell>
                <TableBodyCell>{row.user.email}</TableBodyCell>
                <TableBodyCell>{getDisplayInstitute(row)}</TableBodyCell>
                <TableBodyCell>
                    <div class="flex justify-center gap-2">
                        <Button color="none" size="none" onclick={() => deleteReviewerModal(row.id)}>
                            <UserRemoveSolid class="w-5 h-5" />
                        </Button>
                    </div>
                </TableBodyCell>
            </TableBodyRow>
        {/each}
        {#if filteredReviewers.length === 0}
            <TableBodyRow>
                <TableBodyCell colspan="5" class="text-center">{m.abstracts_noRecords()}</TableBodyCell>
            </TableBodyRow>
        {/if}
    </TableBody>
</TableSearch>

<Heading tag="h3" class="text-lg font-bold mt-12 mb-3">{m.abstracts_abstractsTitle()}</Heading>
<TableSearch placeholder={m.abstracts_searchAbstractPlaceholder()} hoverable={true}>
    <TableHead>
        <TableHeadCell>{m.abstracts_title()}</TableHeadCell>
        <TableHeadCell>{m.abstracts_presenter()}</TableHeadCell>
        <TableHeadCell>{m.abstracts_type()}</TableHeadCell>
        <TableHeadCell>{m.abstracts_accepted()}</TableHeadCell>
        <TableHeadCell>{m.abstracts_votes()}</TableHeadCell>
        <TableHeadCell class="w-1">{m.abstracts_actions()}</TableHeadCell>
    </TableHead>
    <TableBody tableBodyClass="divide-y">
        {#each data.abstracts as row}
            <TableBodyRow>
                <TableBodyCell>{(row.title.length > 10)?row.title.slice(0, 10)+'...':row.title}</TableBodyCell>
                <TableBodyCell>{getDisplayName(row.attendee)}</TableBodyCell>
                <TableBodyCell>{row.is_oral ? m.abstractType_oral() : m.abstractType_poster()}</TableBodyCell>
                <TableBodyCell>{row.is_accepted}</TableBodyCell>
                <TableBodyCell>{row.votes}</TableBodyCell>
                <TableBodyCell>
                    <div class="flex justify-center gap-2">
                        <Button color="none" size="none" href={row.link}>
                            <DownloadSolid class="w-5 h-5" />
                        </Button>
                        <Button color="none" size="none" onclick={() => showAbstractEditModal(row.id)}>
                            <EditSolid class="w-5 h-5" />
                        </Button>
                        <Button color="none" size="none" onclick={() => showAbstractDeleteModal(row.id)}>
                            <TrashBinSolid class="w-5 h-5" />
                        </Button>
                    </div>
                </TableBodyCell>
            </TableBodyRow>
        {/each}
        {#if data.abstracts.length === 0}
            <TableBodyRow>
                <TableBodyCell colspan="5" class="text-center">{m.abstracts_noRecords()}</TableBodyCell>
            </TableBodyRow>
        {/if}
    </TableBody>
</TableSearch>

<Modal bind:open={reviewer_modal} title={m.abstracts_addReviewer()} size="lg">
    <form method="POST" action="?/add_reviewer" use:enhance={afterAddReviewer}>
        <div class="mb-6">
            <Label for="id" class="block mb-2">{m.abstracts_reviewer()}</Label>
            <Select id="id" name="id" items={
                data.attendees.map(a => ({ value: a.id, name: getDisplayName(a) + ", " + getDisplayInstitute(a) }))
            } onchange={
                (e) => {
                    const id = parseInt(e.target.value);
                    const attendee = data.attendees.find(a => a.id === id);
                    document.getElementById('name').value = getDisplayName(attendee);
                    document.getElementById('email').value = attendee.user.email;
                    document.getElementById('affiliation').value = getDisplayInstitute(attendee);
                }
            } />
        </div>
        {#if add_reviwer_error}
            <Alert color="red" class="mb-6">{add_reviwer_error}</Alert>
        {/if}
        <div class="flex justify-center">
            <Button color="primary" type="submit">{m.abstracts_add()}</Button>
        </div>
    </form>
</Modal>

<Modal bind:open={delete_reviewer_modal} title={m.abstracts_removeReviewer()} size="sm">
    <form method="POST" action="?/delete_reviewer" use:enhance={afterDeleteReviewer}>
        <input type="hidden" name="id" value={selected_reviewer?selected_reviewer.id:''} />
        <p class="mb-6">{m.abstracts_removeReviewerConfirm()}</p>
        {#if delete_reviewer_error}
            <Alert color="red" class="mb-6">{delete_reviewer_error}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="red" type="submit">{m.abstracts_remove()}</Button>
            <Button color="dark" type="button" onclick={() => delete_reviewer_modal = false}>{m.abstracts_cancel()}</Button>
        </div>
    </form>
</Modal>

<Modal id="send_email_modal" size="lg" title={m.abstracts_sendEmails()} bind:open={send_email_modal} outsideclose>
    <form method="post" action="?/send_emails" use:enhance={afterSuccessfulSendEmails}>
        <div class="mb-6">
            <Label for="to" class="block mb-2 text-black">{m.abstracts_to()}</Label>
            <Input id="to" name="to" type="text" value={selectedReviewers.map(id => data.reviewers.find(a => a.id === id).user.email).join("; ")} readonly />
        </div>
        <div class="mb-6">
            <Label for="subject" class="block mb-2">{m.abstracts_subject()}</Label>
            <Input id="subject" name="subject" type="text" />
        </div>
        <div class="mb-6">
            <Label for="body" class="block mb-2">{m.abstracts_message()}</Label>
            <Textarea id="body" name="body" rows="10" class="w-full" />
        </div>
        {#if message_send_email.type === 'error'}
            <Alert type="error" color="red" class="mb-6">{message_send_email.message}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="primary" type="submit">{m.abstracts_sendEmails()}</Button>
        </div>
    </form>
</Modal>

<Modal id="abstract_modal" size="lg" title={m.abstracts_detailsTitle()} bind:open={abstract_modal} outsideclose>
    <form method="post" action="?/update_abstract" use:enhance={afterUpdateAbstract}>
        <input type="hidden" name="id" value={selected_abstract?selected_abstract.id:''} />
        <div class="flex flex-row justify-stretch gap-6 mb-6">
            <div class="w-full">
                <Label for="votes" class="block mb-2">{m.abstracts_votes()}</Label>
                <Input id="votes" type="number" value={selected_abstract?selected_abstract.votes:''} readonly />
            </div>
            <div class="w-full">
                <Label for="type" class="block mb-2">{m.abstracts_type()}</Label>
                <Select id="type" name="type" items={[
                    { value: 'oral', name: m.abstractType_oral() },
                    { value: 'poster', name: m.abstractType_poster() }
                ]} value={selected_abstract?selected_abstract.is_oral?'oral':'poster':''} />
            </div>
            <div class="w-full">
                <Label for="is_accepted" class="block mb-2">{m.abstracts_accepted()}</Label>
                <Select id="is_accepted" name="is_accepted" items={[
                    { value: 'true', name: m.abstracts_yes() },
                    { value: 'false', name: m.abstracts_no() }
                ]} value={selected_abstract?selected_abstract.is_accepted?'true':'false':''} />
            </div>
        </div>
        <div class="mb-6">
            <Label for="presenter" class="block mb-2">{m.abstracts_presenter()}</Label>
            <Input id="presenter" type="text" value={selected_abstract?getDisplayName(selected_abstract.attendee):''} readonly />
        </div>
        <div class="mb-6">
            <Label for="title" class="block mb-2">{m.abstracts_titleField()}</Label>
            <Input id="title" name="title" type="text" value={selected_abstract?selected_abstract.title:''} />
        </div>
        <div class="mb-6">
            <Label for="abstract" class="block mb-2">{m.abstracts_preview()}</Label>
            <Card size="xl">
                {@html selected_abstract?selected_abstract.body:''}
            </Card>
        </div>
        {#if update_abstract_error}
            <Alert color="red" class="mb-6">{update_abstract_error}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="primary" type="submit">{m.abstracts_update()}</Button>
        </div>
    </form>
</Modal>

<Modal id="abstract_delete_modal" size="sm" title={m.abstracts_removeAbstract()} bind:open={abstract_delete_modal} outsideclose>
    <form method="post" action="?/delete_abstract" use:enhance={afterDeleteAbstract}>
        <input type="hidden" name="id" value={selected_abstract?selected_abstract.id:''} />
        <p class="mb-6">{m.abstracts_removeAbstractConfirm()}</p>
        {#if delete_abstract_error}
            <Alert color="red" class="mb-6">{delete_abstract_error}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="red" type="submit">{m.abstracts_remove()}</Button>
            <Button color="dark" type="button" onclick={() => abstract_delete_modal = false}>{m.abstracts_cancel()}</Button>
        </div>
    </form>
</Modal>
