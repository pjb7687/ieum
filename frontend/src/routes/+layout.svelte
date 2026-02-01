<script>
	import "../app.css";
	let { children, data } = $props();
	import {
		Navbar,
		NavBrand,
		Avatar,
		Dropdown,
		DropdownHeader,
		DropdownItem,
		DropdownDivider,
		Button,
		Spinner,
	} from "flowbite-svelte";
	import { GlobeOutline } from "flowbite-svelte-icons";
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { page } from '$app/stores';
	import { languageTag, setLanguageTag, onSetLanguageTag } from '$lib/paraglide/runtime.js';
	import * as m from '$lib/paraglide/messages.js';

	const languages = [
		{ code: 'en', name: 'English' },
		{ code: 'ko', name: '한국어' }
	];

	let currentLanguage = $state(languageTag());
	let profileDropdownOpen = $state(false);
	let languageDropdownOpen = $state(false);
	let isLoading = $state(true);

	onMount(() => {
		// Set up callback to update state when language changes
		onSetLanguageTag((newTag) => {
			currentLanguage = newTag;
		});

		const savedLocale = localStorage.getItem('preferred-locale');

		if (!savedLocale) {
			const browserLanguage = navigator.language.toLowerCase();
			const supportedLanguages = ['en', 'ko'];

			let detectedLanguage = supportedLanguages.find(lang =>
				browserLanguage === lang || browserLanguage.startsWith(lang + '-')
			);

			if (!detectedLanguage) {
				detectedLanguage = 'en';
			}

			setLanguageTag(detectedLanguage);
			localStorage.setItem('preferred-locale', detectedLanguage);
		} else {
			setLanguageTag(savedLocale);
		}

		// Update current language state after setting
		currentLanguage = languageTag();

		// Mark loading as complete
		isLoading = false;
	});

	function switchLanguage(newLocale) {
		setLanguageTag(newLocale);
		localStorage.setItem('preferred-locale', newLocale);
		document.documentElement.lang = newLocale;
	}

	// Compute the next parameter for login/registration
	// If user is on email verification page, redirect to root after login
	let nextPath = $derived(
		$page.url.pathname.includes('/verify-email') ? '/' : $page.url.pathname
	);
</script>

{#if isLoading}
	<div class="fixed inset-0 bg-white flex items-center justify-center z-50">
		<Spinner size="12" />
	</div>
{:else}
	{#key currentLanguage}
	<div class="min-h-screen bg-slate-50">
<Navbar class="border-b border-gray-200 bg-white py-2">
	<div class="container mx-auto flex items-center justify-between px-4">
		<!-- Logo -->
		<NavBrand href="/" class="flex items-center">
			<img src="/logo.webp" class="h-10 sm:h-12" alt="Logo" />
		</NavBrand>

		<!-- Right side: Language selector and Auth buttons -->
		<div class="flex flex-row items-center gap-3">
			<!-- Language Selector -->
			<Button color="none" size="sm" class="flex items-center gap-1 hover:bg-gray-100">
				<GlobeOutline class="w-5 h-5" />
				<span class="text-sm font-medium">{currentLanguage.toUpperCase()}</span>
			</Button>
			<Dropdown simple bind:open={languageDropdownOpen}>
				{#each languages as lang}
					<DropdownItem onclick={() => { switchLanguage(lang.code); languageDropdownOpen = false; }}>
						{lang.name}
					</DropdownItem>
				{/each}
			</Dropdown>

			{#if data.user}
				<!-- User Profile Dropdown -->
				<Avatar size="sm" class="cursor-pointer">
					{data.user.first_name.charAt(0)}{data.user.last_name.charAt(0)}
				</Avatar>
				<Dropdown simple placement="bottom-end" bind:open={profileDropdownOpen}>
					<DropdownHeader>
						<span class="block text-sm font-semibold">{data.user.first_name} {data.user.last_name}</span>
						<span class="block truncate text-sm text-gray-500">{data.user.email}</span>
					</DropdownHeader>
					<DropdownItem href="/profile" onclick={() => profileDropdownOpen = false}>{m.nav_myProfile()}</DropdownItem>
					<DropdownItem href="/payment-history" onclick={() => profileDropdownOpen = false}>{m.nav_paymentHistory()}</DropdownItem>
					{#if data.user.is_staff}
						<DropdownDivider />
						<DropdownItem href="/{data.admin_page_name}" onclick={() => profileDropdownOpen = false}>{m.nav_adminPage()}</DropdownItem>
					{/if}
					<DropdownDivider />
					<DropdownItem href="/logout" data-sveltekit-reload onclick={() => profileDropdownOpen = false}>{m.nav_signOut()}</DropdownItem>
				</Dropdown>
			{:else}
				<!-- Login Button -->
				<Button
					href="/login?next={encodeURIComponent(nextPath)}"
					color="primary"
					size="sm"
				>
					{m.nav_login()}
				</Button>
			{/if}
		</div>
	</div>
</Navbar>

{@render children()}

<footer class="bg-gray-50 border-t border-gray-200 mt-20">
	<div class="container mx-auto py-8 px-3 sm:px-7">
		<div class="flex flex-col md:flex-row justify-between items-center gap-6">
			<!-- Logo Section -->
			<div class="flex items-center">
				<a href="/">
					<img src="/logo.webp" class="h-12" alt="Logo" />
				</a>
			</div>

			<!-- Copyright and Credits -->
			<div class="text-center md:text-right">
				<p class="text-sm text-gray-600">
					© {new Date().getFullYear()} {m.footer_copyright()}
				</p>
				<p class="text-xs text-gray-500 mt-1">
					Powered by <a href="https://github.com/pjb7687/ieum" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:underline">IEUM</a>
				</p>
			</div>
		</div>
		</div>
	</footer>
	</div>
	{/key}
{/if}
