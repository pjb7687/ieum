<script>
    import { marked } from 'marked';
    import { Card, Tabs, TabItem, Textarea, Label } from 'flowbite-svelte';
    import * as m from '$lib/paraglide/messages.js';
    import { onMount } from 'svelte';

    let { value = $bindable(), name = '', id = '', label = '', placeholder = '', rows = 10, required = false } = $props();

    let activeTab = $state('edit');
    let DOMPurify = $state(null);
    let previewHtml = $state('');

    // Import DOMPurify only on client side
    onMount(async () => {
        const DOMPurifyModule = await import('dompurify');
        DOMPurify = DOMPurifyModule.default;
    });

    // Configure marked options
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    // Update preview HTML whenever value or DOMPurify changes
    $effect(() => {
        if (!value || !DOMPurify) {
            previewHtml = '';
            return;
        }
        try {
            const rawHtml = marked.parse(value);
            previewHtml = DOMPurify.sanitize(rawHtml);
        } catch (e) {
            console.error('Markdown parsing error:', e);
            previewHtml = '<p class="text-red-500">Error parsing markdown</p>';
        }
    });
</script>

{#if label}
    <Label for={id} class="block mb-2">{label}{#if required} <span class="text-red-500">*</span>{/if}</Label>
{/if}

<Tabs style="underline" bind:activeTabValue={activeTab}>
    <TabItem open={activeTab === 'edit'} title={m.markdownEditor_edit()}>
        <Textarea
            {id}
            {name}
            bind:value={value}
            {placeholder}
            {rows}
            class="font-mono w-full"
        />
        <p class="text-sm text-gray-500 mt-2">{m.markdownEditor_supportsMarkdown()}</p>
    </TabItem>

    <TabItem open={activeTab === 'preview'} title={m.markdownEditor_preview()}>
        <Card size="xl" class="p-4 min-h-[200px] prose prose-sm max-w-none dark:prose-invert">
            {#if value}
                {@html previewHtml}
            {:else}
                <p class="text-gray-400 italic">{m.markdownEditor_noContent()}</p>
            {/if}
        </Card>
    </TabItem>

    <TabItem open={activeTab === 'split'} title={m.markdownEditor_split()}>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <p class="text-sm font-medium mb-2">{m.markdownEditor_edit()}</p>
                <Textarea
                    id="{id}-split"
                    {name}
                    bind:value={value}
                    {placeholder}
                    {rows}
                    class="font-mono w-full"
                />
            </div>
            <div>
                <p class="text-sm font-medium mb-2">{m.markdownEditor_preview()}</p>
                <Card size="xl" class="p-4 min-h-[200px] prose prose-sm max-w-none dark:prose-invert overflow-auto">
                    {#if value && previewHtml}
                        {@html previewHtml}
                    {:else}
                        <p class="text-gray-400 italic">{m.markdownEditor_noContent()}</p>
                    {/if}
                </Card>
            </div>
        </div>
    </TabItem>
</Tabs>
