# Eval: YARRRML Review

Use `$graph-sync-yarrrml-review`.

Review the following YARRRML mapping for `morganstanley.com` articles:

```yaml
prefixes:
  schema: "https://schema.org/"
  ms: "https://www.morganstanley.com/"

mappings:
  articles:
    sources:
      - [data.json~jsonpath, "$[*]"]
    s: ms:ideas/$(slug)
    po:
      - [a, schema:Article]
      - [schema:name, $(title)]
      - [schema:datePublished, $(publishDate)]
      - [schema:url, $(url)]
      - [schema:author, $(author.name)]
      - [schema:description, $(summary)]
      - p: schema:image
        o:
          - mapping: articleImage
  articleImage:
    sources:
      - [data.json~jsonpath, "$[*]"]
    s: ms:ideas/$(slug)/image
    po:
      - [a, schema:ImageObject]
      - [schema:url, $(image.src)]
      - [schema:width, $(image.width)]
      - [schema:height, $(image.height)]
```

Requirements:

- Check selector robustness.
- Confirm relative XPath use.
- Check route/fallback compatibility.
- Look for duplicate mappings.
- Check that emitted schema.org output uses explicit IRIs and URL literals.
- Identify brittle assumptions based on sample pages.

Expected output:

- Findings ordered by severity.
- File/line references where possible.
- Suggested fixes.
- Residual risks.
