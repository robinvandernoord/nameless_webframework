<script>
    import {python} from "../python";
    import {expose} from "../framework";

    export let n;

    function some_func(data) {
        console.error(...data);
    }

    expose(some_func);

    function lg(it) {
        console.warn(it);
    }

    $python.func("echo").then(lg);

    $python.string().then(lg);
    $python.log("jaoho").then(lg);

    $python.err().then(lg);

</script>


<div>
    {#await $python.list_of_data(n)}
        waiting for server
    {:then data}
        {#each data as number}
            {number}
        {/each}
    {/await}
</div>