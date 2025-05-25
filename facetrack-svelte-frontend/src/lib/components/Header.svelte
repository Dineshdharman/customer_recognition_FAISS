<script lang="ts">
    import { page } from '$app/stores';

    $: title = $page.url.pathname === '/' ? 'Dashboard'
             : $page.url.pathname === '/chat' ? 'Chatbot Assistant'
             : $page.url.pathname === '/settings' ? 'Settings'
             : 'FaceTrack CMS';
</script>

<header class="flex justify-between items-center p-6 bg-white border-b shadow-sm h-20">
    <h2 class="text-2xl font-semibold text-gray-800">{title}</h2>
    <div class="flex items-center space-x-4">
       <button class="text-gray-500 hover:text-indigo-600">
            <i class="fas fa-bell text-xl"></i>
        </button>
        <button class="text-gray-500 hover:text-indigo-600">
             <i class="fas fa-user-circle text-2xl"></i>
        </button>
    </div>
</header>