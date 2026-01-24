<script>
    import { Button, Card, Heading } from 'flowbite-svelte';
    import { MapPinAltSolid, FacebookSolid, TwitterSolid, LinkedinSolid, EnvelopeSolid } from 'flowbite-svelte-icons';

    let { data } = $props();
    let event = data.event;
    let user = data.user;
    let registered = data.registered;
</script>

<!-- Hero Section -->
<div class="relative flex justify-center items-center overflow-hidden h-[400px]">
    <div class="absolute flex w-full h-full bg-darken">
        <img alt={event.name} src="/bg-default.webp" class="absolute block !w-full h-full object-cover z-0">
    </div>
    <div class="relative container px-7">
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">{event.name}</h1>
    </div>
</div>

<!-- Main Content -->
<div class="container mx-auto my-10 px-3 sm:px-7">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Column - Main Content -->
        <div class="lg:col-span-2 space-y-8">
            <!-- About the Event -->
            <Card>
                <Heading tag="h2" class="mb-4">About the Event</Heading>
                <div class="space-y-4 text-gray-700">
                    <p><strong>Organizer:</strong> {event.organizers}</p>
                    <p><strong>Venue:</strong> {event.venue}</p>
                    <p><strong>Dates:</strong> {event.start_date} - {event.end_date}</p>
                    {#if event.registration_deadline}
                        <p><strong>Registration Deadline:</strong> {event.registration_deadline}</p>
                    {/if}
                    {#if event.abstract_deadline && event.accepts_abstract}
                        <p><strong>Abstract Submission Deadline:</strong> {event.abstract_deadline}</p>
                    {/if}
                    {#if event.link_info}
                        <p>
                            <a href={event.link_info} target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:underline">
                                Visit Event Website →
                            </a>
                        </p>
                    {/if}
                </div>
            </Card>

            <!-- Speakers Section (if available) -->
            {#if data.speakers && data.speakers.length > 0}
            <Card>
                <Heading tag="h2" class="mb-6">Keynote Speakers</Heading>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {#each data.speakers.slice(0, 6) as speaker}
                        <div class="text-center">
                            <div class="w-24 h-24 mx-auto mb-3 rounded-full bg-gray-300 flex items-center justify-center text-2xl font-bold text-gray-600">
                                {speaker.name.split(' ').map(n => n[0]).join('')}
                            </div>
                            <h3 class="font-semibold text-gray-900">{speaker.name}</h3>
                            {#if speaker.affiliation}
                                <p class="text-sm text-gray-600">{speaker.affiliation}</p>
                            {/if}
                            <p class="text-xs text-gray-500 mt-1 capitalize">{speaker.type.replace('_', ' ')}</p>
                        </div>
                    {/each}
                </div>
            </Card>
            {/if}

            <!-- Conference Schedule -->
            <Card>
                <Heading tag="h2" class="mb-4">Conference Schedule</Heading>
                <div class="space-y-4">
                    <div class="border-l-4 border-blue-600 pl-4">
                        <p class="font-semibold text-gray-900">Day 1: {event.start_date}</p>
                        <p class="text-gray-600 text-sm">Opening Ceremony & Sessions</p>
                    </div>
                    {#if event.start_date !== event.end_date}
                        <div class="border-l-4 border-blue-600 pl-4">
                            <p class="font-semibold text-gray-900">Day 2: {event.end_date}</p>
                            <p class="text-gray-600 text-sm">Workshops, Networking & Closing</p>
                        </div>
                    {/if}
                </div>
            </Card>
        </div>

        <!-- Right Column - Sidebar -->
        <div class="space-y-6">
            <!-- Registration Information -->
            <Card class="bg-gray-50">
                <Heading tag="h3" class="mb-4">Registration Information</Heading>

                {#if user && registered}
                    <div class="space-y-4">
                        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                            <p class="font-semibold">✓ You are registered!</p>
                            <p class="text-sm mt-1">Thank you for joining us.</p>
                        </div>
                        {#if event.accepts_abstract}
                            <Button href="/event/{event.id}/abstract" color="primary" class="w-full">
                                Submit an Abstract
                            </Button>
                        {/if}
                        <Button href="/event/{event.id}" color="alternative" class="w-full">
                            View My Registration
                        </Button>
                    </div>
                {:else}
                    <div class="space-y-4">
                        <div>
                            <p class="text-sm text-gray-600">Capacity</p>
                            <p class="text-2xl font-bold text-gray-900">{event.capacity} attendees</p>
                        </div>

                        {#if event.registration_deadline}
                            <div>
                                <p class="text-sm text-gray-600">Registration Deadline</p>
                                <p class="font-semibold text-gray-900">{event.registration_deadline}</p>
                            </div>
                        {/if}

                        {#if user}
                            <Button href="/event/{event.id}/register" color="primary" size="lg" class="w-full">
                                Register Now
                            </Button>
                        {:else}
                            <Button href="/login" color="primary" size="lg" class="w-full">
                                Login to Register
                            </Button>
                            <p class="text-xs text-center text-gray-600">
                                Don't have an account?
                                <a href="/registration" class="text-blue-600 hover:underline">Sign up here</a>
                            </p>
                        {/if}
                    </div>
                {/if}
            </Card>

            <!-- Location -->
            <Card>
                <Heading tag="h3" class="mb-3 flex items-center gap-2">
                    <MapPinAltSolid class="w-5 h-5" />
                    Location
                </Heading>
                <div class="space-y-3">
                    <p class="text-gray-700">{event.venue}</p>
                    <!-- Map placeholder -->
                    <div class="w-full h-48 bg-gray-200 rounded-lg flex items-center justify-center">
                        <p class="text-gray-500 text-sm">Map</p>
                    </div>
                </div>
            </Card>

            <!-- Share -->
            <Card>
                <Heading tag="h3" class="mb-3">Share</Heading>
                <div class="flex gap-3">
                    <button class="p-2 rounded-full bg-blue-600 text-white hover:bg-blue-700">
                        <FacebookSolid class="w-5 h-5" />
                    </button>
                    <button class="p-2 rounded-full bg-sky-500 text-white hover:bg-sky-600">
                        <TwitterSolid class="w-5 h-5" />
                    </button>
                    <button class="p-2 rounded-full bg-blue-700 text-white hover:bg-blue-800">
                        <LinkedinSolid class="w-5 h-5" />
                    </button>
                    <button class="p-2 rounded-full bg-gray-600 text-white hover:bg-gray-700">
                        <EnvelopeSolid class="w-5 h-5" />
                    </button>
                </div>
            </Card>

            <!-- Contact Organizers -->
            <Card>
                <a href="mailto:contact@example.com" class="text-blue-600 hover:underline font-medium">
                    Contact Organizers
                </a>
            </Card>
        </div>
    </div>
</div>
