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

	let selectedLanguage = $state('en');

	function changeLanguage(lang) {
		selectedLanguage = lang;
		// TODO: Implement language change logic
	}
</script>

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
					<span class="text-sm font-medium">{selectedLanguage.toUpperCase()}</span>
				</button>
				<Dropdown placement="bottom-end">
					<DropdownItem on:click={() => changeLanguage('en')}>
						<span class={selectedLanguage === 'en' ? 'font-semibold' : ''}>English</span>
					</DropdownItem>
					<DropdownItem on:click={() => changeLanguage('ko')}>
						<span class={selectedLanguage === 'ko' ? 'font-semibold' : ''}>한국어</span>
					</DropdownItem>
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
					<Dropdown placement="bottom-end">
						<DropdownHeader>
							<span class="block text-sm font-semibold">{data.user.first_name} {data.user.last_name}</span>
							<span class="block truncate text-sm text-gray-500">{data.user.email}</span>
						</DropdownHeader>
						<DropdownItem href="/profile">My Profile</DropdownItem>
						<DropdownDivider />
						<DropdownItem href="/logout" data-sveltekit-reload>Sign Out</DropdownItem>
					</Dropdown>
				</NavLi>
			{:else}
				<!-- Login and Register Buttons -->
				<NavLi class="flex items-center gap-3">
					<Button
						href="/login"
						color="light"
						size="sm"
						class="border-2 border-blue-600 text-blue-600 hover:bg-blue-50 font-medium px-4 py-1.5"
					>
						Login
					</Button>
					<Button
						href="/registration"
						size="sm"
						class="bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-1.5"
					>
						Register
					</Button>
				</NavLi>
			{/if}
		</NavUl>
	</div>
</Navbar>

{@render children()}

<footer class="bg-gray-50 border-t border-gray-200 mt-20">
	<div class="container mx-auto px-4 py-8">
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
					© {new Date().getFullYear()} All rights reserved.
				</p>
				<p class="text-xs text-gray-500 mt-1">
					Powered by <strong>IEUM</strong>
				</p>
			</div>
		</div>
	</div>
</footer>
</div>
