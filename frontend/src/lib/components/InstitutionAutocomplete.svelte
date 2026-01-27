<script>
  import { Input, Label, Alert } from 'flowbite-svelte';
  import * as m from '$lib/paraglide/messages.js';

  let { value = $bindable(''), error = null, required = false } = $props();

  let suggestions = $state([]);
  let showSuggestions = $state(false);
  let loading = $state(false);
  let searchTimeout;
  let selectedInstitution = $state(null);

  async function searchInstitutions(query) {
    if (!query || query.length < 2) {
      suggestions = [];
      showSuggestions = false;
      return;
    }

    loading = true;
    try {
      const response = await fetch(`/api/institutions?search=${encodeURIComponent(query)}`);
      if (response.ok) {
        suggestions = await response.json();
        showSuggestions = true;
      }
    } catch (err) {
      console.error('Failed to search institutions:', err);
    } finally {
      loading = false;
    }
  }

  function handleInput() {
    clearTimeout(searchTimeout);
    selectedInstitution = null;

    searchTimeout = setTimeout(() => {
      searchInstitutions(value);
    }, 300);
  }

  function selectInstitution(institution) {
    selectedInstitution = institution;
    value = institution.name_en;
    showSuggestions = false;
  }

  function handleBlur() {
    setTimeout(() => {
      showSuggestions = false;
    }, 200);
  }

  function handleFocus() {
    if (suggestions.length > 0) {
      showSuggestions = true;
    }
  }
</script>

<Label for="institute" class="block mb-2">
  {m.form_institute()}{required ? '*' : ''}
</Label>
<div class="relative">
  <Input
    id="institute"
    name="institute"
    type="text"
    bind:value={value}
    oninput={handleInput}
    onblur={handleBlur}
    onfocus={handleFocus}
    placeholder={m.form_institutePlaceholder()}
    autocomplete="off"
  />

  {#if showSuggestions && suggestions.length > 0}
    <div class="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
      {#each suggestions as suggestion}
        <button
          type="button"
          class="w-full text-left px-4 py-2 hover:bg-gray-100 border-b border-gray-100 last:border-b-0"
          onclick={() => selectInstitution(suggestion)}
        >
          <div class="font-medium text-gray-900">{suggestion.name_en}</div>
          {#if suggestion.name_ko}
            <div class="text-sm text-gray-600">{suggestion.name_ko}</div>
          {/if}
        </button>
      {/each}
    </div>
  {/if}

  {#if loading}
    <div class="absolute right-3 top-3">
      <svg class="animate-spin h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
  {/if}
</div>

{#if !selectedInstitution && value.length >= 2}
  <p class="text-xs text-gray-500 mt-1">
    {m.form_institutionWillBeCreated()}
  </p>
{/if}

{#if error}
  <Alert color="red" class="mt-3">
    <p class="text-sm">{error}</p>
  </Alert>
{/if}
