<script lang="ts">
	import { page } from '$app/stores';
	import '@fortawesome/fontawesome-free/css/all.min.css';

	const links = [
		{ href: '/', label: 'Dashboard', icon: 'fa-tachometer-alt' },
		{ href: '/chat', label: 'Chatbot', icon: 'fa-robot' },
		{ href: '/settings', label: 'Settings', icon: 'fa-cog' }
	];
</script>

<aside class="w-64 bg-white shadow-xl hidden md:flex flex-col flex-shrink-0">
	<div class="p-6 h-20 flex items-center border-b">
		<a href="/" class="text-2xl font-bold text-indigo-600 flex items-center">
			<i class="fas fa-camera-retro mr-3 text-3xl"></i>
			<span>FaceTrack CMS</span>
		</a>
	</div>
	<nav class="mt-6 flex-1 px-3 space-y-2">
		{#each links as link (link.href)}
			<a
				href={link.href}
				class="flex items-center px-4 py-3 text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 border-l-4 rounded-r-md transition-colors duration-150"
				class:active={$page.url.pathname === link.href}
			>
				<i class="fas {link.icon} w-6 text-center text-lg"></i>
				<span class="ml-4 text-base font-medium">{link.label}</span>
			</a>
		{/each}
	</nav>
	<div class="p-6 border-t text-xs text-gray-400 text-center">
		&copy; 2025 AI FaceTrack.
	</div>
</aside>

<style>
	.active {
		@apply bg-indigo-100 text-indigo-700 font-semibold border-indigo-600;
	}
	.active i {
		@apply text-indigo-600;
	}
	:not(.active) {
		@apply border-transparent;
	}
</style>