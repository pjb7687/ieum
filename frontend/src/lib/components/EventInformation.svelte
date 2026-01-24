<script>
    import { Alert, Button, Heading } from 'flowbite-svelte';
    import { enhance } from '$app/forms';
    import * as m from '$lib/paraglide/messages.js';

    import EventAdminForm from '$lib/components/EventAdminForm.svelte';

    export let data = {};
    export let success = "";
    export let failure = "";

    const afterSubmit = () => {
        return async ({ result, action, update }) => {
            console.log(result);
            if (result.type === "success") {
                success = result.data.message;
                failure = "";
            } else {
                failure = result.error.message;
                success = "";
            }
        }
    };
</script>

<Heading tag="h2" customSize="text-xl font-bold" class="mb-3">{m.eventInfo_title()}</Heading>
<p class="font-light mb-6">{m.eventInfo_description()}</p>
<form method="POST" action="?/update_event" use:enhance={afterSubmit}>
    <EventAdminForm data={data.event} />
    <div class="mb-6">
        {#if success}
            <Alert color="green">{success}</Alert>
        {/if}
        {#if failure}
            <Alert color="red">{failure}</Alert>
        {/if}
    </div>
    <div class="flex justify-center">
        <Button color="primary" type="submit" size="lg">{m.eventInfo_update()}</Button>
    </div>
</form>