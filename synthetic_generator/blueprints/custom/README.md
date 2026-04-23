# Custom Blueprints

Place custom curated batch blueprints in this directory and run them with:

```powershell
py -m synthetic_generator.generate --mode blueprint --blueprint synthetic_generator/blueprints/custom/my_showcase.yaml --output-dir data --seed 42 --validate
```

Blueprint files should follow the same macro-level structure as the built-in showcase blueprints:

- `metadata`
- `generation`
- `scenario_controls`
- `lifecycle_controls`
- optional `outcome_controls`
- optional `realism_controls`
- optional `validation`
