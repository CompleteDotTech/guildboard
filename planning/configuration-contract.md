# Ready task contract: configuration validation

Stable issue: GB-T0.03.02.T1. This narrow pure-function contract is sufficiently specified to implement independently from the runtime architecture. No configuration code has been implemented by bootstrap.

## Files and API

Create `packages/config` as a private ESM TypeScript workspace package named `@guildboard/config`. Implementation: `src/index.ts`; tests: `test/config.test.ts`; usage/security notes: `README.md`. Target ES2022; use no external validation library or Discord/database network calls. Tests may use Node's built-in test/assert modules against compiled output. Add only the compiler/tooling needed by the focused PR and record its lockfile/license review.

Export `parseConfig(env: Readonly<Record<string, string | undefined>>): ConfigResult` with these types:

```ts
type AppConfig = Readonly<{
  port: number;
  nodeEnv: 'development' | 'test' | 'production';
  databaseUrl: string;
  discordClientId: string;
  sessionSecret: string;
}>;
type ConfigResult =
  | { ok: true; value: AppConfig }
  | { ok: false; error: { code: 'CONFIG_INVALID'; invalidKeys: string[] } };
```

Do not read global `process.env`, log values, bind a listener or perform network IO inside `parseConfig`. Invalid input returns the failure variant without throwing. Aggregate all invalid/missing names, sort them lexicographically and include each name once. Service entry points will later translate failure to nonzero exit before binding; runtime entry-point integration belongs to the service implementation issues.

## Rules

- Every listed key is required; undefined or empty input is invalid. Ignore unrelated variables.
- `PORT`: ASCII decimal digits only, integer in inclusive range 1–65535; reject signs, whitespace, decimal points, exponential notation and overflow. Leading zeroes are accepted as decimal, never octal.
- `NODE_ENV`: exact `development`, `test` or `production`; no implicit default or case folding.
- `DATABASE_URL`: parse as URL; exact `mysql:` protocol, nonempty hostname and a nonempty database path beyond `/`. Preserve original valid string without logging it. Credentials may be supplied in the URL; never include them in diagnostics.
- `DISCORD_CLIENT_ID`: nonempty ASCII decimal digits. Preserve as string to avoid numeric precision loss. Existence/ownership of the Discord application is a separate integration check.
- `SESSION_SECRET`: minimum 32 characters; reject a whitespace-only string. Do not trim or change the supplied valid secret. This structural check is not an entropy guarantee; secure generation and rotation belong to deployment/security work.

## Acceptance evidence

Table-driven tests cover valid input, all missing keys, multiple simultaneous failures, port boundaries (0/1/65535/65536), signs, fractions, exponential forms, huge values, malformed/wrong-scheme URLs, absent host/database, unsafe numeric conversion of Discord IDs, enum mismatches and short/blank secrets. Assert failure values contain only `CONFIG_INVALID` and sorted variable names; captured logs must not contain a sentinel URL password or secret. Assert parser does not mutate input and ignores unrelated keys. Usage docs must warn against logging the successful value because it contains credentials.

The two native subtasks isolate secret-safe diagnostics and numeric/URL parsing. Remaining enum/ID/secret checks are small checklist steps within the parent implementation task. The sibling verification issue retains independent acceptance responsibility.
