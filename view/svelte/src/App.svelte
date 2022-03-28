<script>
    import Server from "./components/Server.svelte";

    export let name;

    let n = 0;
</script>

<style>
    main {
        text-align: center;
        padding: 1em;
        max-width: 240px;
        margin: 0 auto;
    }

    h1 {
        color: #ff3e00;
        text-transform: uppercase;
        font-size: 4em;
        font-weight: 100;
    }

    @media (min-width: 640px) {
        main {
            max-width: none;
        }
    }
</style>

<main>
    <h1>Hello {name}!</h1>
    <p>
        <button on:click={_=>n -= 1}>-</button>
        <span>{n}</span>
        <button on:click={_=>n += 1}>+</button>
    </p>

    <Server {n} />
    <Server n={n + 1} />
    <Server n={n + 2} />
</main>