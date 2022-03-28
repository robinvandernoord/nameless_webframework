import {writable} from "svelte/store";
import {python as _py} from "./framework";

export const python = writable(_py);
