<script>
	import "../app.css";
	let { children, data } = $props();
	import {
		Navbar,
		NavBrand,
		NavLi,
		NavUl,
		NavHamburger,
		Avatar,
		Dropdown,
		DropdownHeader,
		DropdownItem,
		DropdownDivider,
		Button,
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
	});

	function switchLanguage(newLocale) {
		setLanguageTag(newLocale);
		localStorage.setItem('preferred-locale', newLocale);
		document.documentElement.lang = newLocale;
	}

	// Compute the next parameter for login/registration
	// If user is on email verification page, redirect to events page after login
	let nextPath = $derived(
		$page.url.pathname.includes('/verify-email') ? '/events' : $page.url.pathname
	);
</script>

{#key currentLanguage}
<div class="min-h-screen bg-slate-50">
<Navbar class="border-b border-gray-200 bg-white py-2">
	<div class="container mx-auto flex flex-wrap items-center justify-between px-4">
		<!-- Logo -->
		<NavBrand href="/" class="flex items-center">
			<img src="/logo.webp" class="h-10 sm:h-12" alt="Logo" />
		</NavBrand>

		<!-- Mobile menu button -->
		<NavHamburger class="md:hidden" />

		<!-- Right side: Language selector and Auth buttons -->
		<NavUl class="md:flex md:items-center md:gap-3">
			<!-- Language Selector -->
			<NavLi class="relative">
				<button class="flex items-center gap-1 text-gray-700 hover:text-gray-900 px-2 py-1.5">
					<GlobeOutline class="w-5 h-5" />
					<span class="text-sm font-medium">{currentLanguage.toUpperCase()}</span>
				</button>
				<Dropdown>
					{#each languages as lang}
						<DropdownItem onclick={() => switchLanguage(lang.code)}>
							<span class="flex items-center gap-2">
								{lang.name}
							</span>
						</DropdownItem>
					{/each}
				</Dropdown>
			</NavLi>

			{#if data.user}
				<!-- User Profile Dropdown -->
				<NavLi class="relative">
					<button class="flex items-center gap-2">
						<Avatar size="sm" class="cursor-pointer">
							{data.user.first_name.charAt(0)}{data.user.last_name.charAt(0)}
						</Avatar>
						<span class="text-gray-700 font-medium hidden md:block text-sm">
							{data.user.first_name}
						</span>
					</button>
					<Dropdown placement="bottom-end" bind:open={profileDropdownOpen}>
						<DropdownHeader>
							<span class="block text-sm font-semibold">{data.user.first_name} {data.user.last_name}</span>
							<span class="block truncate text-sm text-gray-500">{data.user.email}</span>
						</DropdownHeader>
						<DropdownItem href="/profile" onclick={() => profileDropdownOpen = false}>{m.nav_myProfile()}</DropdownItem>
						{#if data.user.is_staff}
							<DropdownDivider />
							<DropdownItem href="/{data.admin_page_name}" onclick={() => profileDropdownOpen = false}>{m.nav_adminPage()}</DropdownItem>
						{/if}
						<DropdownDivider />
						<DropdownItem href="/logout" data-sveltekit-reload onclick={() => profileDropdownOpen = false}>{m.nav_signOut()}</DropdownItem>
					</Dropdown>
				</NavLi>
			{:else}
				<!-- Login and Register Buttons -->
				<NavLi class="flex items-center gap-3">
					<Button
						href="/login?next={encodeURIComponent(nextPath)}"
						color="light"
						size="sm"
						class="border-2 border-blue-600 text-blue-600 hover:bg-blue-50 font-medium px-4 py-1.5"
					>
						{m.nav_login()}
					</Button>
					<Button
						href="/registration?next={encodeURIComponent(nextPath)}"
						size="sm"
						class="bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-1.5"
					>
						{m.nav_register()}
					</Button>
				</NavLi>
			{/if}
		</NavUl>
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
					{m.footer_poweredBy()}
				</p>
			</div>
		</div>
	</div>
</footer>
</div>
{/key}
