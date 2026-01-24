import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { paraglide } from '@inlang/paraglide-js-adapter-sveltekit/vite';

const ALLOWED_HOST = process.env.ALLOWED_HOST || 'localhost'

export default defineConfig({
	server: {
		allowedHosts: [ALLOWED_HOST, ],
	},
	plugins: [
		paraglide({
			project: './project.inlang',
			outdir: './src/lib/paraglide'
		}),
		sveltekit()
	]
});
