import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
	preprocess: [
		vitePreprocess(),
	],
	extensions: ['.svelte', '.svx'],
	kit: {
		adapter: adapter()
	}
};
