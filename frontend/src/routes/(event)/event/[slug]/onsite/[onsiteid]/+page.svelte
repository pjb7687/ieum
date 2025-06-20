<script>
    import { Heading } from 'flowbite-svelte';
    export let data;
    const onsiteid = data.onsiteid;
</script>

<main>
    <Heading tag="h1" customSize="text-2xl font-bold" class="mb-3">On-site Registration</Heading>
    <p class="mb-10 font-light">Thank you so much for the registration. Your on-site registration is complete.</p>
    <p class="text-center">Your on-site registration ID is <span class="font-bold">{onsiteid}</span>.</p>
</main>