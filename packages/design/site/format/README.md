# packages/design/site/format: the pure number and name formats

## Knows

- The number, gap, record, ordinal, and count formats. They follow the Jinja filters of the pipeline.
- The short form of a name.

## Ports

None.

## Does not do

- It reads no file, no storage, and no env. Each function takes values and returns values.
- It holds no helper over the type of a published file. Each package holds its own.
