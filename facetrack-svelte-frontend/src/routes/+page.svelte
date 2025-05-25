<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import KpiCard from '$lib/components/KpiCard.svelte';
	import ChartCard from '$lib/components/ChartCard.svelte';
	import LineChart from '$lib/components/LineChart.svelte';
	import BarChart from '$lib/components/BarChart.svelte';
	import { fetchDashboardStats, fetchVisitTrend, fetchTopVisitors } from '$lib/api';
	import { recognitionStatus, lastRecognition } from '$lib/stores/socket';
	import type { RecognitionStatus } from '$lib/stores/socket';

	let stats: any = { totalCustomers: 0, newToday: 0, totalVisitsToday: 0 };
	let trendData: any = null;
	let topData: any = null;
    let currentRecStatus: RecognitionStatus = { running: false, scheduled: false }; // Initialize

    const unsubscribeRec = recognitionStatus.subscribe(value => {
        currentRecStatus = value;
    });

    const unsubscribeLastRec = lastRecognition.subscribe(value => {
        if (value) {
           loadData(); // Re-fetch data
        }
    });

	async function loadData() {
		stats = (await fetchDashboardStats()) || stats;
		trendData = await fetchVisitTrend(); // This will update the trendData variable
		topData = await fetchTopVisitors();   // This will update the topData variable
	}

	onMount(() => {
		loadData();
        const intervalId = setInterval(loadData, 30000);
        return () => {
             clearInterval(intervalId);
             unsubscribeRec();
             unsubscribeLastRec();
        }
	});

    $: recValue = currentRecStatus?.running ? 'ON' : 'OFF';
    $: recColor = currentRecStatus?.running ? 'text-green-600' : 'text-red-600';
    $: recIcon = currentRecStatus?.running ? 'fa-video' : 'fa-video-slash';
</script>

<svelte:head>
	<title>Dashboard - FaceTrack CMS</title>
</svelte:head>

<h1 class="text-3xl font-semibold text-gray-800 mb-8">Dashboard Overview</h1>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
	<KpiCard title="Total Customers" value={stats.totalCustomers} icon="fa-users" />
	<KpiCard title="New Today" value={stats.newToday} icon="fa-user-plus" />
	<KpiCard title="Visits Today" value={stats.totalVisitsToday} icon="fa-street-view" />
	<KpiCard title="Recognition" value={recValue} icon={recIcon} valueColor={recColor} />
</div>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-10">
	<ChartCard title="Visit Trend (Last 7 Days)">
		{#if trendData}
			<LineChart data={trendData} />
		{:else}
			<div class="flex justify-center items-center h-full text-gray-400">Loading Trend Data...</div>
		{/if}
	</ChartCard>
	<ChartCard title="Top 5 Visitors">
		{#if topData}
			<BarChart data={topData} />
		{:else}
			<div class="flex justify-center items-center h-full text-gray-400">Loading Visitor Data...</div>
		{/if}
	</ChartCard>
</div>