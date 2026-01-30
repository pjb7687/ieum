<script>
    import { Button, Alert, Checkbox } from 'flowbite-svelte';
    import { UserCircleSolid, FileLinesSolid, ClipboardListSolid } from 'flowbite-svelte-icons';
    import * as m from '$lib/paraglide/messages.js';
    import { languageTag } from '$lib/paraglide/runtime.js';

    let { data } = $props();
    let event = data.event;
    let attendee = data.attendee;
    let my_abstract = data.my_abstract;

    // Determine which languages are included in the event
    const hasEnglish = event.main_languages && event.main_languages.includes('en');
    const hasKorean = event.main_languages && event.main_languages.includes('ko');

    // Display based on event language
    const currentLang = languageTag();
    const showEnglishName = hasEnglish; // Always show English name if event has English
    const showKoreanName = hasKorean || currentLang === 'ko'; // Show Korean if event has Korean OR UI is Korean

    // Helper to get nationality display text
    function getNationalityText(nationality) {
        switch(nationality) {
            case 1: return m.nationality_korean();
            case 2: return m.nationality_nonKorean();
            default: return m.nationality_notSpecified();
        }
    }

    // Parse checkbox answer format: "- option1: value\n- option2: value"
    function parseCheckboxAnswer(answer) {
        const lines = answer.split('\n');
        return lines.map(line => {
            const match = line.match(/^-\s*(.+?):\s*(.+)$/);
            if (match) {
                return {
                    option: match[1],
                    checked: match[2] === 'on' || match[2] === 'true' || match[2] === 'checked'
                };
            }
            return null;
        }).filter(item => item !== null);
    }
</script>

<div class="container mx-auto my-10 px-3 sm:px-7">
    <!-- Page Header Card -->
    <div class="relative rounded-lg shadow-sm py-16 px-8 mb-8 overflow-hidden" style="background-image: url('/bg-events.webp'); background-size: cover; background-position: center;">
        <div class="absolute inset-0 bg-slate-900 opacity-60"></div>
        <div class="relative z-10">
            <h1 class="text-3xl font-bold text-white">{m.myRegistration_title()}</h1>
            <p class="text-slate-200 mt-2">
                <a href="/" class="hover:underline">{m.eventDetail_breadcrumbEvents()}</a>
                <span class="mx-2">/</span>
                <a href="/event/{event.id}" class="hover:underline">{event.name}</a>
                <span class="mx-2">/</span>
                <span class="text-white font-medium">{m.myRegistration_title()}</span>
            </p>
        </div>
    </div>

    {#if attendee}
        <!-- Registration Details -->
        <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-8 mb-6">
            <div class="mb-6">
                <Alert color="blue" class="mb-0">
                    {m.myRegistration_contactOrganizer()}
                </Alert>
            </div>

            <!-- Personal Information Section -->
            <div class="mb-8">
                <div class="flex items-center gap-2 mb-4">
                    <UserCircleSolid class="w-6 h-6 text-gray-700" />
                    <h2 class="text-xl font-bold text-gray-900">{m.myRegistration_personalInfo()}</h2>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pl-8">
                    {#if showEnglishName}
                        <div>
                            <p class="text-sm font-medium text-gray-500">{m.form_firstName()}</p>
                            <p class="text-base text-gray-900">{attendee.first_name}</p>
                        </div>
                        {#if attendee.middle_initial}
                            <div>
                                <p class="text-sm font-medium text-gray-500">{m.form_middleInitial()}</p>
                                <p class="text-base text-gray-900">{attendee.middle_initial}</p>
                            </div>
                        {/if}
                        <div>
                            <p class="text-sm font-medium text-gray-500">{m.form_lastName()}</p>
                            <p class="text-base text-gray-900">{attendee.last_name}</p>
                        </div>
                    {/if}
                    {#if showKoreanName && attendee.korean_name}
                        <div>
                            <p class="text-sm font-medium text-gray-500">{m.form_koreanName()}</p>
                            <p class="text-base text-gray-900">{attendee.korean_name}</p>
                        </div>
                    {/if}
                    <div>
                        <p class="text-sm font-medium text-gray-500">{m.form_nationality()}</p>
                        <p class="text-base text-gray-900">{getNationalityText(attendee.nationality)}</p>
                    </div>
                    <div>
                        <p class="text-sm font-medium text-gray-500">{m.form_institute()}</p>
                        <p class="text-base text-gray-900">{hasEnglish ? attendee.institute : (showKoreanName && attendee.institute_ko ? attendee.institute_ko : attendee.institute)}</p>
                    </div>
                    {#if attendee.department}
                        <div>
                            <p class="text-sm font-medium text-gray-500">{m.form_department()}</p>
                            <p class="text-base text-gray-900">{attendee.department}</p>
                        </div>
                    {/if}
                    {#if attendee.job_title}
                        <div>
                            <p class="text-sm font-medium text-gray-500">{m.form_jobTitle()}</p>
                            <p class="text-base text-gray-900">{attendee.job_title}</p>
                        </div>
                    {/if}
                    {#if attendee.disability}
                        <div>
                            <p class="text-sm font-medium text-gray-500">{m.form_disability()}</p>
                            <p class="text-base text-gray-900">{attendee.disability}</p>
                        </div>
                    {/if}
                    {#if attendee.dietary}
                        <div>
                            <p class="text-sm font-medium text-gray-500">{m.form_dietary()}</p>
                            <p class="text-base text-gray-900">{attendee.dietary}</p>
                        </div>
                    {/if}
                </div>
            </div>

            <!-- Event-Specific Answers Section -->
            {#if attendee.custom_answers && attendee.custom_answers.length > 0}
                <div class="pt-6 border-t border-gray-200">
                    <div class="flex items-center gap-2 mb-4">
                        <ClipboardListSolid class="w-6 h-6 text-gray-700" />
                        <h2 class="text-xl font-bold text-gray-900">{m.myRegistration_eventSpecificAnswers()}</h2>
                    </div>
                    <div class="space-y-4 pl-8">
                        {#each attendee.custom_answers as answer}
                            <div>
                                <p class="text-sm font-medium text-gray-500 mb-2">{answer.question}</p>
                                {#if answer.reference?.question?.type === 'checkbox'}
                                    <div class="space-y-2">
                                        {#each parseCheckboxAnswer(answer.answer) as item}
                                            <Checkbox checked={item.checked} disabled>{item.option}</Checkbox>
                                        {/each}
                                    </div>
                                {:else}
                                    <p class="text-base text-gray-900">{answer.answer}</p>
                                {/if}
                            </div>
                        {/each}
                    </div>
                </div>
            {/if}
        </div>

        <!-- Abstract Information -->
        {#if event.accepts_abstract}
            <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-8">
                <div class="flex items-center gap-2 mb-4">
                    <FileLinesSolid class="w-6 h-6 text-gray-700" />
                    <h2 class="text-xl font-bold text-gray-900">{m.myRegistration_abstractInfo()}</h2>
                </div>

                {#if my_abstract}
                    <div class="space-y-4 pl-8">
                        <div>
                            <p class="text-sm font-medium text-gray-500">{m.myRegistration_abstractTitle()}</p>
                            <p class="text-base text-gray-900">{my_abstract.title}</p>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <p class="text-sm font-medium text-gray-500">{m.myRegistration_abstractType()}</p>
                                <p class="text-base text-gray-900">{my_abstract.is_oral ? m.abstractType_oral() : m.abstractType_poster()}</p>
                            </div>
                            <div>
                                <p class="text-sm font-medium text-gray-500">{m.myRegistration_abstractStatus()}</p>
                                <p class="text-base text-gray-900">{my_abstract.is_accepted ? m.myRegistration_abstractAccepted() : m.myRegistration_abstractPending()}</p>
                            </div>
                            <div>
                                <p class="text-sm font-medium text-gray-500">{m.myRegistration_abstractVotes()}</p>
                                <p class="text-base text-gray-900">{my_abstract.votes}</p>
                            </div>
                        </div>
                        <div class="pt-4">
                            <Button href="/event/{event.id}/abstract" color="primary">{m.myRegistration_viewAbstract()}</Button>
                        </div>
                    </div>
                {:else}
                    <div class="pl-8">
                        <p class="text-gray-600 mb-4">{m.myRegistration_noAbstract()}</p>
                        <Button href="/event/{event.id}/abstract" color="primary">{m.myRegistration_submitAbstract()}</Button>
                    </div>
                {/if}
            </div>
        {/if}

        <!-- Action Buttons -->
        <div class="flex justify-center mt-8">
            <Button href="/event/{event.id}" color="alternative" size="lg">{m.common_goBack()}</Button>
        </div>
    {:else}
        <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-8">
            <Alert color="red">
                Unable to load registration details. Please try again later.
            </Alert>
        </div>
    {/if}
</div>
