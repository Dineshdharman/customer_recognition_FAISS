<script lang="ts">
	import { recognitionStatus } from '$lib/stores/socket';
	import { startRecognition, stopRecognition, generateReport } from '$lib/api';
	import { showNotification } from '$lib/stores/notifications';
	import flatpickr from 'flatpickr';
	import { onMount } from 'svelte';

	let startTime = '09:00';
	let endTime = '17:00';
	let reportRangeEl: HTMLInputElement;
	let fpInstance: flatpickr.Instance | null = null;
    let isSubmittingReport = false;

	function handleStartContinuous() {
		startRecognition().then((res) => {
			if (res) showNotification(res.message, res.status === 'success' ? 'success' : 'error');
		});
	}

	function handleStartScheduled() {
		startRecognition(startTime, endTime).then((res) => {
			if (res) showNotification(res.message, res.status === 'success' ? 'success' : 'error');
		});
	}

	function handleStop() {
		stopRecognition().then((res) => {
			if (res) showNotification(res.message, res.status === 'success' ? 'success' : 'error');
		});
	}

	async function handleGenerateReport() {
        if (!fpInstance || fpInstance.selectedDates.length < 2) {
            showNotification('Please select a start and end date.', 'warning');
            return;
        }
        isSubmittingReport = true;
        const formatDate = (date: Date) => date.toISOString().split('T')[0];
        const start_date = formatDate(fpInstance.selectedDates[0]);
        const end_date = formatDate(fpInstance.selectedDates[1]);

        const res = await generateReport(start_date, end_date);
        if (res) showNotification(res.message, res.status === 'success' ? 'success' : 'error');
        isSubmittingReport = false;
    }

	onMount(() => {
		fpInstance = flatpickr(reportRangeEl, {
			mode: 'range',
			dateFormat: 'Y-m-d',
            altInput: true, // User-friendly format
            altFormat: "F j, Y",
		});
	});

    $: statusText = $recognitionStatus.running ? ($recognitionStatus.scheduled ? 'SCHEDULED' : 'RUNNING') : 'STOPPED';
    $: statusColor = $recognitionStatus.running ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
</script>

<svelte:head>
	<title>Settings - FaceTrack CMS</title>
</svelte:head>

<h1 class="text-3xl font-semibold text-gray-800 mb-8">System Settings</h1>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-10">

	<div class="bg-white p-8 rounded-2xl shadow-sm">
		<h3 class="text-xl font-semibold text-gray-800 mb-6 border-b pb-3">Recognition Control</h3>
		<div class="mb-8 flex items-center">
			<p class="text-gray-600 text-lg">Current Status:</p>
			<span class="font-bold ml-3 px-4 py-1 rounded-full text-lg {statusColor}">
				{statusText}
			</span>
		</div>
		<div class="space-y-6">
			<button
                on:click={handleStartContinuous}
                disabled={$recognitionStatus.running}
				class="w-full bg-green-500 text-white px-4 py-3 rounded-lg hover:bg-green-600 shadow-sm transition duration-200 flex items-center justify-center text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
				<i class="fas fa-play mr-3"></i>Start Continuous
			</button>

			<div class="border p-6 rounded-lg bg-gray-50">
				<h4 class="font-medium mb-5 text-gray-700 text-lg">Scheduled Recognition</h4>
				<div class="flex items-center mb-4">
					<label for="start-time" class="w-24 text-gray-600">Start Time:</label>
					<input type="time" id="start-time" bind:value={startTime} class="border border-gray-300 rounded p-2 text-sm flex-1" />
				</div>
				<div class="flex items-center mb-5">
					<label for="end-time" class="w-24 text-gray-600">End Time:</label>
					<input type="time" id="end-time" bind:value={endTime} class="border border-gray-300 rounded p-2 text-sm flex-1" />
				</div>
				<button
                    on:click={handleStartScheduled}
                    disabled={$recognitionStatus.running}
					class="w-full bg-blue-500 text-white px-4 py-3 rounded-lg hover:bg-blue-600 shadow-sm transition duration-200 flex items-center justify-center text-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
					<i class="fas fa-clock mr-3"></i>Start Scheduled
				</button>
			</div>
			<button
                on:click={handleStop}
                disabled={!$recognitionStatus.running}
				class="w-full bg-red-500 text-white px-4 py-3 rounded-lg hover:bg-red-600 shadow-sm transition duration-200 flex items-center justify-center text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
				<i class="fas fa-stop mr-3"></i>Stop All
			</button>
		</div>
	</div>

	<div class="bg-white p-8 rounded-2xl shadow-sm">
		<h3 class="text-xl font-semibold text-gray-800 mb-6 border-b pb-3">Report Generation</h3>
		<p class="text-gray-600 mb-8">
			Generate a CSV visit report for a specific period and send it via email to the configured
			admin address.
		</p>
		<div class="space-y-6">
			<div>
				<label for="report-range" class="block mb-2 text-gray-700 font-medium text-lg">Select Date Range:</label>
				<input
                    bind:this={reportRangeEl}
					type="text"
					id="report-range"
					class="w-full border border-gray-300 rounded-lg p-3"
					placeholder="Click to select dates..."
				/>
			</div>
			<button
                on:click={handleGenerateReport}
                disabled={isSubmittingReport}
				class="w-full bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 shadow-sm transition duration-200 flex items-center justify-center text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {#if isSubmittingReport}
                    <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-3"></div>
                    <span>Sending...</span>
                {:else}
				    <i class="fas fa-paper-plane mr-3"></i>Generate & Email Report
                {/if}
			</button>
		</div>
	</div>
</div>