/**
 * The Playwright reporter that picks the tests of a sharded run, in place of the built-in split of Playwright.
 * The shard keeps each Nth test of the run, so the tests of one slow file spread over the shards of CI.
 */

/* The tests of `shard`, out of `tests` in the order of the run. A unit is one test, or one whole file of a project in
   `wholeFileProjects`, whose tests must run in one place and in order. The shard keeps each Nth unit, so every test lands in
   exactly one shard, and the tests of one slow file spread over the shards. The built-in split gives each shard one block of
   tests in a row, so the slow first file of a run, such as evidence-rules.spec.ts or analyzer-stage.spec.ts, landed in shard 1
   alone. `projectOf` and `fileOf` read the project name and the file of a test. */
export function inShard(tests, shard, { wholeFileProjects = [], projectOf, fileOf } = {}) {
  const rankOfUnit = new Map();
  return tests.filter((test) => {
    const unit = wholeFileProjects.includes(projectOf?.(test))
      ? `${projectOf(test)}\n${fileOf(test)}`
      : test;
    if (!rankOfUnit.has(unit)) rankOfUnit.set(unit, rankOfUnit.size);
    return rankOfUnit.get(unit) % shard.total === shard.current - 1;
  });
}

/* Splits the tests of a run with a shard, such as one that PLAYWRIGHT_SHARD sets. A run with no shard keeps every test.
   It prints nothing. The option wholeFileProjects names the projects that are not fully parallel. The config does not
   import this file, because Playwright loads a module of the config as CommonJS and then cannot load it again as a reporter. */
export default class RoundRobinShard {
  constructor({ wholeFileProjects = [] } = {}) {
    this.wholeFileProjects = wholeFileProjects;
  }

  async preprocess({ config, suite, testRun }) {
    if (!config.shard) return;
    testRun.skipSharding();
    const tests = suite.allTests();
    const kept = new Set(
      inShard(tests, config.shard, {
        wholeFileProjects: this.wholeFileProjects,
        projectOf: (test) => test.parent.project()?.name,
        fileOf: (test) => test.location.file,
      }),
    );
    for (const test of tests) {
      if (!kept.has(test)) testRun.exclude(test);
    }
  }

  printsToStdio() {
    return false;
  }
}
