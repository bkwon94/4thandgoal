# The pipeline owns the published shape

The site reads the pipeline's JSON files. The pydantic models here are the one owner of each published
shape. The site writes a Zod schema per file by hand as the consumer's contract. No generated schema
crosses between the repos. We rejected a generator because it is a third artifact to keep current.
The site's test over its `public/` files already finds a changed shape.
