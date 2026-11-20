/**
 * Loads the types of `bun:test` into the site type check. TypeScript 7 loads no `@types` package by default.
 * The preload and each test file that `bun test` runs import from `bun:test`.
 */
/// <reference types="bun" />
