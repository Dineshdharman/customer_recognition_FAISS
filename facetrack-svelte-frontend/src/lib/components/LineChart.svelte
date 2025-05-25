<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import Chart from 'chart.js/auto';
	import { format, isValid } from 'date-fns';

	export let data: { visit_date: string | null; visit_count: number }[] | null = null;

	let canvasElement: HTMLCanvasElement;
	let chartInstance: Chart | null = null;

	function createChart() {
		if (!canvasElement || !data) {
            console.warn("LineChart: No canvas element or data provided.");
            return;
        }

        console.log("LineChart: Raw data received:", JSON.parse(JSON.stringify(data)));

		const processedData: { label: string; value: number }[] = [];

		for (const d of data) {
			if (d.visit_date && String(d.visit_date).trim() !== "") {
				// Directly use the visit_date string if it's already well-formatted
				const dateObj = new Date(String(d.visit_date));

                // console.log(`LineChart: Processing visit_date: '${d.visit_date}', Date Object: ${dateObj}`);

				if (isValid(dateObj)) {
					processedData.push({
						label: format(dateObj, 'MMM d'), // Format it to 'May 24'
						value: d.visit_count
					});
				} else {
					console.warn(`LineChart: Invalid date constructed for visit_date: '${d.visit_date}'. Skipping.`);
				}
			} else {
				console.warn(`LineChart: Null, undefined, or empty visit_date found. Skipping entry:`, d);
			}
		}

        if (!processedData.length) {
            if (chartInstance) {
                chartInstance.data.labels = [];
                chartInstance.data.datasets[0].data = [];
                chartInstance.update();
            }
            console.warn("LineChart: No valid data to plot after filtering and validation.");
            return;
        }

		const labels = processedData.map(item => item.label);
		const values = processedData.map(item => item.value);

		if (chartInstance) {
			chartInstance.data.labels = labels;
			chartInstance.data.datasets[0].data = values;
			chartInstance.update();
		} else {
			const ctx = canvasElement.getContext('2d');
			if (ctx) {
				chartInstance = new Chart(ctx, {
					type: 'line',
					data: {
						labels: labels,
						datasets: [
							{
								label: 'Visits',
								data: values,
								borderColor: '#4f46e5',
								backgroundColor: 'rgba(79, 70, 229, 0.1)',
								fill: true,
								tension: 0.3,
								pointBackgroundColor: '#4f46e5',
								pointBorderColor: '#fff',
								pointHoverRadius: 7
							}
						]
					},
					options: {
						responsive: true,
						maintainAspectRatio: false,
						scales: {
							y: {
								beginAtZero: true,
                                grid: { color: '#e5e7eb' }
							},
                            x: {
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
		console.log("LineChart: Data prop changed, re-creating chart.");
		createChart();
	}
</script>

<canvas bind:this={canvasElement}></canvas>