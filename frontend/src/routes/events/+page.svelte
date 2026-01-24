<script>
    import { Input, Label, Button, Checkbox, Select } from 'flowbite-svelte';
    import { SearchOutline, CalendarMonthOutline, MapPinAltSolid, UserCircleOutline, CheckCircleSolid, ClockOutline } from 'flowbite-svelte-icons';
    import * as m from '$lib/paraglide/messages.js';

    let { data } = $props();
    let events = $state(data.events || []);

    // Filter state
    let searchKeyword = $state('');
    let startDate = $state('');
    let endDate = $state('');
    let showOnlyOpen = $state(false);
    let selectedYear = $state('all');

    // Get available years from events
    let availableYears = $derived(() => {
        const years = new Set();
        events.forEach(event => {
            if (event.start_date) {
                const year = event.start_date.split('-')[0];
                years.add(year);
            }
        });
        return Array.from(years).sort((a, b) => b - a); // Sort descending
    });

    // Filtered events
    let filteredEvents = $derived(() => {
        let result = events;

        // Year filter
        if (selectedYear !== 'all') {
            result = result.filter(event => {
                if (event.start_date) {
                    const year = event.start_date.split('-')[0];
                    return year === selectedYear;
                }
                return false;
            });
        }

        // Keyword filter
        if (searchKeyword.trim()) {
            const keyword = searchKeyword.toLowerCase();
            result = result.filter(event =>
                event.name.toLowerCase().includes(keyword) ||
                event.venue.toLowerCase().includes(keyword) ||
                event.organizers.toLowerCase().includes(keyword)
            );
        }

        // Date filter
        if (startDate) {
            result = result.filter(event => event.start_date >= startDate);
        }
        if (endDate) {
            result = result.filter(event => event.end_date <= endDate);
        }

        // Open/Close filter
        if (showOnlyOpen) {
            const today = new Date().toISOString().split('T')[0];
            result = result.filter(event =>
                (!event.registration_deadline || event.registration_deadline >= today)
            );
        }

        return result;
    });

    function isEventOpen(event) {
        if (!event.registration_deadline) return true;
        const today = new Date().toISOString().split('T')[0];
        return event.registration_deadline >= today;
    }

    function getStatusColor(event) {
        return isEventOpen(event) ? 'text-green-600' : 'text-red-600';
    }

    function getStatusText(event) {
        return isEventOpen(event) ? m.events_registrationOpen() : m.events_registrationClosed();
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
                <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-6 space-y-6">
                    <!-- Keyword Search -->
                    <div>
                        <Label class="mb-2 text-sm font-semibold text-gray-700">{m.events_search()}</Label>
                        <div class="relative">
                            <Input
                                type="text"
                                bind:value={searchKeyword}
                                placeholder={m.events_searchPlaceholder()}
                                class="pl-10"
                            />
                            <SearchOutline class="w-4 h-4 absolute left-3 top-3 text-gray-400" />
                        </div>
                    </div>

                    <!-- Date Range Filter -->
                    <div>
                        <Label class="mb-2 text-sm font-semibold text-gray-700">{m.events_dateRange()}</Label>
                        <div class="space-y-2">
                            <div>
                                <Label class="mb-1 text-xs text-gray-600">{m.events_dateFrom()}</Label>
                                <Input type="date" bind:value={startDate} />
                            </div>
                            <div>
                                <Label class="mb-1 text-xs text-gray-600">{m.events_dateTo()}</Label>
                                <Input type="date" bind:value={endDate} />
                            </div>
                        </div>
                    </div>

                    <!-- Status Filter -->
                    <div>
                        <Label class="mb-2 text-sm font-semibold text-gray-700">{m.events_status()}</Label>
                        <Checkbox bind:checked={showOnlyOpen}>{m.events_showOnlyOpen()}</Checkbox>
                    </div>

                    <!-- Clear Filters -->
                    {#if searchKeyword || startDate || endDate || showOnlyOpen || selectedYear !== 'all'}
                        <Button
                            color="light"
                            class="w-full"
                            on:click={() => {
                                searchKeyword = '';
                                startDate = '';
                                endDate = '';
                                showOnlyOpen = false;
                                selectedYear = 'all';
                            }}
                        >
                            {m.events_clearFilters()}
                        </Button>
                    {/if}
                </div>
            </div>
        </div>

        <!-- Right Content - Events List -->
        <div class="lg:col-span-3">
            <!-- Year Selector -->
            <div class="mb-4 flex items-center gap-4">
                <Label class="text-sm font-semibold text-gray-700 whitespace-nowrap">{m.events_year()}:</Label>
                <Select bind:value={selectedYear} class="w-48">
                    <option value="all">{m.events_allYears()}</option>
                    {#each availableYears() as year}
                        <option value={year}>{year}</option>
                    {/each}
                </Select>
            </div>

            {#if data.user && data.user.is_staff}
                <div class="mb-4">
                    <Button href="/{data.admin_page_name}" size="lg" color="primary">
                        {m.events_manageEvents()}
                    </Button>
                </div>
            {/if}
            <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
                {#if filteredEvents().length === 0}
                    <div class="text-center py-16">
                        <CalendarMonthOutline class="w-16 h-16 mx-auto text-gray-400 mb-4" />
                        <h3 class="text-xl font-semibold text-gray-900 mb-2">{m.events_noResults()}</h3>
                        <p class="text-gray-600">{m.events_noResultsDesc()}</p>
                    </div>
                {:else}
                    <div class="space-y-6">
                        {#each filteredEvents() as event}
                            <div class="py-4 border-b border-gray-200 last:border-b-0">
                                <div class="flex justify-between items-start mb-3">
                                    <a href="/event/{event.id}" class="text-2xl font-bold text-gray-900 underline hover:text-gray-700">
                                        {event.name}
                                    </a>
                                    <span class={`flex items-center gap-1 text-sm font-semibold ${getStatusColor(event)}`}>
                                        {#if isEventOpen(event)}
                                            <CheckCircleSolid class="w-4 h-4" />
                                        {:else}
                                            <ClockOutline class="w-4 h-4" />
                                        {/if}
                                        {getStatusText(event)}
                                    </span>
                                </div>

                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                                    <div class="flex items-start gap-2">
                                        <CalendarMonthOutline class="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
                                        <div>
                                            <p class="font-medium text-gray-900">{m.events_dates()}</p>
                                            <p>{event.start_date} - {event.end_date}</p>
                                            {#if event.registration_deadline}
                                                <p class="text-xs mt-1">
                                                    {m.events_registrationDeadline()}: {event.registration_deadline}
                                                </p>
                                            {/if}
                                        </div>
                                    </div>

                                    <div class="flex items-start gap-2">
                                        <MapPinAltSolid class="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
                                        <div>
                                            <p class="font-medium text-gray-900">{m.events_location()}</p>
                                            <p>{event.venue}</p>
                                        </div>
                                    </div>

                                    <div class="flex items-start gap-2">
                                        <UserCircleOutline class="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
                                        <div>
                                            <p class="font-medium text-gray-900">{m.events_organizer()}</p>
                                            <p>{event.organizers}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        {/each}
                </div>
            {/if}
            </div>
        </div>
    </div>
</div>
