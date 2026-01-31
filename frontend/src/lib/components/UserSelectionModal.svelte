<script>
    import { Modal, Label, Input, Button, Alert } from 'flowbite-svelte';
    import { SearchOutline } from 'flowbite-svelte-icons';
    import { enhance } from '$app/forms';
    import { getDisplayInstitute, getDisplayName } from '$lib/utils.js';
    import * as m from '$lib/paraglide/messages.js';

    let {
        open = $bindable(false),
        title,
        userList = [],
        action,
        submitLabel,
        error = $bindable(''),
        onSubmit
    } = $props();

    let searchKeyword = $state('');
    let selectedUserId = $state(null);

    // Filter users based on search keyword
    let filteredUsers = $derived(
        userList.filter(user => {
            if (!searchKeyword.trim()) return true;
            const searchLower = searchKeyword.toLowerCase();
            const name = getDisplayName(user).toLowerCase();
            const institute = getDisplayInstitute(user).toLowerCase();
            const email = (user.email || user.user?.email || '').toLowerCase();
            return name.includes(searchLower) ||
                   institute.includes(searchLower) ||
                   email.includes(searchLower);
        })
    );

    // Reset state when modal closes
    $effect(() => {
        if (!open) {
            searchKeyword = '';
            selectedUserId = null;
            error = '';
        }
    });

    function selectUser(userId) {
        selectedUserId = userId;
    }
</script>

<Modal bind:open={open} {title} size="lg">
    <form method="POST" {action} use:enhance={onSubmit}>
        <input type="hidden" name="id" value={selectedUserId || ''} />

        <div class="mb-4">
            <div class="relative">
                <Input
                    id="search"
                    type="text"
                    bind:value={searchKeyword}
                    placeholder={m.userSelection_searchPlaceholder()}
                    class="pl-10"
                />
                <SearchOutline class="w-4 h-4 absolute left-3 top-3 text-gray-400" />
            </div>
        </div>

        <div class="mb-6">
            <div class="border border-gray-200 rounded-lg max-h-80 overflow-y-auto">
                {#if filteredUsers.length === 0}
                    <div class="p-4 text-center text-gray-500">
                        {m.userSelection_noResults()}
                    </div>
                {:else}
                    {#each filteredUsers as user}
                        <button
                            type="button"
                            onclick={() => selectUser(user.id)}
                            class="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors {selectedUserId === user.id ? 'bg-blue-50 hover:bg-blue-100' : ''}"
                        >
                            <div class="font-medium text-gray-900">{getDisplayName(user)}</div>
                            <div class="text-sm text-gray-600">{getDisplayInstitute(user)}</div>
                            <div class="text-xs text-gray-500">{user.email || user.user?.email || ''}</div>
                        </button>
                    {/each}
                {/if}
            </div>
        </div>

        {#if error}
            <Alert color="red" class="mb-6">{error}</Alert>
        {/if}

        <div class="flex justify-center gap-2">
            <Button color="alternative" type="button" onclick={() => open = false}>{m.common_cancel()}</Button>
            <Button color="primary" type="submit" disabled={!selectedUserId}>{submitLabel}</Button>
        </div>
    </form>
</Modal>
