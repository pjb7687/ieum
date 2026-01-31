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
        FileLinesSolid,
        GlobeSolid,
        CreditCardSolid
    } from 'flowbite-svelte-icons';
    import * as m from '$lib/paraglide/messages.js';
    import { languageTag } from '$lib/paraglide/runtime.js';
    import { getDisplayVenue, getDisplayOrganizers, formatDate, formatDateRange } from '$lib/utils.js';
    import { marked } from 'marked';
    import { browser } from '$app/environment';
    import VenueMapWidget from '$lib/components/VenueMapWidget.svelte';

    let DOMPurify;

    // Configure marked options for consistent rendering
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    let { data } = $props();
    let event = data.event;
    let user = data.user;
    let registered = data.registered;
    let is_event_admin = data.is_event_admin;

    // Import DOMPurify only in browser
    $effect(() => {
        if (browser && !DOMPurify) {
            import('dompurify').then(module => {
                DOMPurify = module.default;
            });
        }
    });

    // Parse and sanitize markdown description
    let descriptionHtml = $derived.by(() => {
        if (!event.description) return '';
        const html = marked.parse(event.description);
        // Only sanitize in browser, marked already escapes dangerous content
        if (browser && DOMPurify) {
            return DOMPurify.sanitize(html);
        }
        return html;
    });

    // Check if registration is closed
    let isRegistrationClosed = $derived.by(() => {
        if (!event.registration_deadline) return false;
        const deadline = new Date(event.registration_deadline);
        const now = new Date();
        return deadline < now;
    });

    // Format registration fee based on language
    let formattedRegistrationFee = $derived.by(() => {
        const fee = event.registration_fee || 0;
        if (fee === 0) {
            return m.eventDetail_registrationFeeFree();
        }
        const formattedAmount = fee.toLocaleString('ko-KR', {maximumFractionDigits: 0});
        return languageTag() === 'ko' ? `${formattedAmount} 원` : `KRW ${formattedAmount}`;
    });

    // Get current page URL for sharing
    let pageUrl = $state('');
    $effect(() => {
        if (typeof window !== 'undefined') {
            pageUrl = window.location.href;
        }
    });

    // Share text
    const shareText = `${event.name} - ${formatDateRange(event.start_date, event.end_date)} at ${getDisplayVenue(event)}`;
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
                <a href="/" class="hover:underline">{m.eventDetail_breadcrumbEvents()}</a>
                <span class="mx-2">/</span>
                <span class="text-white font-medium">{event.name}</span>
            </p>
        </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-3 2xl:grid-cols-4 gap-6">
        <!-- Left Column - Main Content -->
        <div class="lg:col-span-2 2xl:col-span-3 space-y-6">
            <!-- Event Details -->
            <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-8">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Dates -->
                    <div class="flex items-start gap-3">
                        <CalendarMonthSolid class="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                        <div class="flex-1">
                            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{m.eventDetail_eventDates()}</p>
                            <p class="text-sm text-gray-900 font-medium">{formatDateRange(event.start_date, event.end_date)}</p>
                            {#if event.registration_deadline}
                                <p class="text-xs text-gray-600 mt-1.5">
                                    <span class="font-medium">{m.eventDetail_registrationDeadline()}:</span> {formatDate(event.registration_deadline)}
                                </p>
                            {/if}
                            {#if event.abstract_deadline && event.accepts_abstract}
                                <p class="text-xs text-gray-600 mt-1.5">
                                    <span class="font-medium">{m.eventDetail_abstractDeadline()}:</span> {formatDate(event.abstract_deadline)}
                                </p>
                            {/if}
                        </div>
                    </div>

                    <!-- Venue -->
                    <div class="flex items-start gap-3">
                        <MapPinAltSolid class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                        <div class="flex-1">
                            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{m.eventDetail_venue()}</p>
                            <p class="text-sm text-gray-900 font-medium">{getDisplayVenue(event)}</p>
                            {#if event.venue_address}
                                <p class="text-xs text-gray-600 mt-1">{event.venue_address}</p>
                            {/if}
                        </div>
                    </div>

                    <!-- Organizer -->
                    <div class="flex items-start gap-3">
                        <UsersSolid class="w-5 h-5 text-purple-500 mt-0.5 flex-shrink-0" />
                        <div class="flex-1">
                            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{m.eventDetail_organizer()}</p>
                            <p class="text-sm text-gray-900 font-medium">{getDisplayOrganizers(event)}</p>
                        </div>
                    </div>

                    <!-- Main Languages -->
                    {#if event.main_languages && event.main_languages.length > 0}
                    <div class="flex items-start gap-3">
                        <GlobeSolid class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                        <div class="flex-1">
                            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{m.eventDetail_mainLanguages()}</p>
                            <p class="text-sm text-gray-900 font-medium">
                                {event.main_languages.map(lang => lang === 'ko' ? m.language_korean() : m.language_english()).join(', ')}
                            </p>
                        </div>
                    </div>
                    {/if}
                </div>

                {#if descriptionHtml}
                    <div class="prose prose-gray prose-sm max-w-none mt-6 pt-6 border-t border-gray-200">
                        {@html descriptionHtml}
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
                            <Button href="/event/{event.id}/abstract" color="primary" size="lg" class="w-full">
                                {m.eventDetail_submitAbstract()}
                            </Button>
                        {/if}
                        <Button href="/event/{event.id}/registration" color="alternative" size="lg" class="w-full">
                            {m.eventDetail_viewRegistration()}
                        </Button>
                        {#if is_event_admin}
                            <Button href="/event/{event.id}/admin" color="primary" size="lg" class="w-full">
                                {m.eventDetail_manageEvent()}
                            </Button>
                        {/if}
                    </div>
                {:else}
                    <div class="space-y-4">
                        {#if isRegistrationClosed}
                            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                                <p class="font-semibold">{m.eventRegister_closed()}</p>
                            </div>
                        {:else if user}
                            <div class="flex justify-between items-center">
                                <span class="text-base font-medium text-gray-700">{m.eventDetail_registrationFee()}</span>
                                <span class="{languageTag() === 'ko' ? 'text-xl' : 'text-lg'} font-bold text-gray-900">{formattedRegistrationFee}</span>
                            </div>
                            <Button href="/event/{event.id}/register" color="primary" size="lg" class="w-full">
                                {m.eventDetail_registerNow()}
                            </Button>
                        {:else}
                            <div class="flex justify-between items-center">
                                <span class="text-base font-medium text-gray-700">{m.eventDetail_registrationFee()}</span>
                                <span class="{languageTag() === 'ko' ? 'text-xl' : 'text-lg'} font-bold text-gray-900">{formattedRegistrationFee}</span>
                            </div>
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
                <hr class="my-6 border-gray-200" />
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

            <!-- Location Map -->
            <VenueMapWidget
                venueName={getDisplayVenue(event)}
                venueAddress={event.venue_address}
                venueLatitude={event.venue_latitude}
                venueLongitude={event.venue_longitude}
            />
        </div>
    </div>
</div>
