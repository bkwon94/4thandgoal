# The published shape has one owner

Every file under `public/` comes from the pipeline repo, where pydantic models own its shape. This
site writes one Zod schema per file by hand and infers its types from it. A test parses every file in
`public/` with its schema. A shape change then fails the site test and not just the version check.
We rejected a generated schema from the pipeline. The test over the real files is the contract, and
a generated schema is a third thing to keep the same.
