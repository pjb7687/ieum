<script>
  import { Input, Label, Alert, Modal, Button, ButtonGroup } from 'flowbite-svelte';
  import { SearchOutline } from 'flowbite-svelte-icons';
  import * as m from '$lib/paraglide/messages.js';
  import { enhance } from '$app/forms';

  let { value = $bindable(''), error = null, required = false, institutions = $bindable([]) } = $props();

  let modal_open = $state(false);
  let modal_step = $state('search'); // 'search' or 'create'
  let search_query = $state('');
  let filtered_suggestions = $state([]);
  let new_name_en = $state('');
  let new_name_ko = $state('');
  let create_error = $state('');

  function filterInstitutions() {
    if (!search_query || search_query.length < 2) {
      filtered_suggestions = [];
      return;
    }

    const query = search_query.toLowerCase();
    filtered_suggestions = institutions.filter(inst =>
      inst.name_en.toLowerCase().includes(query) ||
      (inst.name_ko && inst.name_ko.toLowerCase().includes(query))
    ).slice(0, 50); // Limit to 50 results
  }

  function goToCreateStep() {
    modal_step = 'create';
    new_name_en = search_query; // Pre-fill with search query
    create_error = '';
  }

  function goBackToSearch() {
    modal_step = 'search';
    new_name_en = '';
    new_name_ko = '';
    create_error = '';
  }

  function handleSearchInput() {
    filterInstitutions();
  }

  function selectInstitution(institution) {
    value = institution.name_en;
    modal_open = false;
    modal_step = 'search';
    search_query = '';
    filtered_suggestions = [];
  }

  const handleCreateInstitution = () => {
    return async ({ result, update }) => {
      if (result.type === 'success' && result.data?.success) {
        // Add the new institution to the list
        institutions.push(result.data.institution);
        // Set the value to the new institution
        value = result.data.institution.name_en;
        // Close modal and reset
        modal_open = false;
        modal_step = 'search';
        search_query = '';
        filtered_suggestions = [];
        new_name_en = '';
        new_name_ko = '';
        create_error = '';
      } else {
        create_error = result.data?.error || 'Failed to create institution';
      }
    };
  };

  function openModal() {
    modal_open = true;
    modal_step = 'search';
    search_query = value || '';
    if (search_query.length >= 2) {
      filterInstitutions();
    }
  }

  function closeModal() {
    modal_open = false;
    modal_step = 'search';
    search_query = '';
    filtered_suggestions = [];
    new_name_en = '';
    new_name_ko = '';
    create_error = '';
  }
</script>

<Label for="institute" class="block mb-2">
  {m.form_institute()}{required ? '*' : ''}
</Label>
<ButtonGroup class="w-full">
  <Input
    id="institute"
    name="institute"
    type="text"
    bind:value={value}
    readonly
    placeholder={m.form_institutePlaceholder()}
    class="cursor-pointer"
    onclick={openModal}
  />
  <Button color="primary" onclick={openModal} class="min-w-48">
    <SearchOutline class="w-4 h-4 me-2" />
    {m.form_findInstitution()}
  </Button>
</ButtonGroup>

{#if error}
  <Alert color="red" class="mt-3">
    <p class="text-sm">{error}</p>
  </Alert>
{/if}

<Modal title={modal_step === 'search' ? m.form_findInstitution() : m.form_createInstitution()} bind:open={modal_open} size="md" outsideclose>
  <div class="space-y-4">
    {#if modal_step === 'search'}
      <!-- Search Step -->
      <div>
        <Label for="search_institution" class="block mb-2">{m.form_searchInstitution()}</Label>
        <Input
          id="search_institution"
          type="text"
          bind:value={search_query}
          oninput={handleSearchInput}
          placeholder={m.form_institutePlaceholder()}
          autofocus
        />
      </div>

      <!-- Search Results -->
      {#if filtered_suggestions.length > 0}
        <div class="border border-gray-200 rounded-lg overflow-hidden max-h-80 overflow-y-auto">
          {#each filtered_suggestions as suggestion}
            <button
              type="button"
              class="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors"
              onclick={() => selectInstitution(suggestion)}
            >
              <div class="font-medium text-gray-900">{suggestion.name_en}</div>
              {#if suggestion.name_ko}
                <div class="text-sm text-gray-600 mt-1">{suggestion.name_ko}</div>
              {/if}
            </button>
          {/each}
        </div>
      {/if}

      <!-- No Results Message -->
      {#if search_query.length >= 2 && filtered_suggestions.length === 0}
        <div class="border border-gray-200 rounded-lg p-4 bg-gray-50 text-center">
          <p class="text-sm text-gray-600 mb-3">{m.form_noInstitutionsFound()}</p>
          <Button color="primary" onclick={goToCreateStep}>
            {m.form_createInstitution()}
          </Button>
        </div>
      {/if}

      <!-- Instructions -->
      {#if search_query.length < 2}
        <p class="text-sm text-gray-500 text-center py-4">
          {m.form_institutionSearchHint()}
        </p>
      {/if}
    {:else}
      <!-- Create Step -->
      <form id="create_institution_form" method="post" action="?/create_institution" use:enhance={handleCreateInstitution}>
        <div class="space-y-4">
          <div>
            <Label for="new_name_en" class="block mb-2">{m.admin_institutionNameEn()}*</Label>
            <Input
              id="new_name_en"
              name="name_en"
              type="text"
              bind:value={new_name_en}
              placeholder={m.admin_institutionNameEn()}
              required
              autofocus
            />
          </div>
          <div>
            <Label for="new_name_ko" class="block mb-2">{m.admin_institutionNameKo()}</Label>
            <Input
              id="new_name_ko"
              name="name_ko"
              type="text"
              bind:value={new_name_ko}
              placeholder={m.admin_institutionNameKo()}
            />
          </div>
          {#if create_error}
            <Alert color="red">
              <p class="text-sm">{create_error}</p>
            </Alert>
          {/if}
        </div>
      </form>
    {/if}
  </div>

  <svelte:fragment slot="footer">
    <div class="flex justify-between w-full">
      {#if modal_step === 'create'}
        <Button color="alternative" onclick={goBackToSearch}>{m.common_goBack()}</Button>
        <Button color="primary" type="submit" form="create_institution_form">{m.form_createInstitution()}</Button>
      {:else}
        <Button color="alternative" onclick={closeModal}>{m.common_cancel()}</Button>
      {/if}
    </div>
  </svelte:fragment>
</Modal>
