import App from './App.svelte';

const app = new App({
	target: document.body,
	props: window.__globals,
});

export default app;

// clean up:
delete window.__globals;
document.querySelectorAll('[selfdestruct]').forEach(el=>el.remove())