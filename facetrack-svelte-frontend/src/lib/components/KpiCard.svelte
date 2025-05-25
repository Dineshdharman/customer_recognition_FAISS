<script lang="ts">
	export let title: string;
	export let value: string | number;
	export let icon: string;
	export let valueColor: string = 'text-gray-900';
</script>

<div
	class="bg-white p-6 rounded-2xl shadow-sm flex items-center transition-all duration-300 hover:shadow-lg hover:scale-[1.02]"
>
	<div class="p-4 rounded-full bg-indigo-100">
		<i class="fas {icon} text-3xl text-indigo-600"></i>
	</div>
	<div class="ml-5">
		<h3 class="text-gray-500 font-medium text-sm uppercase tracking-wider">{title}</h3>
		<p class="text-3xl font-bold {valueColor}">{value}</p>
	</div>
</div>