<script lang="ts">
	import ChatBubble from '$lib/components/ChatBubble.svelte';
	import { postChatMessage } from '$lib/api';
	import { onMount, tick } from 'svelte';

	interface Message {
		type: 'user' | 'bot';
		text: string;
		plot?: string | null;
	}

	let messages: Message[] = [
		{ type: 'bot', text: "Hello! I'm FaceTrack AI. How can I help you with your customer data today?" }
	];
	let inputMessage = '';
	let isLoading = false;
    let chatWindow: HTMLElement;

    async function autoScroll() {
        await tick(); // Wait for DOM to update
        if (chatWindow) {
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    }

	async function sendMessage() {
		const question = inputMessage.trim();
		if (!question || isLoading) return;

		isLoading = true;
		messages = [...messages, { type: 'user', text: question }];
        inputMessage = '';
        await autoScroll();

		const response = await postChatMessage(question);
		isLoading = false;

		if (response) {
			messages = [
				...messages,
				{ type: 'bot', text: response.summary, plot: response.plotFilename }
			];
		} else {
			messages = [...messages, { type: 'bot', text: 'Sorry, I had trouble getting a response.' }];
		}
        await autoScroll();
	}

    function handleKeydown(event: KeyboardEvent) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    }

</script>

<svelte:head>
	<title>Chatbot - FaceTrack CMS</title>
</svelte:head>

<div class="h-full flex flex-col bg-white rounded-2xl shadow-sm overflow-hidden">
    <div bind:this={chatWindow} class="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
        {#each messages as msg (msg)}
            <ChatBubble type={msg.type} message={msg.text} plotFilename={msg.plot ?? null} />
        {/each}
        {#if isLoading}
             <div class="flex items-center text-gray-500 p-3">
                <div class="w-5 h-5 border-2 border-gray-300 border-t-indigo-600 rounded-full animate-spin mr-3"></div>
                <span>FaceTrack AI is thinking...</span>
            </div>
        {/if}
	</div>

    <div class="p-6 border-t bg-white">
		<div class="flex items-center border border-gray-300 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-indigo-500">
			<textarea
                bind:value={inputMessage}
                on:keydown={handleKeydown}
				class="flex-1 p-3 border-none focus:outline-none resize-none"
				placeholder="Ask about customers, visits, or request a plot..."
                rows="1"
                disabled={isLoading}
			></textarea>
			<button
                on:click={sendMessage}
                disabled={isLoading || !inputMessage.trim()}
				class="bg-indigo-600 text-white px-6 py-3 hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition duration-200"
			>
                <i class="fas fa-paper-plane"></i>
			</button>
		</div>
	</div>
</div>