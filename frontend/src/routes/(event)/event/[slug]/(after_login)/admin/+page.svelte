<script>
    import { error } from '@sveltejs/kit';
    import { Modal, Heading, Button, Table, TableSearch, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell, Input, Label } from 'flowbite-svelte';
    import { Card, List, Li, Checkbox, Datepicker, Textarea, Select } from 'flowbite-svelte';
    import { Sidebar, SidebarGroup, SidebarItem, SidebarWrapper, Alert } from 'flowbite-svelte';
    import { NewspaperSolid, EnvelopeSolid, ClipboardListSolid, MicrophoneSolid, UsersGroupSolid, EditSolid, ProfileCardSolid } from 'flowbite-svelte-icons';
    import { onMount } from 'svelte';
	import { enhance } from '$app/forms';
    import * as m from '$lib/paraglide/messages.js';

    import RegistrationForm from '$lib/components/RegistrationForm.svelte';
    import EventAdminForm from '$lib/components/EventAdminForm.svelte';
    import EventInformation from '$lib/components/EventInformation.svelte';
    import EmailTemplates from '$lib/components/EmailTemplates.svelte';
    import EventSpecificQuestions from '$lib/components/EventSpecificQuestions.svelte';
    import Speakers from '$lib/components/Speakers.svelte';
    import Attendees from '$lib/components/Attendees.svelte';
    import OnSiteAttendees from '$lib/components/OnSiteAttendees.svelte';
    import Abstracts from '$lib/components/Abstracts.svelte';
    import EventAdmins from '$lib/components/EventAdmins.svelte';

    let { data } = $props();

    let nonActiveClass = 'flex items-center p-2 text-base font-normal text-gray-900 rounded-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700';
    let activeClass = 'flex items-center p-2 text-base font-normal text-primary-900 bg-primary-200 dark:bg-primary-700 rounded-lg dark:text-white hover:bg-primary-100 dark:hover:bg-gray-700';
    let sidebar_selected = $state('event_information');
    const setAdminPage = () => {
        if (!location.hash) {
            sidebar_selected = 'event_information';
            return;
        }
        if (location.hash !== '#event_information' &&
            location.hash !== '#email_templates' &&
            location.hash !== '#event_specific_questions' &&
            location.hash !== '#speakers' &&
            location.hash !== '#attendees' &&
            location.hash !== '#abstracts' &&
            location.hash !== '#event_admins' &&
            location.hash !== '#onsite'
        ) {
            location.hash = '#event_information';
            return;
        }
        sidebar_selected = location.hash.slice(1);
        const el = document.getElementById('scroll_here');
        if (el) {
            el.scrollIntoView({ behavior: 'smooth' });
        }
    };

    let show_sidebar = $state(true);

    $effect.pre(() => {
        setAdminPage();
    });
</script>

<svelte:window on:hashchange={setAdminPage}/>

{#snippet process_spaces(text)}
    {@html text.replace(/\n/g, '<br>').replace(/ /g, '&nbsp;')}
{/snippet}

<div class="container mx-auto py-8 px-3 sm:px-7">
    <!-- Page Header Card -->
    <div class="relative rounded-lg shadow-sm py-16 px-8 mb-4 overflow-hidden" style="background-image: url('/bg-events.webp'); background-size: cover; background-position: center;">
        <div class="absolute inset-0 bg-slate-900 opacity-60"></div>
        <div class="relative z-10">
            <h1 class="text-3xl font-bold text-white">{data.event.name}</h1>
            <p class="text-slate-200 mt-2">
                <a href="/events" class="hover:underline">Events</a>
                <span class="mx-2">/</span>
                <a href="/event/{data.event.id}" class="hover:underline">{data.event.name}</a>
                <span class="mx-2">/</span>
                <span class="text-white font-medium">Admin Panel</span>
            </p>
        </div>
    </div>

    <div id="scroll_here">&nbsp;</div>
    <Card size="none" class="!p-0">
        <div class="flex flex-row">
            <div class={"border-r lg:relative fixed bottom-0 top-0 left-0 bg-white z-10" + (show_sidebar ? " w-[292px] md:w-[300px] p-4 sm:p-6" : " w-0 py-4 sm:py-6")}>
                <Sidebar class="sticky py-2 top-0">
                    <Button class={"text-md absolute top-32 bg-gray-50 border" + (show_sidebar? " left-[260px]":" md:-translate-x-1/2")} size="xs" color="none" onclick={() => show_sidebar = !show_sidebar}>
                        {#if show_sidebar}
                            &lsaquo;
                        {:else}
                            &rsaquo;
                        {/if}
                    </Button>
                    {#if show_sidebar}
                    <SidebarGroup>
                        <SidebarItem label={m.eventAdmin_eventInformation()} class={(sidebar_selected === 'event_information')?activeClass:nonActiveClass} href="#event_information">
                            <svelte:fragment slot="icon">
                                <NewspaperSolid class="w-6 h-6" />
                            </svelte:fragment>
                        </SidebarItem>
                        <SidebarItem label={m.eventAdmin_emailTemplates()} class={(sidebar_selected === 'email_templates')?activeClass:nonActiveClass} href="#email_templates">
                            <svelte:fragment slot="icon">
                                <EnvelopeSolid class="w-6 h-6" />
                            </svelte:fragment>
                        </SidebarItem>
                        <SidebarItem label={m.eventAdmin_eventSpecificQuestions()} class={(sidebar_selected === 'event_specific_questions')?activeClass:nonActiveClass} href="#event_specific_questions">
                            <svelte:fragment slot="icon">
                                <ClipboardListSolid class="w-6 h-6" />
                            </svelte:fragment>
                        </SidebarItem>
                        <SidebarItem label={m.eventAdmin_speakers()} class={(sidebar_selected === 'speakers')?activeClass:nonActiveClass} href="#speakers">
                            <svelte:fragment slot="icon">
                                <MicrophoneSolid class="w-6 h-6" />
                            </svelte:fragment>
                        </SidebarItem>
                        <SidebarItem label={m.eventAdmin_attendees()} class={(sidebar_selected === 'attendees')?activeClass:nonActiveClass} href="#attendees">
                            <svelte:fragment slot="icon">
                                <UsersGroupSolid class="w-6 h-6" />
                            </svelte:fragment>
                        </SidebarItem>
                        <SidebarItem label={m.eventAdmin_onsiteAttendees()} class={(sidebar_selected === 'onsite')?activeClass:nonActiveClass} href="#onsite">
                            <svelte:fragment slot="icon">
                                <UsersGroupSolid class="w-6 h-6" />
                            </svelte:fragment>
                        </SidebarItem>
                        <SidebarItem label={m.eventAdmin_abstracts()} class={(sidebar_selected === 'abstracts')?activeClass:nonActiveClass} href="#abstracts">
                            <svelte:fragment slot="icon">
                                <EditSolid class="w-6 h-6" />
                            </svelte:fragment>
                        </SidebarItem>
                        <SidebarItem label={m.eventAdmin_eventAdmins()} class={(sidebar_selected === 'event_admins')?activeClass:nonActiveClass} href="#event_admins">
                            <svelte:fragment slot="icon">
                                <ProfileCardSolid class="w-6 h-6" />
                            </svelte:fragment>
                        </SidebarItem>
                    </SidebarGroup>
                    {/if}
                </Sidebar>
            </div>
            <div class="p-6 sm:p-8 overflow-auto w-full">
                {#if sidebar_selected === 'event_information'}
                <EventInformation data={data} />
                {/if}

                {#if sidebar_selected === 'email_templates'}
                <EmailTemplates data={data} />
                {/if}

                {#if sidebar_selected === 'event_specific_questions'}
                <EventSpecificQuestions data={data} />
                {/if}

                {#if sidebar_selected === 'speakers'}
                <Speakers data={data} />
                {/if}

                {#if sidebar_selected === 'attendees'}
                <Attendees data={data} />
                {/if}

                {#if sidebar_selected === 'onsite'}
                <OnSiteAttendees data={data} />
                {/if}

                {#if sidebar_selected === 'abstracts'}
                <Abstracts data={data} />
                {/if}

                {#if sidebar_selected === 'event_admins'}
                <EventAdmins data={data} />
                {/if}
            </div>
        </div>
    </Card>
</div>
