<script lang="ts">
	export let title: string;
</script>

<div class="bg-white p-6 rounded-2xl shadow-sm">
	<h3 class="text-lg font-semibold text-gray-800 mb-6 text-center border-b pb-3">{title}</h3>
	<div class="chart-container">
		<slot />
	</div>
</div>