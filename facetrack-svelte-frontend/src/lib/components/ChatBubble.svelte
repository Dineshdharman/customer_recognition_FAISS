<script lang="ts">
	import { BACKEND_URL } from '$lib/config';

	export let type: 'user' | 'bot';
	export let message: string;
	export let plotFilename: string | null = null;

	let plotError = false; // Reactive variable to control error message visibility

	function handlePlotImageError(event: Event) {
		const imgElement = event.currentTarget as HTMLImageElement;
		imgElement.style.display = 'none'; // Hide the broken image
		plotError = true; // Show the error message
	}

	// Reset plotError when plotFilename changes (e.g., for a new message)
	$: if (plotFilename) {
		plotError = false;
	}

	$: bubbleClass =
		type === 'user' ? 'bg-indigo-600 text-white ml-auto' : 'bg-white text-gray-800 mr-auto border';
</script>

<div class="chat-bubble p-4 rounded-xl max-w-lg shadow-sm {bubbleClass}">
	<p class="whitespace-pre-wrap">{@html message.replace(/\n/g, '<br>')}</p>

	{#if plotFilename}
		<div class="mt-3 border-t pt-3">
			<img
				src="{BACKEND_URL}/api/get-plot/{plotFilename}?t={new Date().getTime()}"
				alt="Chatbot Visualization"
				class="rounded-lg max-w-full border p-1 bg-white shadow-sm"
				on:error={handlePlotImageError}
			/>
			{#if plotError}
				<p class="text-xs text-red-500 italic mt-1">Could not load plot image.</p>
			{/if}
		</div>
	{/if}
</div>