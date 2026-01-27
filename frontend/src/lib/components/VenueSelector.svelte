<script>
  import { Input, Label, Alert, Modal, Button } from 'flowbite-svelte';
  import { MapPinAltSolid } from 'flowbite-svelte-icons';
  import * as m from '$lib/paraglide/messages.js';
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';

  let {
    venueName = $bindable(''),
    venueAddress = $bindable(''),
    venueLatitude = $bindable(null),
    venueLongitude = $bindable(null),
    error = null,
    required = false
  } = $props();

  let mapContainer;
  let map;
  let marker;
  let searchInput = $state('');
  let predictions = $state([]);
  let showPredictions = $state(false);
  let modal_open = $state(false);
  let loadError = $state('');

  // Load Google Maps API
  onMount(() => {
    if (!browser) return;

    // Check if Google Maps is already loaded or loading
    if (window.__GOOGLE_MAPS_LOADED__ || window.__GOOGLE_MAPS_LOADING__) {
      return;
    }

    // Check if Google Maps is already available
    if (window.google && window.google.maps) {
      window.__GOOGLE_MAPS_LOADED__ = true;
      return;
    }

    // Mark as loading to prevent duplicate script injection
    window.__GOOGLE_MAPS_LOADING__ = true;

    // Load Google Maps API with Places and Marker libraries
    const script = document.createElement('script');
    const apiKey = import.meta.env.GOOGLE_MAPS_API_KEY || 'YOUR_GOOGLE_MAPS_API_KEY';
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places,marker&loading=async`;
    script.async = true;
    script.defer = true;

    script.onload = () => {
      window.__GOOGLE_MAPS_LOADED__ = true;
      window.__GOOGLE_MAPS_LOADING__ = false;
    };

    script.onerror = () => {
      loadError = 'Failed to load Google Maps API. Please check your API key.';
      window.__GOOGLE_MAPS_LOADING__ = false;
    };

    document.head.appendChild(script);
  });

  function initializeMap() {
    if (!mapContainer) return;

    // Wait for Google Maps API to be fully loaded
    if (!window.google || !window.google.maps || !window.google.maps.Map || !window.google.maps.marker?.AdvancedMarkerElement) {
      loadError = 'Google Maps API is still loading. Please wait...';
      // Retry after a short delay
      setTimeout(() => {
        loadError = '';
        initializeMap();
      }, 500);
      return;
    }

    try {
      // Initialize map
      const center = venueLatitude && venueLongitude
        ? { lat: venueLatitude, lng: venueLongitude }
        : { lat: 37.5665, lng: 126.9780 }; // Default to Seoul

      map = new google.maps.Map(mapContainer, {
        center: center,
        zoom: 15,
        mapId: 'VENUE_SELECTOR_MAP',
      });

      // Add marker if coordinates exist
      if (venueLatitude && venueLongitude) {
        marker = new google.maps.marker.AdvancedMarkerElement({
          position: { lat: venueLatitude, lng: venueLongitude },
          map: map,
          gmpDraggable: true,
        });

        marker.addListener('dragend', (event) => {
          venueLatitude = event.latLng.lat();
          venueLongitude = event.latLng.lng();
          reverseGeocode(venueLatitude, venueLongitude);
        });
      }
    } catch (error) {
      console.error('Error initializing map:', error);
      loadError = 'Error initializing map. Please try again.';
    }
  }

  async function handleSearchInput() {
    if (!searchInput || searchInput.length < 3) {
      predictions = [];
      showPredictions = false;
      return;
    }

    try {
      const request = {
        input: searchInput,
        includedPrimaryTypes: ['establishment'],
      };

      const { suggestions } = await google.maps.places.AutocompleteSuggestion.fetchAutocompleteSuggestions(request);

      if (suggestions && suggestions.length > 0) {
        predictions = suggestions;
        showPredictions = true;
      } else {
        predictions = [];
        showPredictions = false;
      }
    } catch (error) {
      console.error('Error fetching autocomplete suggestions:', error);
      predictions = [];
      showPredictions = false;
    }
  }

  async function selectPlace(suggestion) {
    try {
      // Get the place from the suggestion
      const place = suggestion.placePrediction.toPlace();

      // Fetch place details
      await place.fetchFields({
        fields: ['displayName', 'formattedAddress', 'location'],
      });

      // Update venue data
      venueName = place.displayName || suggestion.placePrediction.text?.text || '';
      venueAddress = place.formattedAddress || '';
      venueLatitude = place.location.lat();
      venueLongitude = place.location.lng();

      // Update map
      map.setCenter(place.location);
      map.setZoom(15);

      // Update or create marker
      if (marker) {
        marker.position = place.location;
      } else {
        marker = new google.maps.marker.AdvancedMarkerElement({
          position: place.location,
          map: map,
          gmpDraggable: true,
        });

        marker.addListener('dragend', (event) => {
          venueLatitude = event.latLng.lat();
          venueLongitude = event.latLng.lng();
          reverseGeocode(venueLatitude, venueLongitude);
        });
      }

      // Clear search input and hide predictions
      searchInput = '';
      predictions = [];
      showPredictions = false;
      loadError = '';
    } catch (error) {
      console.error('Error getting place details:', error);
      loadError = 'Failed to get place details. Please try again.';
    }
  }

  function reverseGeocode(lat, lng) {
    const geocoder = new google.maps.Geocoder();
    const latlng = { lat: lat, lng: lng };

    geocoder.geocode({ location: latlng }, (results, status) => {
      if (status === 'OK') {
        if (results[0]) {
          venueAddress = results[0].formatted_address;
        }
      }
    });
  }

  function openModal() {
    modal_open = true;
    // Initialize map when modal opens
    setTimeout(() => {
      initializeMap();
    }, 100);
  }

  function closeModal() {
    modal_open = false;
  }

  function clearVenue() {
    venueName = '';
    venueAddress = '';
    venueLatitude = null;
    venueLongitude = null;
  }
</script>

<div class="space-y-4">
  <div>
    <Label for="venue_name" class="block mb-2">
      {m.form_venueName()}{required ? '*' : ''}
    </Label>
    <Input
      id="venue_name"
      name="venue"
      type="text"
      bind:value={venueName}
      placeholder={m.form_venueNamePlaceholder()}
      required={required}
    />
  </div>

  <div>
    <Label for="venue_address" class="block mb-2">
      {m.form_venueAddress()}
    </Label>
    <div class="flex gap-2">
      <Input
        id="venue_address"
        name="venue_address"
        type="text"
        bind:value={venueAddress}
        placeholder={m.form_venueAddressPlaceholder()}
        class="flex-1"
        readonly
      />
      <Button color="primary" onclick={openModal}>
        <MapPinAltSolid class="w-4 h-4 me-2" />
        {m.form_selectLocation()}
      </Button>
      {#if venueName || venueAddress}
        <Button color="alternative" onclick={clearVenue}>
          {m.common_clear()}
        </Button>
      {/if}
    </div>
  </div>

  {#if venueLatitude && venueLongitude}
    <input type="hidden" name="venue_latitude" value={venueLatitude} />
    <input type="hidden" name="venue_longitude" value={venueLongitude} />
  {/if}

  {#if error}
    <Alert color="red" class="mt-3">
      <p class="text-sm">{error}</p>
    </Alert>
  {/if}
</div>

<Modal title={m.form_selectVenueLocation()} bind:open={modal_open} size="xl" outsideclose>
  <div class="space-y-4">
    {#if loadError}
      <Alert color="red">{loadError}</Alert>
    {/if}

    <div class="relative">
      <Label for="search_address" class="block mb-2">{m.form_searchAddress()}</Label>
      <div class="relative">
        <div class="absolute inset-y-0 start-0 flex items-center ps-3.5 pointer-events-none">
          <MapPinAltSolid class="h-5 w-5 text-gray-500" />
        </div>
        <Input
          id="search_address"
          type="text"
          bind:value={searchInput}
          oninput={handleSearchInput}
          onfocus={() => { if (predictions.length > 0) showPredictions = true; }}
          placeholder={m.form_searchAddressPlaceholder()}
          class="ps-10"
          size="md"
        />
      </div>

      {#if showPredictions && predictions.length > 0}
        <div class="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {#each predictions as suggestion}
            <button
              type="button"
              class="w-full text-left px-4 py-2 hover:bg-gray-100 border-b border-gray-200 last:border-b-0"
              onclick={() => selectPlace(suggestion)}
            >
              <div class="font-medium text-sm">{suggestion.placePrediction.mainText?.text || suggestion.placePrediction.text?.text || ''}</div>
              <div class="text-xs text-gray-600">{suggestion.placePrediction.secondaryText?.text || ''}</div>
            </button>
          {/each}
        </div>
      {/if}

      <p class="text-sm text-gray-500 mt-2">{m.form_searchAddressHint()}</p>
    </div>

    <div bind:this={mapContainer} class="w-full h-96 rounded-lg border border-gray-300"></div>

    <p class="text-sm text-gray-600">
      {m.form_dragMarkerHint()}
    </p>
  </div>

  <svelte:fragment slot="footer">
    <div class="flex justify-end gap-2 w-full">
      <Button color="alternative" onclick={closeModal}>{m.common_cancel()}</Button>
      <Button color="primary" onclick={closeModal}>{m.common_confirm()}</Button>
    </div>
  </svelte:fragment>
</Modal>
