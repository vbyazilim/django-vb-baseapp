## `CustomLocaleMiddleware`

This is mostly used for our custom projects. Injects `LANGUAGE_CODE` variable to
`request` object. `/en/path/to/page/` sets `request.LANGUAGE_CODE` to `en` otherwise `tr`.

```python
# add this to your settings/base.py
MIDDLEWARE += ['baseapp.middlewares.CustomLocaleMiddleware']
```

## `TimezoneMiddleware`

If you have custom user model or you have `timezone` field in your `request.user`,
this middleware activates timezone for user.
