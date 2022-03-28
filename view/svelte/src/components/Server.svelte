<script>

    import {python} from "../python";
    import {expose} from "../framework";

    function some_func(data) {
        console.error(...data);
    }

    expose(some_func);

    function lg(it) {
        console.warn(it);
    }

    $python.func("echo").then(lg);

</script>


<div>
    {#await $python.list_of_data()}
        waiting for server
    {:then data}
        {#each data as number}
            {number}
        {/each}
    {/await}
</div>