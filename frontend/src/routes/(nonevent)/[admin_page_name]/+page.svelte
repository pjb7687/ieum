<script>
    import { TableSearch, TableHead, TableHeadCell, TableBody, TableBodyRow, TableBodyCell} from 'flowbite-svelte';
    import { Modal, Heading, Button, Alert } from 'flowbite-svelte';
    import { CogSolid, TrashBinSolid, UserEditSolid } from 'flowbite-svelte-icons';
    import { enhance } from '$app/forms';
    import * as m from '$lib/paraglide/messages.js';
    import { getDisplayInstitute, getDisplayName } from '$lib/utils.js';

    import EventAdminForm from '$lib/components/EventAdminForm.svelte';
    import RegistrationForm from '$lib/components/RegistrationForm.svelte';

    let { data } = $props();

    let selected_event = $state(null);
    let delete_error = $state('');
    let delete_modal = $state(false);

    let search_term = $state('');
    let filtered_events = $state([]);
    $effect(() => {
        filtered_events = data.admin.events.filter((item) => item.name.toLowerCase().indexOf(search_term.toLowerCase()) !== -1);
    });

    let user_search_term = $state('');
    let filtered_users = $state([]);
    $effect(() => {
        filtered_users = data.admin.users.filter((user) => {
            const searchLower = user_search_term.toLowerCase();
            return user.name.toLowerCase().includes(searchLower) ||
                   (user.korean_name && user.korean_name.toLowerCase().includes(searchLower)) ||
                   user.email.toLowerCase().includes(searchLower) ||
                   (user.institute_en && user.institute_en.toLowerCase().includes(searchLower)) ||
                   (user.institute_ko && user.institute_ko.toLowerCase().includes(searchLower));
        });
    });

    let institution_search_term = $state('');
    let filtered_institutions = $state([]);
    $effect(() => {
        filtered_institutions = data.admin.institutions.filter((inst) =>
            inst.name_en.toLowerCase().indexOf(institution_search_term.toLowerCase()) !== -1 ||
            inst.name_ko.toLowerCase().indexOf(institution_search_term.toLowerCase()) !== -1
        );
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
    let newEventData = $state({
        name: '',
        description: '',
        category: 'conference',
        organizers: '',
        venue: '',
        venue_address: '',
        venue_latitude: null,
        venue_longitude: null,
        main_languages: ['en'],
        start_date: '',
        end_date: '',
        registration_deadline: '',
        capacity: 0,
        accepts_abstract: false,
        abstract_deadline: '',
        capacity_abstract: 0,
        max_votes: 2,
    });

    const afterCreate = () => {
        return async ({ result, action, update }) => {
            if (result.type === "success") {
                await update();
                create_modal = false;
                create_error = '';
                // Reset form data
                newEventData = {
                    name: '',
                    description: '',
                    category: 'conference',
                    organizers: '',
                    venue: '',
                    venue_address: '',
                    venue_latitude: null,
                    venue_longitude: null,
                    main_languages: ['en'],
                    start_date: '',
                    end_date: '',
                    registration_deadline: '',
                    capacity: 0,
                    accepts_abstract: false,
                    abstract_deadline: '',
                    capacity_abstract: 0,
                    max_votes: 2,
                };
            } else {
                create_error = result.error.message;
            }
        }
    };

    function handleCreateSubmit(event) {
        // Validate main_languages before submission
        if (!newEventData.main_languages || newEventData.main_languages.length === 0) {
            event.preventDefault();
            create_error = m.eventForm_mainLanguagesRequired();
            // Scroll to the error message
            const errorElement = document.querySelector('#create_modal .text-red-600');
            if (errorElement) {
                errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return false;
        }
        // Clear any previous error messages
        create_error = '';
    }

    // User management
    let selected_user = $state(null);
    let user_edit_modal = $state(false);
    let user_edit_error = $state('');

    const openUserEditModal = (user) => {
        selected_user = user;
        user_edit_modal = true;
        user_edit_error = '';
    };

    const afterUserEdit = () => {
        return async ({ result, update }) => {
            if (result.type === "success") {
                await update();
                user_edit_modal = false;
                user_edit_error = '';
                selected_user = null;
            } else {
                user_edit_error = result.error?.message || 'An error occurred';
            }
        }
    };

    // Institution management
    let selected_institution = $state(null);
    let institution_modal = $state(false);
    let institution_delete_modal = $state(false);
    let institution_error = $state('');

    const openInstitutionModal = (institution = null) => {
        selected_institution = institution;
        institution_modal = true;
        institution_error = '';
    };

    const deleteInstitution = (institution) => {
        selected_institution = institution;
        institution_delete_modal = true;
        institution_error = '';
    };

    const afterInstitutionAction = () => {
        return async ({ result, action, update }) => {
            if (result.type === "success") {
                await update();
                institution_modal = false;
                institution_delete_modal = false;
                institution_error = '';
                selected_institution = null;
            } else {
                institution_error = result.error?.message || 'An error occurred';
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
                    <TableBodyCell>
                        <div>
                            <div class="font-medium">{event.venue}</div>
                            {#if event.venue_address}
                                <div class="text-sm text-gray-600">{event.venue_address}</div>
                            {/if}
                        </div>
                    </TableBodyCell>
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
    <form method="post" action="?/create_event" use:enhance={afterCreate} on:submit={handleCreateSubmit}>
        <EventAdminForm bind:data={newEventData} />
        {#if create_error}
            <Alert color="red" class="mb-6">{create_error}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="primary" type="submit">{m.admin_create()}</Button>
            <Button color="alternative" type="button" onclick={() => create_modal = false}>{m.common_cancel()}</Button>
        </div>
    </form>
</Modal>

<!-- User Management Section -->
<div class="mt-8 bg-white border border-gray-200 rounded-lg shadow-sm p-6">
    <h2 class="text-2xl font-bold mb-6">{m.admin_manageUsers_title()}</h2>

    <TableSearch placeholder={m.admin_searchUsers()} bind:inputValue={user_search_term} hoverable={true}>
        <TableHead>
            <TableHeadCell>{m.admin_tableId()}</TableHeadCell>
            <TableHeadCell>{m.admin_tableUserName()}</TableHeadCell>
            <TableHeadCell>{m.admin_tableEmail()}</TableHeadCell>
            <TableHeadCell>{m.admin_tableInstitute()}</TableHeadCell>
            <TableHeadCell>{m.admin_tableJoinDate()}</TableHeadCell>
            <TableHeadCell>{m.admin_tableActiveStatus()}</TableHeadCell>
            <TableHeadCell>{m.admin_tableVerifiedStatus()}</TableHeadCell>
            <TableHeadCell class="w-1">{m.admin_tableActions()}</TableHeadCell>
        </TableHead>
        <TableBody>
            {#each filtered_users as user}
                <TableBodyRow>
                    <TableBodyCell>{user.id}</TableBodyCell>
                    <TableBodyCell>{getDisplayName(user)}</TableBodyCell>
                    <TableBodyCell>{user.email}</TableBodyCell>
                    <TableBodyCell>{getDisplayInstitute(user)}</TableBodyCell>
                    <TableBodyCell>{new Date(user.date_joined).toLocaleDateString()}</TableBodyCell>
                    <TableBodyCell>
                        <form method="post" action="?/toggle_user_active" use:enhance>
                            <input type="hidden" name="user_id" value={user.id} />
                            <Button size="xs" color={user.is_active ? 'green' : 'red'} type="submit" disabled={user.id === data.user.id}>
                                {user.is_active ? m.admin_userActive() : m.admin_userInactive()}
                            </Button>
                        </form>
                    </TableBodyCell>
                    <TableBodyCell>
                        <form method="post" action="?/toggle_user_verified" use:enhance>
                            <input type="hidden" name="user_id" value={user.id} />
                            <Button size="xs" color={user.email_verified ? 'green' : 'red'} type="submit">
                                {user.email_verified ? m.admin_userVerified() : m.admin_userUnverified()}
                            </Button>
                        </form>
                    </TableBodyCell>
                    <TableBodyCell>
                        <div class="flex justify-center">
                            <Button color="none" size="none" onclick={() => openUserEditModal(user)}>
                                <UserEditSolid class="w-5 h-5" />
                            </Button>
                        </div>
                    </TableBodyCell>
                </TableBodyRow>
            {/each}
            {#if filtered_users.length === 0}
                <TableBodyRow>
                    <TableBodyCell colspan="8" class="text-center">{m.admin_noUsersFound()}</TableBodyCell>
                </TableBodyRow>
            {/if}
        </TableBody>
    </TableSearch>
</div>

<!-- Institution Management Section -->
<div class="mt-8 bg-white border border-gray-200 rounded-lg shadow-sm p-6">
    <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold">{m.admin_manageInstitutions_title()}</h2>
        <Button color="primary" onclick={() => openInstitutionModal(null)}>{m.admin_addInstitution()}</Button>
    </div>

    <TableSearch placeholder={m.admin_searchInstitutions()} bind:inputValue={institution_search_term} hoverable={true}>
        <TableHead>
            <TableHeadCell>{m.admin_tableId()}</TableHeadCell>
            <TableHeadCell>{m.admin_tableInstitutionNameEn()}</TableHeadCell>
            <TableHeadCell>{m.admin_tableInstitutionNameKo()}</TableHeadCell>
            <TableHeadCell class="w-1">{m.admin_tableActions()}</TableHeadCell>
        </TableHead>
        <TableBody>
            {#each filtered_institutions as institution}
                <TableBodyRow>
                    <TableBodyCell>{institution.id}</TableBodyCell>
                    <TableBodyCell>{institution.name_en}</TableBodyCell>
                    <TableBodyCell>{institution.name_ko || '-'}</TableBodyCell>
                    <TableBodyCell>
                        <div class="flex justify-center gap-2">
                            <Button color="none" size="none" onclick={() => openInstitutionModal(institution)}>
                                <CogSolid class="w-5 h-5" />
                            </Button>
                            <Button color="none" size="none" onclick={() => deleteInstitution(institution)}>
                                <TrashBinSolid class="w-5 h-5" />
                            </Button>
                        </div>
                    </TableBodyCell>
                </TableBodyRow>
            {/each}
            {#if filtered_institutions.length === 0}
                <TableBodyRow>
                    <TableBodyCell colspan="4" class="text-center">{m.admin_noInstitutionsFound()}</TableBodyCell>
                </TableBodyRow>
            {/if}
        </TableBody>
    </TableSearch>
</div>

<!-- Institution Create/Edit Modal -->
<Modal id="institution_modal" size="md" title={selected_institution ? m.admin_editInstitution() : m.admin_addInstitution()} bind:open={institution_modal} outsideclose>
    <form method="post" action={selected_institution ? '?/update_institution' : '?/create_institution'} use:enhance={afterInstitutionAction}>
        {#if selected_institution}
            <input type="hidden" name="id" value={selected_institution.id} />
        {/if}
        <div class="mb-4">
            <label for="name_en" class="block mb-2 text-sm font-medium">{m.admin_institutionNameEn()}*</label>
            <input type="text" id="name_en" name="name_en" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5" value={selected_institution?.name_en || ''} required />
        </div>
        <div class="mb-6">
            <label for="name_ko" class="block mb-2 text-sm font-medium">{m.admin_institutionNameKo()}</label>
            <input type="text" id="name_ko" name="name_ko" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5" value={selected_institution?.name_ko || ''} />
        </div>
        {#if institution_error}
            <Alert color="red" class="mb-6">{institution_error}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="primary" type="submit">{selected_institution ? m.admin_update() : m.admin_create()}</Button>
            <Button color="alternative" type="button" onclick={() => institution_modal = false}>{m.common_cancel()}</Button>
        </div>
    </form>
</Modal>

<!-- Institution Delete Modal -->
<Modal id="institution_delete_modal" size="sm" title={m.admin_removeInstitutionTitle()} bind:open={institution_delete_modal} outsideclose>
    <form method="post" action="?/delete_institution" use:enhance={afterInstitutionAction}>
        <input type="hidden" name="id" value={selected_institution?.id || ''} />
        <p class="mb-6">{m.admin_removeInstitutionConfirm()}</p>
        {#if institution_error}
            <Alert color="red" class="mb-6">{institution_error}</Alert>
        {/if}
        <div class="flex justify-center gap-2">
            <Button color="red" type="submit">{m.admin_remove()}</Button>
            <Button color="dark" type="button" onclick={() => institution_delete_modal = false}>{m.common_cancel()}</Button>
        </div>
    </form>
</Modal>

<!-- User Edit Modal -->
<Modal id="user_edit_modal" size="xl" title={m.admin_editUser()} bind:open={user_edit_modal} outsideclose>
    {#if selected_user}
    <form method="post" action="?/update_user" use:enhance={afterUserEdit}>
        <input type="hidden" name="user_id" value={selected_user.id} />
        <RegistrationForm
            data={{
                email: selected_user.email,
                first_name: selected_user.first_name,
                middle_initial: selected_user.middle_initial,
                korean_name: selected_user.korean_name || '',
                last_name: selected_user.last_name,
                nationality: selected_user.nationality ? selected_user.nationality.toString() : '',
                institute: selected_user.institute || '',
                department: selected_user.department || '',
                job_title: selected_user.job_title || '',
                disability: selected_user.disability || '',
                dietary: selected_user.dietary || ''
            }}
            errors={{}}
            config={{
                hide_login_info: true,
                hide_password: true,
                show_english_name: true,
                show_korean_name: true
            }}
        />
        {#if user_edit_error}
            <Alert color="red" class="mb-6">{user_edit_error}</Alert>
        {/if}
        <div class="flex justify-center gap-2 mt-6">
            <Button color="primary" type="submit">{m.admin_update()}</Button>
            <Button color="alternative" type="button" onclick={() => user_edit_modal = false}>{m.common_cancel()}</Button>
        </div>
    </form>
    {/if}
</Modal>