<script lang="ts">
	import { notifications, hideNotification } from '$lib/stores/notifications';
	import { fly } from 'svelte/transition';
    import type { Notification } from '$lib/stores/notifications';

	$: notificationList = $notifications;

	const colorClasses: Record<Notification['type'], string> = {
		info: 'bg-blue-500',
		success: 'bg-green-500',
		error: 'bg-red-600',
        warning: 'bg-yellow-500',
	};

    const iconClasses: Record<Notification['type'], string> = {
		info: 'fa-circle-info',
		success: 'fa-check-circle',
		error: 'fa-exclamation-triangle',
        warning: 'fa-exclamation-circle',
	};
</script>

<div class="fixed bottom-5 right-5 z-50 space-y-3 w-80">
	{#each notificationList as notification (notification.id)}
		<div
			in:fly={{ x: 300, duration: 300 }}
			out:fly={{ x: 300, duration: 300 }}
			class="p-4 rounded-lg shadow-xl text-white flex items-center {colorClasses[notification.type]}"
            role="alert"
		>
            <i class="fas {iconClasses[notification.type]} mr-3 text-xl"></i>
			<span class="flex-1">{notification.message}</span>
            <button class="ml-2 text-white opacity-70 hover:opacity-100" on:click={() => hideNotification(notification.id)}>
                <i class="fas fa-times"></i>
            </button>
		</div>
	{/each}
</div>