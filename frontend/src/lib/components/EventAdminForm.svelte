<script>
    import { Label, Input, Select, Checkbox } from 'flowbite-svelte';
    import * as m from '$lib/paraglide/messages.js';
    import MarkdownEditor from '$lib/components/MarkdownEditor.svelte';
    import VenueSelector from '$lib/components/VenueSelector.svelte';

    let { data = $bindable({
        name: '',
        description: '',
        category: 'conference',
        organizers: '',
        venue: '',
        venue_address: '',
        venue_latitude: null,
        venue_longitude: null,
        main_languages: [],
        start_date: '',
        end_date: '',
        deadline: '',
        capacity: 0,
        accepts_abstract: false,
        abstract_deadline: '',
        capacity_abstract: 0,
        max_votes: 2,
    }) } = $props();

    // Create local reactive state for properties to enable two-way binding
    let description = $state(data.description);
    let category = $state(data.category);
    let venue = $state(data.venue);
    let venue_address = $state(data.venue_address);
    let venue_latitude = $state(data.venue_latitude);
    let venue_longitude = $state(data.venue_longitude);
    let main_languages = $state(data.main_languages || []);
    let accepts_abstract = $state(data.accepts_abstract);

    // Keep properties in sync with data object
    $effect(() => {
        data.description = description;
        data.category = category;
        data.venue = venue;
        data.venue_address = venue_address;
        data.venue_latitude = venue_latitude;
        data.venue_longitude = venue_longitude;
        data.main_languages = main_languages;
        data.accepts_abstract = accepts_abstract;
    });

    // Helper functions for language checkboxes
    function toggleLanguage(lang) {
        if (main_languages.includes(lang)) {
            main_languages = main_languages.filter(l => l !== lang);
        } else {
            main_languages = [...main_languages, lang];
        }
    }
</script>

<div class="mb-6">
    <Label for="name" class="block mb-2">{m.eventForm_eventName()}*</Label>
    <Input type="text" id="name" name="name" value={data.name} />
</div>
<div class="mb-6">
    <Label for="link_info" class="block mb-2">{m.eventForm_eventPageUrl()}*</Label>
    <Input type="text" id="link_info" name="link_info" value={data.link_info} />
</div>
<div class="mb-6">
    <MarkdownEditor
        bind:value={description}
        id="description"
        name="description"
        label={m.eventForm_description()}
        placeholder={m.eventForm_descriptionPlaceholder()}
        rows={8}
    />
</div>
<div class="mb-6">
    <Label for="category" class="block mb-2">{m.eventForm_category()}*</Label>
    <Select id="category" name="category" bind:value={category} items={[
        { value: 'workshop', name: m.eventCategory_workshop() },
        { value: 'hackathon', name: m.eventCategory_hackathon() },
        { value: 'symposium', name: m.eventCategory_symposium() },
        { value: 'meeting', name: m.eventCategory_meeting() },
        { value: 'conference', name: m.eventCategory_conference() }
    ]} />
</div>
<div class="mb-6">
    <Label for="organizers" class="block mb-2">{m.eventForm_organizer()}*</Label>
    <Input type="text" id="organizers" name="organizers" value={data.organizers} />
</div>
<div class="mb-6">
    <Label class="block mb-2">{m.eventForm_mainLanguages()}*</Label>
    <div class="flex gap-4">
        <Checkbox
            checked={main_languages.includes('ko')}
            on:change={() => toggleLanguage('ko')}
        >
            {m.language_korean()}
        </Checkbox>
        <Checkbox
            checked={main_languages.includes('en')}
            on:change={() => toggleLanguage('en')}
        >
            {m.language_english()}
        </Checkbox>
    </div>
    {#if main_languages.length === 0}
        <p class="text-sm text-red-600 mt-2">{m.eventForm_mainLanguagesRequired()}</p>
    {/if}
    <input type="hidden" name="main_languages" value={JSON.stringify(main_languages)} />
</div>
<div class="mb-6">
    <VenueSelector
        bind:venueName={venue}
        bind:venueAddress={venue_address}
        bind:venueLatitude={venue_latitude}
        bind:venueLongitude={venue_longitude}
        required={true}
    />
</div>
<div class="mb-6">
    <Label for="start_date" class="block mb-2">{m.eventForm_dates()}*</Label>
    <div class="flex flex-col md:flex-row justify-stretch gap-4">
        <div class="w-full">
            <Input type="date" id="start_date" name="start_date" value={data.start_date} />
        </div>
        <div class="flex w-3 justify-center items-center">
            <span>-</span>
        </div>
        <div class="w-full">
            <Input type="date" id="end_date" name="end_date" value={data.end_date} />
        </div>
    </div>
</div>
<div class="mb-6">
    <Label for="registration_deadline" class="block mb-2">{m.eventForm_registrationDeadline()}</Label>
    <Input type="date" id="registration_deadline" name="registration_deadline" value={data.registration_deadline} />
    <span class="text-sm">* {m.eventForm_registrationDeadlineHelp()}</span>
</div>
<div class="mb-6">
    <Label for="capacity" class="block mb-2">{m.eventForm_registrationCapacity()}</Label>
    <Input type="number" id="capacity" name="capacity" value={data.capacity} />
    <span class="text-sm">* {m.eventForm_registrationCapacityHelp()}</span>
</div>
<div class="mb-6">
    <Label for="accepts_abstract" class="block mb-2">{m.eventForm_enableAbstract()}</Label>
    <Select id="accepts_abstract" name="accepts_abstract" bind:value={accepts_abstract} items={[
        { value: true, name: m.eventForm_yes() },
        { value: false, name: m.eventForm_no() }
    ]} />
</div>
{#if accepts_abstract}
<div class="mb-6">
    <Label for="abstract_deadline" class="block mb-2">{m.eventForm_abstractDeadline()}</Label>
    <Input type="date" id="abstract_deadline" name="abstract_deadline" value={data.abstract_deadline} />
    <span class="text-sm">* {m.eventForm_abstractDeadlineHelp()}</span>
</div>

<div class="mb-6">
    <Label for="capacity_abstract" class="block mb-2">{m.eventForm_abstractCapacity()}</Label>
    <Input type="number" id="capacity_abstract" name="capacity_abstract" value={data.capacity_abstract} />
    <span class="text-sm">* {m.eventForm_abstractCapacityHelp()}</span>
</div>

<div class="mb-6">
    <Label for="max_votes" class="block mb-2">{m.eventForm_maxVotes()}</Label>
    <Input type="number" id="max_votes" name="max_votes" value={data.max_votes} />
    <span class="text-sm">* {m.eventForm_maxVotesHelp()}</span>
</div>
{/if}