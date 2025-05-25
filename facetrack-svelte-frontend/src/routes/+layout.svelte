<script lang="ts">
	import '../app.css';
	import '@fortawesome/fontawesome-free/css/all.min.css'; // Import Font Awesome
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Header from '$lib/components/Header.svelte';
	import Notifications from '$lib/components/Notifications.svelte';
	import { initializeSocket } from '$lib/stores/socket';
	import { onMount } from 'svelte';

	// Initialize socket connection once when layout mounts
	onMount(() => {
		initializeSocket();
	});
</script>

<div class="flex h-screen bg-gray-100">
	<Sidebar />
	<div class="flex-1 flex flex-col overflow-hidden">
		<Header />
		<main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6 md:p-10">
			<slot />
		</main>
	</div>
</div>
<Notifications />