<script>
    import { Input, Label, Button, Checkbox, Spinner } from 'flowbite-svelte';
    import { SearchOutline, CalendarMonthOutline, MapPinAltSolid, UserCircleOutline, CheckCircleSolid, ClockOutline } from 'flowbite-svelte-icons';
    import * as m from '$lib/paraglide/messages.js';
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';

    let { data } = $props();

    // Events state - initialize from server data once
    let events = $state(data.eventsData?.events || []);
    let total = $state(data.eventsData?.total || 0);
    let offset = $state(data.eventsData?.events?.length || 0);
    let hasMore = $derived(events.length < total);
    let loading = $state(false);
    let loadingMore = $state(false);

    // Filter state
    let searchKeyword = $state('');
    let showOnlyOpen = $state(false);
    let selectedYear = $state('all');

    // Debounce timer for search
    let searchTimer;

    // Year navigation
    const currentYear = new Date().getFullYear();
    let yearOffset = $state(0);

    // Get years to display (3 years centered on current + offset)
    let displayYears = $derived(() => {
        const centerYear = currentYear + yearOffset;
        return [centerYear - 1, centerYear, centerYear + 1];
    });

    function selectYear(year) {
        selectedYear = year.toString();
        loadEvents(true);
    }

    function navigateYears(direction) {
        yearOffset += direction;
    }

    // Load events from API
    async function loadEvents(reset = false) {
        if (loading || loadingMore) return;

        if (reset) {
            loading = true;
            offset = 0;
        } else {
            loadingMore = true;
        }

        try {
            const queryParams = new URLSearchParams({
                offset: reset ? '0' : offset.toString(),
                limit: '20',
            });

            if (selectedYear !== 'all') queryParams.append('year', selectedYear);
            if (searchKeyword.trim()) queryParams.append('search', searchKeyword.trim());
            if (showOnlyOpen) queryParams.append('showOnlyOpen', 'true');

            const response = await fetch(`/api/events?${queryParams.toString()}`);
            if (response.ok) {
                const data = await response.json();

                if (reset) {
                    events = data.events;
                    offset = data.events.length;
                } else {
                    events = [...events, ...data.events];
                    offset += data.events.length;
                }

                total = data.total;
            }
        } catch (error) {
            console.error('Failed to load events:', error);
        } finally {
            loading = false;
            loadingMore = false;
        }
    }

    // Handle search with debounce
    function handleSearchChange() {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {
            loadEvents(true);
        }, 500);
    }

    // Handle checkbox change
    function handleCheckboxChange() {
        loadEvents(true);
    }

    // Clear all filters
    function clearFilters() {
        searchKeyword = '';
        showOnlyOpen = false;
        selectedYear = 'all';
        yearOffset = 0;
        loadEvents(true);
    }

    // Infinite scroll handler
    let scrollContainer;

    function handleScroll() {
        if (!scrollContainer || loading || loadingMore || !hasMore) return;

        const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
        const scrollPercentage = (scrollTop + clientHeight) / scrollHeight;

        // Load more when scrolled to 80%
        if (scrollPercentage > 0.8) {
            loadEvents(false);
        }
    }

    onMount(() => {
        if (browser) {
            // Find the scrollable container (window or specific element)
            window.addEventListener('scroll', () => {
                if (loading || loadingMore || !hasMore) return;

                const scrollHeight = document.documentElement.scrollHeight;
                const scrollTop = window.scrollY;
                const clientHeight = window.innerHeight;
                const scrollPercentage = (scrollTop + clientHeight) / scrollHeight;

                // Load more when scrolled to 80%
                if (scrollPercentage > 0.8) {
                    loadEvents(false);
                }
            });
        }

        return () => {
            clearTimeout(searchTimer);
        };
    });

    function isEventOpen(event) {
        if (!event.registration_deadline) return true;
        const today = new Date().toISOString().split('T')[0];
        return event.registration_deadline >= today;
    }

    function isClosingSoon(event) {
        if (!event.registration_deadline) return false;
        const today = new Date();
        const deadline = new Date(event.registration_deadline);
        const daysUntilDeadline = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24));
        return daysUntilDeadline > 0 && daysUntilDeadline <= 7;
    }

    function getStatusColor(event) {
        if (!isEventOpen(event)) return 'text-red-600';
        if (isClosingSoon(event)) return 'text-orange-600';
        return 'text-green-600';
    }

    function getStatusText(event) {
        if (!isEventOpen(event)) return m.events_registrationClosed();
        if (isClosingSoon(event)) return m.events_registrationClosingSoon();
        return m.events_registrationOpen();
    }

    // Highlight matched text in search results
    function highlightText(text, keyword) {
        if (!keyword || !keyword.trim()) return text;

        const regex = new RegExp(`(${keyword.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
    }
</script>

<div class="container mx-auto my-10 px-3 sm:px-7">
        <!-- Page Header Card -->
        <div class="relative rounded-lg shadow-sm py-16 px-8 mb-4 overflow-hidden" style="background-image: url('/bg-events.webp'); background-size: cover; background-position: center;">
            <div class="absolute inset-0 bg-slate-900 opacity-60"></div>
            <div class="relative z-10">
                <h1 class="text-3xl font-bold text-white">{m.events_browse()}</h1>
                <p class="text-slate-200 mt-2">{m.events_discover()}</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <!-- Left Sidebar - Filters -->
        <div class="lg:col-span-1">
            <div class="sticky top-8">
                <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-8 space-y-6">
                    <!-- Keyword Search -->
                    <div>
                        <Label class="mb-2 text-sm font-semibold text-gray-700">{m.events_search()}</Label>
                        <div class="relative">
                            <Input
                                type="text"
                                bind:value={searchKeyword}
                                oninput={handleSearchChange}
                                placeholder={m.events_searchPlaceholder()}
                                class="pl-10"
                            />
                            <SearchOutline class="w-4 h-4 absolute left-3 top-3 text-gray-400" />
                        </div>
                    </div>

                    <!-- Year Selector -->
                    <div>
                        <Label class="mb-3 text-sm font-semibold text-gray-700">{m.events_year()}</Label>
                        <div class="flex items-center justify-between gap-2">
                            <button
                                type="button"
                                onclick={() => navigateYears(-1)}
                                class="p-1 hover:bg-gray-100 rounded transition-colors"
                                aria-label="Previous years"
                            >
                                <span class="text-gray-600 font-bold text-lg">&lt;</span>
                            </button>
                            <div class="flex items-center gap-2 flex-1 justify-center">
                                {#each displayYears() as year}
                                    <button
                                        type="button"
                                        onclick={() => selectYear(year)}
                                        class={`px-3 py-1 text-sm rounded transition-colors cursor-pointer
                                            ${selectedYear === year.toString() ? 'bg-blue-600 text-white font-bold' : 'hover:bg-gray-100 text-gray-600'}
                                            ${year === currentYear && selectedYear !== year.toString() ? 'font-bold text-gray-900' : ''}
                                        `}
                                    >
                                        {year}
                                    </button>
                                {/each}
                            </div>
                            <button
                                type="button"
                                onclick={() => navigateYears(1)}
                                class="p-1 hover:bg-gray-100 rounded transition-colors"
                                aria-label="Next years"
                            >
                                <span class="text-gray-600 font-bold text-lg">&gt;</span>
                            </button>
                        </div>
                    </div>

                    <!-- Status Filter -->
                    <div>
                        <Label class="mb-2 text-sm font-semibold text-gray-700">{m.events_status()}</Label>
                        <Checkbox bind:checked={showOnlyOpen} onchange={handleCheckboxChange}>{m.events_showOnlyOpen()}</Checkbox>
                    </div>

                    <!-- Clear Filters -->
                    {#if searchKeyword || showOnlyOpen || selectedYear !== 'all'}
                        <Button
                            color="light"
                            class="w-full"
                            onclick={clearFilters}
                        >
                            {m.events_clearFilters()}
                        </Button>
                    {/if}
                </div>
            </div>
        </div>

        <!-- Right Content - Events List -->
        <div class="lg:col-span-3">
            <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-8">
                {#if loading}
                    <div class="text-center py-16">
                        <Spinner size="12" />
                        <p class="text-gray-600 mt-4">Loading events...</p>
                    </div>
                {:else if events.length === 0}
                    <div class="text-center py-16">
                        <CalendarMonthOutline class="w-16 h-16 mx-auto text-gray-400 mb-4" />
                        <h3 class="text-xl font-semibold text-gray-900 mb-2">{m.events_noResults()}</h3>
                        <p class="text-gray-600">{m.events_noResultsDesc()}</p>
                    </div>
                {:else}
                    <div class="space-y-8">
                        {#each events as event}
                            <div class="pb-8 border-b border-gray-200 last:border-b-0 last:pb-0">
                                <!-- Event Title and Status -->
                                <div class="flex justify-between items-start gap-4 mb-4">
                                    <a href="/event/{event.id}" class="text-2xl font-bold text-gray-900 hover:underline">
                                        {@html highlightText(event.name, searchKeyword)}
                                    </a>
                                    <span class={`flex items-center gap-1.5 text-sm font-semibold whitespace-nowrap ${getStatusColor(event)}`}>
                                        {#if !isEventOpen(event)}
                                            <ClockOutline class="w-4 h-4" />
                                        {:else if isClosingSoon(event)}
                                            <ClockOutline class="w-4 h-4" />
                                        {:else}
                                            <CheckCircleSolid class="w-4 h-4" />
                                        {/if}
                                        {getStatusText(event)}
                                    </span>
                                </div>

                                <!-- Event Details Grid -->
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <!-- Dates -->
                                    <div class="flex items-start gap-3">
                                        <CalendarMonthOutline class="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                                        <div class="flex-1">
                                            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{m.events_dates()}</p>
                                            <p class="text-sm text-gray-900 font-medium">{event.start_date} - {event.end_date}</p>
                                            {#if event.registration_deadline}
                                                <p class="text-xs text-gray-600 mt-1.5">
                                                    <span class="font-medium">{m.events_registrationDeadline()}:</span> {event.registration_deadline}
                                                </p>
                                            {/if}
                                        </div>
                                    </div>

                                    <!-- Location -->
                                    <div class="flex items-start gap-3">
                                        <MapPinAltSolid class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                                        <div class="flex-1">
                                            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{m.events_location()}</p>
                                            <p class="text-sm text-gray-900 font-medium">{@html highlightText(event.venue, searchKeyword)}</p>
                                        </div>
                                    </div>

                                    <!-- Organizer -->
                                    <div class="flex items-start gap-3 md:col-span-2">
                                        <UserCircleOutline class="w-5 h-5 text-purple-500 mt-0.5 flex-shrink-0" />
                                        <div class="flex-1">
                                            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{m.events_organizer()}</p>
                                            <p class="text-sm text-gray-900 font-medium">{@html highlightText(event.organizers, searchKeyword)}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        {/each}

                        <!-- Load More Indicator -->
                        {#if loadingMore}
                            <div class="text-center py-8">
                                <Spinner size="8" />
                                <p class="text-gray-600 mt-2 text-sm">Loading more events...</p>
                            </div>
                        {:else if hasMore}
                            <div class="text-center py-8">
                                <p class="text-gray-500 text-sm">Scroll down to load more events</p>
                            </div>
                        {/if}
                    </div>
                {/if}
            </div>
        </div>
    </div>
</div>
