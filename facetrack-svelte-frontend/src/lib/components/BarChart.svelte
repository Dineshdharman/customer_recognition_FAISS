<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import Chart from 'chart.js/auto';

	export let data: { visitor_name: string; visit_count: number }[] | null = null;

	let canvasElement: HTMLCanvasElement;
	let chartInstance: Chart | null = null;

	function createChart() {
		if (!canvasElement || !data) return;

		const labels = data.map((d) => (d.visitor_name || 'Unknown').substring(0, 20));
		const values = data.map((d) => d.visit_count);

		if (chartInstance) {
			chartInstance.data.labels = labels;
			chartInstance.data.datasets[0].data = values;
			chartInstance.update();
		} else {
			const ctx = canvasElement.getContext('2d');
			if (ctx) {
				chartInstance = new Chart(ctx, {
					type: 'bar',
					data: {
						labels: labels,
						datasets: [
							{
								label: 'Visit Count',
								data: values,
								backgroundColor: '#10b981', // Emerald 500
								borderColor: '#059669', // Emerald 600
								borderWidth: 1,
                                borderRadius: 4
							}
						]
					},
					options: {
						responsive: true,
						maintainAspectRatio: false,
						indexAxis: 'y', // Horizontal bar chart
						scales: {
							x: {
								beginAtZero: true,
                                grid: { color: '#e5e7eb' }
							},
                            y: {
                                grid: { display: false }
                            }
						},
                        plugins: {
                            legend: { display: false }
                        }
					}
				});
			}
		}
	}

	onMount(() => {
		createChart();
	});

	onDestroy(() => {
		chartInstance?.destroy();
	});

	$: if (data && canvasElement) {
		createChart();
	}
</script>

<canvas bind:this={canvasElement}></canvas>