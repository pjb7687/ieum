<script>
    import { Button, Card, Heading } from 'flowbite-svelte';
    import {
        MapPinAltSolid,
        FacebookSolid,
        XSolid,
        LinkedinSolid,
        EnvelopeSolid,
        UsersSolid,
        CalendarMonthSolid,
        ClockSolid,
        FileLinesSolid
    } from 'flowbite-svelte-icons';
    import * as m from '$lib/paraglide/messages.js';

    let { data } = $props();
    let event = data.event;
    let user = data.user;
    let registered = data.registered;
    let is_event_admin = data.is_event_admin;

    // Check if registration is closed
    let isRegistrationClosed = $derived.by(() => {
        if (!event.registration_deadline) return false;
        const deadline = new Date(event.registration_deadline);
        const now = new Date();
        return deadline < now;
    });

    // Get current page URL for sharing
    let pageUrl = $state('');
    $effect(() => {
        if (typeof window !== 'undefined') {
            pageUrl = window.location.href;
        }
    });

    // Share text
    const shareText = `${event.name} - ${event.start_date} to ${event.end_date} at ${event.venue}`;
    const shareTitle = event.name;

    // Share functions
    function shareOnFacebook() {
        const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(pageUrl)}`;
        window.open(url, '_blank', 'width=600,height=400');
    }

    function shareOnX() {
        const url = `https://x.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(pageUrl)}`;
        window.open(url, '_blank', 'width=600,height=400');
    }

    function shareOnLinkedIn() {
        const url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(pageUrl)}`;
        window.open(url, '_blank', 'width=600,height=400');
    }

    function shareViaEmail() {
        const subject = encodeURIComponent(shareTitle);
        const body = encodeURIComponent(`${shareText}\n\nLearn more: ${pageUrl}`);
        window.location.href = `mailto:?subject=${subject}&body=${body}`;
    }
</script>

<div class="container mx-auto my-10 px-3 sm:px-7">
    <!-- Page Header Card -->
    <div class="relative rounded-lg shadow-sm py-16 px-8 mb-8 overflow-hidden" style="background-image: url('/bg-events.webp'); background-size: cover; background-position: center;">
        <div class="absolute inset-0 bg-slate-900 opacity-60"></div>
        <div class="relative z-10">
            <h1 class="text-3xl font-bold text-white">{event.name}</h1>
            <p class="text-slate-200 mt-2">
                <a href="/events" class="hover:underline">{m.eventDetail_breadcrumbEvents()}</a>
                <span class="mx-2">/</span>
                <span class="text-white font-medium">{event.name}</span>
            </p>
        </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Column - Main Content -->
        <div class="lg:col-span-2 space-y-6">
            <!-- Event Details -->
            <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-8">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Organizer -->
                    <div class="flex items-start gap-3">
                        <UsersSolid class="w-5 h-5 text-purple-500 mt-0.5 flex-shrink-0" />
                        <div class="flex-1">
                            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{m.eventDetail_organizer()}</p>
                            <p class="text-sm text-gray-900 font-medium">{event.organizers}</p>
                        </div>
                    </div>

                    <!-- Venue -->
                    <div class="flex items-start gap-3">
                        <MapPinAltSolid class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                        <div class="flex-1">
                            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{m.eventDetail_venue()}</p>
                            <p class="text-sm text-gray-900 font-medium">{event.venue}</p>
                        </div>
                    </div>

                    <!-- Dates -->
                    <div class="flex items-start gap-3">
                        <CalendarMonthSolid class="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                        <div class="flex-1">
                            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{m.eventDetail_eventDates()}</p>
                            <p class="text-sm text-gray-900 font-medium">{event.start_date} - {event.end_date}</p>
                        </div>
                    </div>

                    {#if event.registration_deadline}
                        <!-- Registration Deadline -->
                        <div class="flex items-start gap-3">
                            <ClockSolid class="w-5 h-5 text-orange-500 mt-0.5 flex-shrink-0" />
                            <div class="flex-1">
                                <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{m.eventDetail_registrationDeadline()}</p>
                                <p class="text-sm text-gray-900 font-medium">{event.registration_deadline}</p>
                            </div>
                        </div>
                    {/if}

                    {#if event.abstract_deadline && event.accepts_abstract}
                        <!-- Abstract Submission Deadline -->
                        <div class="flex items-start gap-3">
                            <FileLinesSolid class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                            <div class="flex-1">
                                <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{m.eventDetail_abstractDeadline()}</p>
                                <p class="text-sm text-gray-900 font-medium">{event.abstract_deadline}</p>
                            </div>
                        </div>
                    {/if}
                </div>

                {#if event.description}
                    <div class="prose prose-sm max-w-none mt-6 pt-6 border-t border-gray-200">
                        {@html event.description}
                    </div>
                {/if}
            </div>
        </div>

        <!-- Right Column - Sidebar -->
        <div class="space-y-6">
            <!-- Registration Information -->
            <div class="bg-gray-50 border border-gray-200 rounded-lg shadow-sm p-6">
                {#if user && registered}
                    <div class="space-y-4">
                        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                            <p class="font-semibold">{m.eventDetail_registered()}</p>
                            <p class="text-sm mt-1">{m.eventDetail_registeredThankYou()}</p>
                        </div>
                        {#if event.accepts_abstract}
                            <Button href="/event/{event.id}/abstract" color="primary" class="w-full">
                                {m.eventDetail_submitAbstract()}
                            </Button>
                        {/if}
                        <Button href="/event/{event.id}/registration" color="alternative" class="w-full">
                            {m.eventDetail_viewRegistration()}
                        </Button>
                        {#if is_event_admin}
                            <Button href="/event/{event.id}/admin" color="blue" class="w-full">
                                {m.eventDetail_manageEvent()}
                            </Button>
                        {/if}
                    </div>
                {:else}
                    <div class="space-y-4">
                        {#if event.registration_deadline}
                            <div>
                                <p class="text-sm text-gray-600">{m.eventDetail_registrationDeadline()}</p>
                                <p class="font-semibold text-gray-900">{event.registration_deadline}</p>
                            </div>
                        {/if}

                        {#if isRegistrationClosed}
                            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                                <p class="font-semibold">{m.eventRegister_closed()}</p>
                            </div>
                        {:else if user}
                            <Button href="/event/{event.id}/register" color="primary" size="lg" class="w-full">
                                {m.eventDetail_registerNow()}
                            </Button>
                        {:else}
                            <Button href="/login?next={encodeURIComponent(`/event/${event.id}`)}" color="primary" size="lg" class="w-full">
                                {m.eventDetail_loginToRegister()}
                            </Button>
                            <p class="text-xs text-center text-gray-600">
                                {m.eventDetail_noAccount()}
                                <a href="/registration?next={encodeURIComponent(`/event/${event.id}`)}" class="text-blue-600 hover:underline">{m.eventDetail_signUpHere()}</a>
                            </p>
                        {/if}

                        {#if is_event_admin}
                            <Button href="/event/{event.id}/admin" color="primary" size="lg" class="w-full">
                                {m.eventDetail_manageEvent()}
                            </Button>
                        {/if}
                    </div>
                {/if}
                <hr class="my-6" />
                <div class="flex gap-3">
                    <button onclick={shareOnFacebook} class="p-2 rounded-full bg-blue-600 text-white hover:bg-blue-700" aria-label={m.eventDetail_shareOnFacebook()}>
                        <FacebookSolid class="w-5 h-5" />
                    </button>
                    <button onclick={shareOnX} class="p-2 rounded-full bg-black text-white hover:bg-gray-800" aria-label={m.eventDetail_shareOnX()}>
                        <XSolid class="w-5 h-5" />
                    </button>
                    <button onclick={shareOnLinkedIn} class="p-2 rounded-full bg-blue-700 text-white hover:bg-blue-800" aria-label={m.eventDetail_shareOnLinkedIn()}>
                        <LinkedinSolid class="w-5 h-5" />
                    </button>
                    <button onclick={shareViaEmail} class="p-2 rounded-full bg-gray-600 text-white hover:bg-gray-700" aria-label={m.eventDetail_shareViaEmail()}>
                        <EnvelopeSolid class="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
